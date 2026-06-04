import asyncio
import logging
import os
import sounddevice as sd
from typing import Any

from providers import Message
from memory.memory_manager import load_memory, format_memory_for_prompt
from memory.config_manager import load_config, get_model
from tools.declarations import TOOL_DECLARATIONS
from tools import TOOL_IMPLEMENTATIONS
from engine.events import engine_stop
from engine.audio import (
    find_fallback_device, 
    _clean_text_for_tts, 
    _synthesize_speech_in_memory, 
    _play_wav_file,
    _save_pcm_to_wav,
    _transcribe_audio
)
from engine.live import _load_system_prompt

logger = logging.getLogger(__name__)

class JarvisChat:
    """Text-based chat using any provider (Ollama, OpenRouter, Gemini text) with synchronized voice wrapper support."""

    def __init__(self, ui: Any, provider: Any):
        self.ui = ui
        self.provider = provider
        self._history: list[Message] = []
        self._loop = None
        self.ui.on_text_command = self._on_text_command
        self.cfg = load_config()
        self.voice_enabled = self.cfg.get("voice_wrapper_enabled", False)
        self._is_playing_tts = False

    def _on_text_command(self, text: str):
        if not self._loop or engine_stop.is_set():
            return
        asyncio.run_coroutine_threadsafe(self._process_message(text), self._loop)

    async def _process_message(self, text: str, from_voice: bool = False) -> str | None:
        """Process a user message through the chat provider."""
        cfg = load_config()
        selected_prov = cfg.get("selected_provider", "gemini")
        if selected_prov != "gemini" and not cfg.get("llm_active", True):
            self.ui.write_log("SYS: El motor LLM está desactivado. Actívalo para enviar comandos.")
            if not getattr(self.ui, "muted", False):
                self.ui.set_state("LISTENING")
            else:
                self.ui.set_state("MUTED")
            return None

        self.ui.set_state("THINKING")
        if not from_voice:
            self.ui.write_log(f"You: {text}")
        else:
            self.ui.write_log(f"You (Voice): {text}")

        response_content = None
        try:
            if not self._history:
                sys_prompt = self._build_chat_system_prompt()
                self._history.append(Message(role="system", content=sys_prompt))

            self._history.append(Message(role="user", content=text))

            cfg = load_config()
            selected_prov = cfg.get("selected_provider", "gemini")
            new_model = get_model(selected_prov)
            if hasattr(self.provider, 'model'):
                self.provider.model = new_model
            if hasattr(self.provider, 'config') and hasattr(self.provider.config, 'model'):
                self.provider.config.model = new_model

            response = await self.provider.tool_chat_loop(
                messages=self._history,
                tools=TOOL_DECLARATIONS,
                tool_implementations=TOOL_IMPLEMENTATIONS,
                max_turns=10,
            )

            self._history.append(response)
            self.ui.write_log(f"Jarvis: {response.content}")
            response_content = response.content

            if len(self._history) > 50:
                self._history = [self._history[0]] + self._history[-30:]

        except Exception as e:
            self.ui.write_log(f"ERR: {str(e)}")
            logger.exception("Chat loop exception")

        if not from_voice and self.voice_enabled and response_content and not engine_stop.is_set():
            self._is_playing_tts = True
            self.ui.set_state("SPEAKING")
            try:
                cleaned = _clean_text_for_tts(response_content)
                if cleaned:
                    tts_engine = self.cfg.get("tts_engine", "gemini")
                    if tts_engine == "piper":
                        if not hasattr(self, 'piper_provider'):
                            from core.tts_piper import PiperTTSProvider
                            self.piper_provider = PiperTTSProvider()
                        await asyncio.to_thread(self.piper_provider.speak, cleaned, True)
                    else:
                        wav_bytes = await _synthesize_speech_in_memory(response_content, self.cfg)
                        if wav_bytes:
                            spk_cfg = self.cfg.get("audio_output_device")
                            spk_dev = spk_cfg if isinstance(spk_cfg, int) and spk_cfg not in (0, 2) else None
                            vol = max(0, min(100, self.cfg.get("audio_volume", 80))) / 100.0
                            await asyncio.to_thread(_play_wav_file, wav_bytes, vol, spk_dev)
            except Exception as e:
                logger.error(f"[TTS Text-Mode] exception: {e}")
            finally:
                self._is_playing_tts = False

        if not from_voice:
            if not getattr(self.ui, "muted", False):
                self.ui.set_state("LISTENING")
            else:
                self.ui.set_state("MUTED")
        return response_content

    def _build_chat_system_prompt(self) -> str:
        from datetime import datetime
        memory = load_memory()
        mem_str = format_memory_for_prompt(memory)
        sys_prompt = _load_system_prompt()
        now = datetime.now()
        time_str = now.strftime("%A, %B %d, %Y — %I:%M %p")

        cfg = load_config()
        selected = cfg.get("selected_provider", "gemini")
        model_name = get_model(selected)
        prov_name = {"gemini": "Gemini", "ollama": "Ollama", "openrouter": "OpenRouter", "lmstudio": "LM Studio"}.get(selected, selected)

        parts = [
            f"[SYSTEM IDENTITY]\nYou are currently running via {prov_name} using the model: {model_name}.\n",
            f"[CURRENT DATE & TIME]\nRight now it is: {time_str}\n\n"
        ]
        if mem_str:
            parts.append(mem_str)
        parts.append(sys_prompt)
        return "\n".join(parts)

    async def _voice_loop(self):
        logger.info("Starting microphone listener...")
        audio_queue = asyncio.Queue()
        
        def callback(indata, frames, time_info, status):
            if engine_stop.is_set() or getattr(self.ui, "muted", False) or self._is_playing_tts or getattr(self, '_is_processing_voice', False):
                return
            data = indata.tobytes()
            try:
                self.ui._win.hud.push_audio_chunk(data)
            except Exception:
                pass
            self._loop.call_soon_threadsafe(audio_queue.put_nowait, data)

        mic_cfg = self.cfg.get("audio_input_device")
        if isinstance(mic_cfg, int) and mic_cfg == 0:
            import platform
            if platform.system() == "Windows":
                mic_dev = None
            else:
                mic_dev = 0
        elif isinstance(mic_cfg, int):
            mic_dev = mic_cfg
        else:
            mic_dev = None

        try:
            try:
                stream = sd.InputStream(
                    samplerate=16000,
                    channels=1,
                    dtype="int16",
                    blocksize=1024,
                    callback=callback,
                    device=mic_dev,
                )
            except sd.PortAudioError as pa_err:
                if "Invalid sample rate" in str(pa_err) and mic_dev is not None:
                    fallback = find_fallback_device(mic_dev, "input", 16000, 1)
                    logger.warning(f"Mic device {mic_dev} doesn't support 16000Hz. Falling back to device index {fallback}.")
                    mic_dev = fallback
                    stream = sd.InputStream(
                        samplerate=16000,
                        channels=1,
                        dtype="int16",
                        blocksize=1024,
                        callback=callback,
                        device=mic_dev,
                    )
                else:
                    raise
            stream.start()
        except Exception as e:
            logger.error(f"Mic error: {e}")
            self.ui.write_log(f"ERR: No se pudo iniciar el micrófono: {e}")
            return

        logger.info("Microphone active and listening.")

        recording = False
        audio_buffer = []
        silence_counter = 0
        
        VAD_THRESHOLD = 0.02
        SILENCE_CHUNKS = 24  # ~1.5 seconds at 16000Hz

        try:
            while not engine_stop.is_set():
                try:
                    chunk = await asyncio.wait_for(audio_queue.get(), timeout=0.1)
                except asyncio.TimeoutError:
                    continue

                if self._is_playing_tts or getattr(self, '_is_processing_voice', False):
                    recording = False
                    audio_buffer.clear()
                    silence_counter = 0
                    continue

                import struct
                import math
                n = len(chunk) // 2
                if n == 0:
                    continue
                samples = struct.unpack(f"{n}h", chunk)
                rms = math.sqrt(sum(s * s for s in samples) / n) / 32768.0
                
                if rms > VAD_THRESHOLD:
                    if not recording:
                        recording = True
                        logger.info("Habla detectada. Grabando...")
                        self.ui.set_state("LISTENING")
                    audio_buffer.append(chunk)
                    silence_counter = 0
                else:
                    if recording:
                        audio_buffer.append(chunk)
                        silence_counter += 1
                        
                        if silence_counter >= SILENCE_CHUNKS:
                            logger.info("Silencio detectado. Procesando audio...")
                            recording = False
                            silence_counter = 0
                            
                            speech_data = b"".join(audio_buffer)
                            audio_buffer.clear()
                            
                            self._is_processing_voice = True
                            asyncio.create_task(self._handle_voice_turn(speech_data))
        except Exception as e:
            logger.error(f"Loop exception: {e}")
        finally:
            try:
                stream.stop()
                stream.close()
            except Exception:
                pass

    async def _handle_voice_turn(self, speech_data: bytes):
        if not speech_data or len(speech_data) < 3200:
            return

        cfg = load_config()
        selected_prov = cfg.get("selected_provider", "gemini")
        if selected_prov != "gemini" and not cfg.get("llm_active", True):
            return

        self.ui.set_state("THINKING")
        temp_in = "temp_input.wav"

        try:
            _save_pcm_to_wav(temp_in, speech_data, sample_rate=16000)

            stt_engine = self.cfg.get("stt_engine", "gemini")
            self.ui.write_log(f"🎙 Transcribiendo vía {stt_engine.upper()} STT...")
            transcription = await _transcribe_audio(temp_in, self.cfg)
            if not transcription or not transcription.strip():
                logger.info("Transcripción vacía. Ignorando.")
                if not getattr(self.ui, "muted", False):
                    self.ui.set_state("LISTENING")
                else:
                    self.ui.set_state("MUTED")
                return

            response_text = await self._process_message(transcription, from_voice=True)
            
            if response_text and not engine_stop.is_set():
                self._is_playing_tts = True
                self.ui.set_state("SPEAKING")
                
                tts_engine = self.cfg.get("tts_engine", "gemini")
                self.ui.write_log(f"🗣 Hablando vía {tts_engine.upper()} TTS...")
                cleaned_text = _clean_text_for_tts(response_text)
                
                if cleaned_text:
                    if tts_engine == "piper":
                        if not hasattr(self, 'piper_provider'):
                            from core.tts_piper import PiperTTSProvider
                            self.piper_provider = PiperTTSProvider()
                        await asyncio.to_thread(self.piper_provider.speak, cleaned_text, True)
                    else:
                        wav_bytes = await _synthesize_speech_in_memory(response_text, self.cfg)
                        if wav_bytes:
                            spk_cfg = self.cfg.get("audio_output_device")
                            import platform
                            if isinstance(spk_cfg, int) and spk_cfg in (0, 2) and platform.system() == "Windows":
                                spk_dev = None
                            elif isinstance(spk_cfg, int):
                                spk_dev = spk_cfg
                            else:
                                spk_dev = None
                                
                            vol = max(0, min(100, self.cfg.get("audio_volume", 80))) / 100.0
                            await asyncio.to_thread(_play_wav_file, wav_bytes, vol, spk_dev)
                    
        except Exception as e:
            logger.error(f"Voice turn exception: {e}")
            self.ui.write_log(f"ERR: Error en procesamiento de voz: {e}")
        finally:
            self._is_processing_voice = False
            self._is_playing_tts = False
            if not getattr(self.ui, "muted", False):
                self.ui.set_state("LISTENING")
            else:
                self.ui.set_state("MUTED")

            if os.path.exists(temp_in):
                try:
                    os.remove(temp_in)
                except Exception:
                    pass

    async def run(self):
        self._loop = asyncio.get_event_loop()
        prov_name = {"GeminiProvider": "Gemini", "OllamaProvider": "Ollama", "OpenRouterProvider": "OpenRouter", "LMStudioProvider": "LM Studio"}.get(self.provider.__class__.__name__, self.provider.__class__.__name__)
        model_name = getattr(self.provider.config, 'model', 'default')
        
        logger.info(f"{prov_name} provider started and server ready with model: {model_name}")
        self.ui.set_state("LISTENING")
        
        if self.voice_enabled:
            logger.info(f"Listen started ({prov_name} Voice Wrapper)")
            self.ui.write_log(f"SYS: JARVIS online ({prov_name} - Modo de Voz). Habla para comunicarte.")
            asyncio.create_task(self._voice_loop())
        else:
            logger.info(f"Text mode started ({prov_name})")
            self.ui.write_log(f"SYS: JARVIS online ({prov_name}). Escribe un mensaje para comenzar.")

        while not engine_stop.is_set():
            await asyncio.sleep(1)

    async def stop(self):
        engine_stop.set()
