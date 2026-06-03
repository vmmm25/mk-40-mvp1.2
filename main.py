"""MARK XL — Multi-Provider J.A.R.V.I.S.

Supports three AI providers:
- Gemini: Real-time audio with Live API (the original Mark 39 experience)
- Ollama: Local models via REST API
- OpenRouter: Cloud models via REST API

The engine auto-detects the configured provider and starts the appropriate mode.
Switching providers at runtime is supported via the UI.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import threading
import time
import traceback
from contextlib import asynccontextmanager
from pathlib import Path

from google.genai import types

import sounddevice as sd
from ui import JarvisUI
from memory.memory_manager import (
    load_memory, update_memory, format_memory_for_prompt,
)
from memory.config_manager import (
    load_config, save_config, get_selected_provider, get_gemini_key,
    get_openrouter_key, get_ollama_url, get_model, set_model, is_configured,
    get_os_system,
)

from providers import create_provider, ProviderConfig, Message, list_providers
from core.logging_config import setup_logging
from providers.base import ToolCall, ToolResult

# ── Force UTF-8 console on Windows (prevents cp1252 emoji crashes) ──
if sys.platform == "win32":
    import io
    for _stream_name in ("stdout", "stderr"):
        _stream = getattr(sys, _stream_name)
        if hasattr(_stream, "buffer"):
            setattr(sys, _stream_name, io.TextIOWrapper(
                _stream.buffer, encoding="utf-8", errors="replace",
                line_buffering=_stream.line_buffering,
            ))

# ── Engine lifecycle control ────────────────────────────────────────
_engine_stop    = threading.Event()   # signal engine to stop
_engine_restart = threading.Event()   # signal engine to restart with new provider

# ── Tool implementations ────────────────────────────────────────────
from actions.file_processor import file_processor
from actions.flight_finder     import flight_finder
from actions.open_app          import open_app
from actions.weather_report    import weather_action
from actions.send_message      import send_message
from actions.reminder          import reminder
from actions.computer_settings import computer_settings
from actions.screen_processor  import screen_process
from actions.youtube_video     import youtube_video
from actions.desktop           import desktop_control
from actions.browser_control   import browser_control
from actions.file_controller   import file_controller
from actions.code_helper       import code_helper
from actions.dev_agent         import dev_agent
from actions.web_search        import web_search as web_search_action
from actions.computer_control  import computer_control
from actions.game_updater      import game_updater
from agent.task_queue import get_queue, TaskPriority


BASE_DIR        = Path(__file__).resolve().parent
PROMPT_PATH     = BASE_DIR / "core" / "prompt.txt"

# ── Audio constants (Gemini Live) ───────────────────────────────────
LIVE_MODEL          = "models/gemini-2.5-flash-native-audio-preview-12-2025"
CHANNELS            = 1
SEND_SAMPLE_RATE    = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE          = 1024


# ── System prompt ───────────────────────────────────────────────────
def _load_system_prompt() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except Exception:
        return (
            "You are JARVIS, Tony Stark's AI assistant running MARK XL. "
            "Be concise, direct, and always use the provided tools to complete tasks. "
            "Never simulate or guess results — always call the appropriate tool. "
            "You have access to the user's computer. Use desktop/browser/file tools as needed. "
            "Respond in the same language the user speaks to you."
        )


from tools.declarations import TOOL_DECLARATIONS
from tools.handlers import TOOL_IMPLEMENTATIONS


async def _execute_tool(name: str, args: dict, ui: JarvisUI) -> str:
    """Execute a tool by name and args. Returns result string."""
    print(f"[JARVIS] 🔧 {name}  {args}")
    ui.set_state("THINKING")

    if name == "save_memory":
        category = args.get("category", "notes")
        key      = args.get("key", "")
        value    = args.get("value", "")
        if key and value:
            update_memory({category: {key: {"value": value}}})
            print(f"[Memory] 💾 save_memory: {category}/{key} = {value}")
        if not ui.muted:
            ui.set_state("LISTENING")
        return "ok"

    loop = asyncio.get_event_loop()
    result = "Done."

    try:
        handler = TOOL_IMPLEMENTATIONS.get(name)
        if handler:
            result = handler(args, ui) or "Done."
        else:
            result = f"Unknown tool: {name}"

    except Exception as e:
        result = f"Tool '{name}' failed: {e}"
        traceback.print_exc()
        ui.write_log(f"ERR: {name} — {str(e)[:120]}")

    if not ui.muted:
        ui.set_state("LISTENING")

    print(f"[JARVIS] 📤 {name} → {str(result)[:80]}")
    return result


def find_fallback_device(device_index: int | None, kind: str, samplerate: int, channels: int) -> int | None:
    if device_index is None:
        return None
    try:
        dev_info = sd.query_devices(device_index)
        name = dev_info.get("name", "")
        for d in sd.query_devices():
            if d["index"] == device_index:
                continue
            if kind == "input" and d["max_input_channels"] < channels:
                continue
            if kind == "output" and d["max_output_channels"] < channels:
                continue
            
            clean_name1 = name.split(",")[0].strip()
            clean_name2 = d["name"].split(",")[0].strip()
            
            if clean_name1 in clean_name2 or clean_name2 in clean_name1 or clean_name1[:15] in clean_name2:
                try:
                    if kind == "input":
                        sd.check_input_settings(device=d["index"], samplerate=samplerate, channels=channels, dtype="int16")
                    else:
                        sd.check_output_settings(device=d["index"], samplerate=samplerate, channels=channels, dtype="int16")
                    return d["index"]
                except Exception:
                    continue
    except Exception:
        pass
    return None


# ── Synchronous Audio / Voice Utilities ──────────────────────────────
def _save_pcm_to_wav(filename: str, audio_data: bytes, sample_rate: int = 16000):
    """Save raw 16-bit PCM bytes to a WAV file using the built-in wave module."""
    import wave
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data)

def _play_wav_file(wav_data: str | bytes, volume: float = 1.0, device: int | None = None):
    """Play a WAV file (from physical path or raw in-memory bytes) using sounddevice."""
    import wave
    import io
    import sounddevice as sd
    from array import array
    try:
        if isinstance(wav_data, bytes):
            wav_file = io.BytesIO(wav_data)
        else:
            wav_file = wav_data
            
        with wave.open(wav_file, 'rb') as wf:
            samplerate = wf.getframerate()
            channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            
            if sampwidth == 2:
                dtype = 'int16'
            elif sampwidth == 4:
                dtype = 'float32'
            else:
                dtype = 'int8'
                
            try:
                stream = sd.RawOutputStream(
                    samplerate=samplerate,
                    channels=channels,
                    dtype=dtype,
                    device=device,
                )
            except sd.PortAudioError as pa_err:
                if "Invalid sample rate" in str(pa_err) and device is not None:
                    fallback = find_fallback_device(device, "output", samplerate, channels)
                    print(f"[JARVIS] ⚠️ Speaker device {device} doesn't support {samplerate}Hz. Falling back to device index {fallback}.")
                    device = fallback
                    stream = sd.RawOutputStream(
                        samplerate=samplerate,
                        channels=channels,
                        dtype=dtype,
                        device=device,
                    )
                else:
                    raise
            with stream:
                chunk_size = 1024
                data = wf.readframes(chunk_size)
                while data and not _engine_stop.is_set():
                    # Apply master volume
                    if volume < 1.0 and dtype == 'int16':
                        scale = array('h', data)
                        scale = array('h', (int(s * volume) for s in scale))
                        data = scale.tobytes()
                    stream.write(data)
                    data = wf.readframes(chunk_size)
                
                # Padding de silencio al final para prevenir pops / clics residuales en la tarjeta de sonido
                if dtype == 'int16':
                    stream.write(b'\x00' * (channels * 2 * int(samplerate * 0.15)))
                elif dtype == 'float32':
                    stream.write(b'\x00' * (channels * 4 * int(samplerate * 0.15)))
    except Exception as e:
        print(f"[JARVIS] ❌ Play WAV error: {e}")

def _pcm_to_wav_bytes(pcm_data: bytes, sample_rate: int = 24000) -> bytes:
    """Wrap raw 16-bit mono PCM bytes with a standard WAV header in-memory."""
    import io
    import wave
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)
    return wav_io.getvalue()

def _clean_whisper_transcript(text: str) -> str:
    """Clean Whisper transcription output from hallucinations, noise tags, and timestamps."""
    import re
    if not text:
        return ""

    # Remove standard timestamps if any slip in
    text = re.sub(r"\[\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}\]", "", text)
    text = re.sub(r"\[\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}\.\d{3}\]", "", text)
    text = re.sub(r"\[\d{2}:\d{2}\s*-->\s*\d{2}:\d{2}\]", "", text)

    # Remove bracket noise tags: [música], [blank], (risas), [silencio]
    text = re.sub(r"\[[^\]]+\]", "", text)
    text = re.sub(r"\([^)]+\)", "", text)

    # Clean up spacing
    text = re.sub(r"\s+", " ", text).strip()

    # Filter out common silent/low-volume hallucinations of Whisper in Spanish/English
    hallucinations = [
        "subtítulos por amara.org",
        "subtitulado por amara",
        "gracias por ver",
        "gracias por ver este vídeo",
        "gracias por ver este video",
        "gracias por su atención",
        "¡gracias!",
        "thanks for watching",
        "gracias.",
        "gracias",
        "amén",
        "amén.",
        "silencio",
        "música",
        "suscríbete al canal",
        "dale a like",
        "suscríbete",
    ]
    test_clean = text.lower().strip(" .,!¡?¿")
    if test_clean in hallucinations or not test_clean:
        return ""
    return text


def _clean_text_for_tts(text: str) -> str:
    """Clean text before feeding to TTS (Gemini/Piper) to prevent pronunciation of Markdown, emojis, or code blocks."""
    import re
    if not text:
        return ""

    # 1. Remove control tags (e.g. <ctrl1>, <ctrl2>)
    text = re.sub(r"<ctrl\d+>", "", text, flags=re.IGNORECASE)

    # 2. Completely strip out code blocks (```python ... ```) since reading code is terrible in TTS
    text = re.sub(r"```[a-zA-Z0-9_-]*\n.*?```", "", text, flags=re.DOTALL)
    # Remove single backticks
    text = re.sub(r"`", "", text)

    # 3. Clean Markdown formatting (headings, bold, italics, bullet points)
    text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)
    text = re.sub(r"^[-\*+]\s+", "", text, flags=re.MULTILINE)

    # 4. Remove links [link text](url) and keep only link text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # 5. Remove graphical emojis and decorative characters (keep standard punctuation/accented characters)
    allowed_chars = re.compile(r"[^a-zA-Z0-9\s.,;:!¡?¿()\-'\’\"a-áéíóúüñÁÉÍÓÚÜÑ$%\u20AC]")
    text = allowed_chars.sub("", text)

    # 6. Clean up line breaks and repeated spaces
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


async def _transcribe_audio(wav_path: str, cfg: dict) -> str:
    """Transcribe an audio file using either Gemini Cloud STT or Whisper.cpp Local STT."""
    stt_engine = cfg.get("stt_engine", "gemini")
    
    if stt_engine == "whisper":
        whisper_p = cfg.get("whisper_path", "")
        whisper_m = cfg.get("whisper_model", "")
        
        if not whisper_p or not os.path.exists(whisper_p):
            raise FileNotFoundError("El ejecutable de Whisper.cpp no está configurado o no existe.")
        if not whisper_m or not os.path.exists(whisper_m):
            raise FileNotFoundError("El modelo GGML de Whisper.cpp no está configurado o no existe.")
            
        print(f"[JARVIS] 🎙 Transcribing with Whisper.cpp (Local) using {os.path.basename(whisper_m)}...")
        
        cmd = [
            whisper_p,
            "-m", whisper_m,
            "-f", wav_path,
            "-nt", # no timestamps
            "-l", "es", # assume Spanish by default
        ]
        
        def run_whisper():
            import subprocess
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
            if result.returncode != 0:
                raise RuntimeError(f"whisper.cpp error: {result.stderr}")
            return result.stdout.strip()
            
        raw_text = await asyncio.to_thread(run_whisper)
        return _clean_whisper_transcript(raw_text)
        
    else: # Cloud STT (Gemini)
        print("[JARVIS] 🎙 Transcribing with Gemini (Cloud)...")
        api_key = cfg.get("gemini_api_key", "")
        if not api_key:
            raise ValueError("Gemini API key is required for Gemini Cloud transcription.")
            
        from google import genai
        from google.genai import types
        
        client = genai.Client(
            api_key=api_key,
            http_options={"api_version": "v1beta"},
        )
        
        with open(wav_path, "rb") as f:
            audio_bytes = f.read()
            
        def run_gemini():
            response = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type="audio/wav",
                    ),
                    "Transcribe este archivo de audio con la mayor precisión posible. Responde únicamente con el texto transcrito en el idioma original del hablante, sin añadir explicaciones, traducciones o metadatos."
                ]
            )
            return response.text.strip() if response.text else ""
            
        try:
            raw_text = await asyncio.to_thread(run_gemini)
            return _clean_whisper_transcript(raw_text)
        except Exception as ge:
            print(f"[JARVIS] ⚠️ Gemini Cloud STT failed ({ge}). Falling back to local Whisper...")
            cfg_fallback = dict(cfg)
            cfg_fallback["stt_engine"] = "whisper"
            return await _transcribe_audio(wav_path, cfg_fallback)


async def _synthesize_with_piper_fallback(text: str, cfg: dict, reason: str) -> bytes | None:
    """Fallback silently to local Piper speech synthesis if Cloud TTS fails."""
    print(f"[JARVIS] ⚠️ Gemini Cloud TTS failed ({reason}). Falling back to local Piper...")
    piper_p = cfg.get("piper_path", "")
    piper_m = cfg.get("piper_model", "")
    if piper_p and os.path.exists(piper_p) and piper_m and os.path.exists(piper_m):
        cmd = [
            piper_p,
            "-m", piper_m,
            "--length_scale", "1.1", # Slightly slower and clearer
            "--sentence_silence", "0.3",
            "-f", "-", # Output WAV directly to stdout
        ]
        def run_piper():
            import subprocess
            result = subprocess.run(cmd, input=text.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False)
            if result.returncode != 0:
                raise RuntimeError(f"Piper error: {result.stderr.decode('utf-8', errors='replace')}")
            return result.stdout
        try:
            return await asyncio.to_thread(run_piper)
        except Exception as pe:
            print(f"[JARVIS] ❌ Piper fallback also failed: {pe}")
    else:
        print("[JARVIS] ❌ Local Piper is not fully configured/available for fallback.")
    return None


async def _synthesize_speech_in_memory(text: str, cfg: dict) -> bytes | None:
    """Synthesize text to speech in-memory, returning raw WAV bytes."""
    # Clean text to remove Markdown, emojis, code blocks, and decorative garbage
    text = _clean_text_for_tts(text)
    if not text:
        return None

    tts_engine = cfg.get("tts_engine", "gemini")
    
    if tts_engine == "piper":
        piper_p = cfg.get("piper_path", "")
        piper_m = cfg.get("piper_model", "")
        
        if not piper_p or not os.path.exists(piper_p):
            raise FileNotFoundError("El ejecutable de Piper no está configurado o no existe.")
        if not piper_m or not os.path.exists(piper_m):
            raise FileNotFoundError("El modelo de voz de Piper (.onnx) no está configurado o no existe.")
            
        print(f"[JARVIS] 🗣 Synthesizing in-memory with Piper (Local) using {os.path.basename(piper_m)}...")
        
        cmd = [
            piper_p,
            "-m", piper_m,
            "--length_scale", "1.1", # Slightly slower and clearer
            "--sentence_silence", "0.3",
            "-f", "-", # Output WAV directly to stdout
        ]
        
        def run_piper():
            import subprocess
            result = subprocess.run(cmd, input=text.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False)
            if result.returncode != 0:
                raise RuntimeError(f"Piper error: {result.stderr.decode('utf-8', errors='replace')}")
            return result.stdout # WAV bytes
            
        return await asyncio.to_thread(run_piper)
        
    else: # Cloud TTS (Gemini)
        print("[JARVIS] 🗣 Synthesizing in-memory with Gemini (Cloud)...")
        api_key = cfg.get("gemini_api_key", "")
        if not api_key:
            return await _synthesize_with_piper_fallback(text, cfg, "No Gemini API key configured.")
            
        from google import genai
        from google.genai import types
        
        client = genai.Client(
            api_key=api_key,
            http_options={"api_version": "v1beta"},
        )
        
        def run_gemini():
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[f"Lee en voz alta de manera clara, natural y con buena entonación el siguiente texto: {text}"],
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name="Charon"  # Puck, Charon, Kore, Fenrir
                                )
                            )
                        )
                    )
                )
                audio_bytes = None
                for candidate in getattr(response, "candidates", []):
                    for part in getattr(candidate.content, "parts", []):
                        if hasattr(part, "inline_data") and part.inline_data:
                            audio_bytes = part.inline_data.data
                            break
                if audio_bytes:
                    if audio_bytes.startswith(b"RIFF"):
                        return audio_bytes
                    # Gemini returns raw PCM; wrap it as WAV bytes
                    return _pcm_to_wav_bytes(audio_bytes, sample_rate=24000)
                raise ValueError("No audio bytes returned from Gemini API.")
            except Exception as e:
                raise e
            
        try:
            return await asyncio.to_thread(run_gemini)
        except Exception as ge:
            return await _synthesize_with_piper_fallback(text, cfg, str(ge))


# ── Mode 1: Gemini Live Audio (original Mark 39 experience) ─────────

class JarvisLive:
    """Gemini Live real-time audio session."""

    def __init__(self, ui: JarvisUI, provider):
        self.ui             = ui
        self.provider       = provider
        self.session        = None
        self.audio_in_queue = None
        self.out_queue      = None
        self._loop          = None
        self._is_speaking   = False
        self._speaking_lock = threading.Lock()
        self.ui.on_text_command = self._on_text_command
        self._turn_done_event: asyncio.Event | None = None

    def _on_text_command(self, text: str):
        if not self._loop or not self.session or _engine_stop.is_set():
            return
        asyncio.run_coroutine_threadsafe(
            self.session.send_client_content(
                turns={"parts": [{"text": text}]},
                turn_complete=True
            ),
            self._loop
        )

    def set_speaking(self, value: bool):
        with self._speaking_lock:
            self._is_speaking = value
        if value:
            self.ui.set_state("SPEAKING")
        elif not self.ui.muted:
            self.ui.set_state("LISTENING")

    async def _send_realtime(self):
        while not _engine_stop.is_set():
            try:
                msg = await asyncio.wait_for(self.out_queue.get(), timeout=1.0)
                await self.session.send_realtime_input(media=msg)
            except asyncio.TimeoutError:
                continue

    async def _listen_audio(self):
        print("[JARVIS] 🎤 Mic started")
        loop = asyncio.get_event_loop()

        def callback(indata, frames, time_info, status):
            with self._speaking_lock:
                jarvis_speaking = self._is_speaking
            if not jarvis_speaking and not self.ui.muted:
                data = indata.tobytes()
                # Feed audio to visualiser (non-blocking)
                try:
                    self.ui._win.hud.push_audio_chunk(data)
                except Exception:
                    pass
                def _put_audio(data):
                    try:
                        self.out_queue.put_nowait({"data": data, "mime_type": "audio/pcm"})
                    except asyncio.QueueFull:
                        pass
                loop.call_soon_threadsafe(_put_audio, data)

        try:
            mic_cfg = load_config().get("audio_input_device")
            # Device 0 on Windows is the Sound Mapper (virtual), not a real mic.
            # Skip it and fall back to the system default (None).
            if isinstance(mic_cfg, int) and mic_cfg == 0:
                import platform
                if platform.system() == "Windows":
                    print("[JARVIS] ⚠️  audio_input_device=0 is the Windows Sound Mapper — using system default mic instead.")
                    mic_dev = None
                else:
                    mic_dev = 0
            elif isinstance(mic_cfg, int):
                mic_dev = mic_cfg
            else:
                mic_dev = None

            dev_name = str(sd.query_devices(mic_dev or sd.default.device[0])["name"]) if mic_dev is not None else "system default"
            print(f"[JARVIS] 🎤 Using mic: {dev_name} (device={mic_dev})")

            try:
                stream = sd.InputStream(
                    samplerate=SEND_SAMPLE_RATE,
                    channels=CHANNELS,
                    dtype="int16",
                    blocksize=CHUNK_SIZE,
                    callback=callback,
                    device=mic_dev,
                )
            except sd.PortAudioError as pa_err:
                if "Invalid sample rate" in str(pa_err) and mic_dev is not None:
                    fallback = find_fallback_device(mic_dev, "input", SEND_SAMPLE_RATE, CHANNELS)
                    print(f"[JARVIS] ⚠️ Mic device {mic_dev} doesn't support {SEND_SAMPLE_RATE}Hz. Falling back to device index {fallback}.")
                    mic_dev = fallback
                    stream = sd.InputStream(
                        samplerate=SEND_SAMPLE_RATE,
                        channels=CHANNELS,
                        dtype="int16",
                        blocksize=CHUNK_SIZE,
                        callback=callback,
                        device=mic_dev,
                    )
                else:
                    raise

            with stream:
                print("[JARVIS] 🎤 Mic stream open")
                while not _engine_stop.is_set():
                    await asyncio.sleep(0.1)
        except Exception as e:
            print(f"[JARVIS] ❌ Mic: {e}")
            raise

    async def _receive_audio(self):
        print("[JARVIS] 👂 Recv started")
        out_buf, in_buf = [], []
        _CTRL_RE = re.compile(r"<ctrl\d+>", re.IGNORECASE)

        def clean(t: str) -> str:
            return _CTRL_RE.sub("", re.sub(r"[\x00-\x08\x0b-\x1f]", "", t)).strip()

        try:
            while not _engine_stop.is_set():
                async for response in self.session.receive():

                    if response.data:
                        if self._turn_done_event and self._turn_done_event.is_set():
                            self._turn_done_event.clear()
                        self.audio_in_queue.put_nowait(response.data)

                    if response.server_content:
                        sc = response.server_content

                        if sc.output_transcription and sc.output_transcription.text:
                            txt = clean(sc.output_transcription.text)
                            if txt:
                                out_buf.append(txt)

                        if sc.input_transcription and sc.input_transcription.text:
                            txt = clean(sc.input_transcription.text)
                            if txt:
                                in_buf.append(txt)

                        if sc.turn_complete:
                            if self._turn_done_event:
                                self._turn_done_event.set()

                            full_in = " ".join(in_buf).strip()
                            if full_in:
                                self.ui.write_log(f"You: {full_in}")
                            in_buf = []

                            full_out = " ".join(out_buf).strip()
                            if full_out:
                                self.ui.write_log(f"Jarvis: {full_out}")
                            out_buf = []

                    if response.tool_call:
                        fn_responses = []
                        for fc in response.tool_call.function_calls:
                            print(f"[JARVIS] 📞 {fc.name}")
                            result = await _execute_tool(fc.name, dict(fc.args or {}), self.ui)
                            fn_responses.append(types.FunctionResponse(
                                id=fc.id, name=fc.name,
                                response={"result": result}
                            ))
                        await self.session.send_tool_response(
                            function_responses=fn_responses
                        )
        except Exception as e:
            print(f"[JARVIS] ❌ Recv: {e}")
            traceback.print_exc()
            raise

    async def _play_audio(self):
        print("[JARVIS] 🔊 Play started")
        cfg = load_config()
        spk_cfg = cfg.get("audio_output_device")
        # Device 0 or 2 on Windows are Sound Mappers (virtual) — use None for system default
        import platform as _platform
        if isinstance(spk_cfg, int) and spk_cfg in (0, 2) and _platform.system() == "Windows":
            print("[JARVIS] ⚠️  audio_output_device is a Windows Sound Mapper — using system default speaker.")
            spk_dev = None
        elif isinstance(spk_cfg, int):
            spk_dev = spk_cfg
        else:
            spk_dev = None
        vol = max(0, min(100, cfg.get("audio_volume", 80))) / 100.0
        try:
            stream = sd.RawOutputStream(
                samplerate=RECEIVE_SAMPLE_RATE,
                channels=CHANNELS,
                dtype="int16",
                blocksize=CHUNK_SIZE,
                device=spk_dev,
            )
        except sd.PortAudioError as pa_err:
            if "Invalid sample rate" in str(pa_err) and spk_dev is not None:
                fallback = find_fallback_device(spk_dev, "output", RECEIVE_SAMPLE_RATE, CHANNELS)
                print(f"[JARVIS] ⚠️ Speaker device {spk_dev} doesn't support {RECEIVE_SAMPLE_RATE}Hz. Falling back to device index {fallback}.")
                spk_dev = fallback
                stream = sd.RawOutputStream(
                    samplerate=RECEIVE_SAMPLE_RATE,
                    channels=CHANNELS,
                    dtype="int16",
                    blocksize=CHUNK_SIZE,
                    device=spk_dev,
                )
            else:
                raise
        stream.start()

        from array import array
        try:
            while not _engine_stop.is_set():
                try:
                    chunk = await asyncio.wait_for(
                        self.audio_in_queue.get(),
                        timeout=0.2
                    )
                except asyncio.TimeoutError:
                    if self.audio_in_queue.empty():
                        self.set_speaking(False)
                    continue
                self.set_speaking(True)
                # Apply volume scaling
                if vol < 1.0:
                    data = array('h', chunk)
                    data = array('h', (int(s * vol) for s in data))
                    chunk = data.tobytes()
                await asyncio.to_thread(stream.write, chunk)
        except Exception as e:
            print(f"[JARVIS] ❌ Play: {e}")
            raise
        finally:
            self.set_speaking(False)
            stream.stop()
            stream.close()

    async def _shutdown_monitor(self):
        """Watch for engine stop signal and close the session immediately."""
        try:
            while not _engine_stop.is_set():
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            pass
        finally:
            # Force-close the session so blocking tasks (receive, etc.) unblock
            if self.session:
                try:
                    await self.session.close()
                except Exception:
                    pass

    @asynccontextmanager
    async def _build_live_session(self):
        """Async context manager that yields a Gemini Live session."""
        from datetime import datetime
        memory     = load_memory()
        mem_str    = format_memory_for_prompt(memory)
        sys_prompt = _load_system_prompt()
        now        = datetime.now()
        time_str   = now.strftime("%A, %B %d, %Y — %I:%M %p")

        parts = [
            f"[CURRENT DATE & TIME]\nRight now it is: {time_str}\n"
            f"Use this to calculate exact times for reminders.\n\n"
        ]
        if mem_str:
            parts.append(mem_str)
        parts.append(sys_prompt)

        # Use the provider's async context manager to get a live session
        async with self.provider.create_live_session({
            "system_prompt": "\n".join(parts),
            "tools": TOOL_DECLARATIONS,
            "memory_str": mem_str if mem_str else "",
        }) as session:
            yield session

    async def run(self):
        while not _engine_stop.is_set():
            try:
                print("-" * 50)
                print(f"[JARVIS] 🔌 Connecting to Gemini Live with model: {LIVE_MODEL}...")
                print("-" * 50)
                self.ui.set_state("THINKING")

                # Use async with to properly enter both the live session
                # and the TaskGroup context managers
                async with self._build_live_session() as session:
                    # Inner try/except* for TaskGroup (ExceptionGroup only)
                    try:
                        async with asyncio.TaskGroup() as tg:
                            self.session        = session
                            self._loop          = asyncio.get_event_loop()
                            self.audio_in_queue = asyncio.Queue()
                            self.out_queue      = asyncio.Queue(maxsize=10)
                            self._turn_done_event = asyncio.Event()

                            print("[JARVIS] [OK] Connected to Gemini Live.")
                            print("[JARVIS] ▶️ React started")
                            self.ui.set_state("LISTENING")
                            self.ui.write_log("SYS: JARVIS online (Gemini Live Audio).")

                            tg.create_task(self._send_realtime())
                            tg.create_task(self._listen_audio())
                            tg.create_task(self._receive_audio())
                            tg.create_task(self._play_audio())
                            tg.create_task(self._shutdown_monitor())
                    except* Exception as ex_group:
                        for e in ex_group.exceptions:
                            # Suppress normal shutdown/cancellation errors
                            if _engine_stop.is_set():
                                continue
                            try:
                                from google.genai.errors import APIError
                                if isinstance(e, APIError) and "1000" in str(e):
                                    continue
                            except Exception:
                                pass

                            msg = f"[JARVIS] ⚠️ Task: {e}"
                            print(msg)
                            self.ui.write_log(f"SYS: Task error: {e}")
                            traceback.print_exc()

            except Exception as e:
                msg = f"[JARVIS] ❌ Connection failed: {e}"
                print(msg)
                self.ui.write_log(f"SYS: Connection error: {e}")
                traceback.print_exc()

            self.set_speaking(False)
            self.ui.set_state("THINKING")
            print("[JARVIS] 🔄 Reconnecting in 3s...")
            # Check stop event periodically during reconnect delay
            for _ in range(30):
                if _engine_stop.is_set():
                    break
                await asyncio.sleep(0.1)


# ── Mode 2: Chat-based (Ollama, OpenRouter, Gemini text) ───────────

class JarvisChat:
    """Text-based chat using any provider (Ollama, OpenRouter, Gemini text) with synchronized voice wrapper support."""

    def __init__(self, ui: JarvisUI, provider):
        self.ui       = ui
        self.provider = provider
        self._history: list[Message] = []
        self._loop    = None
        self.ui.on_text_command = self._on_text_command
        self.cfg = load_config()
        self.voice_enabled = self.cfg.get("voice_wrapper_enabled", False)
        self._is_playing_tts = False # flag to prevent mic recording while speaking

    def _on_text_command(self, text: str):
        if not self._loop or _engine_stop.is_set():
            return
        asyncio.run_coroutine_threadsafe(self._process_message(text), self._loop)

    async def _process_message(self, text: str, from_voice: bool = False) -> str | None:
        """Process a user message through the chat provider."""
        self.ui.set_state("THINKING")
        if not from_voice:
            self.ui.write_log(f"You: {text}")
        else:
            self.ui.write_log(f"You (Voice): {text}")

        response_content = None
        try:
            # Build system message if first turn
            if not self._history:
                sys_prompt = self._build_chat_system_prompt()
                self._history.append(Message(role="system", content=sys_prompt))

            # Add user message
            self._history.append(Message(role="user", content=text))

            # Dynamically sync the model from config before calling the provider
            cfg = load_config()
            selected_prov = cfg.get("selected_provider", "gemini")
            new_model = get_model(selected_prov)
            if hasattr(self.provider, 'model'):
                self.provider.model = new_model
            if hasattr(self.provider, 'config') and hasattr(self.provider.config, 'model'):
                self.provider.config.model = new_model

            # Run tool chat loop
            response = await self.provider.tool_chat_loop(
                messages=self._history,
                tools=TOOL_DECLARATIONS,
                tool_implementations=TOOL_IMPLEMENTATIONS,
                max_turns=10,
            )

            # Add response to history
            self._history.append(response)
            self.ui.write_log(f"Jarvis: {response.content}")
            response_content = response.content

            # Keep history manageable
            if len(self._history) > 50:
                self._history = [self._history[0]] + self._history[-30:]  # keep system + recent

        except Exception as e:
            self.ui.write_log(f"ERR: {str(e)}")
            traceback.print_exc()

        # Si el voice_wrapper está habilitado, pero la entrada fue de texto, leemos la respuesta
        if not from_voice and self.voice_enabled and response_content and not _engine_stop.is_set():
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
                        # Run blocking TTS in a background thread so UI doesn't freeze
                        await asyncio.to_thread(self.piper_provider.speak, cleaned, True)
                    else:
                        wav_bytes = await _synthesize_speech_in_memory(response_content, self.cfg)
                        if wav_bytes:
                            spk_cfg = self.cfg.get("audio_output_device")
                            spk_dev = spk_cfg if isinstance(spk_cfg, int) and spk_cfg not in (0, 2) else None
                            vol = max(0, min(100, self.cfg.get("audio_volume", 80))) / 100.0
                            await asyncio.to_thread(_play_wav_file, wav_bytes, vol, spk_dev)
            except Exception as e:
                print(f"[JARVIS] ❌ [TTS Text-Mode] exception: {e}")
            finally:
                self._is_playing_tts = False

        if not from_voice:
            if not self.ui.muted:
                self.ui.set_state("LISTENING")
            else:
                self.ui.set_state("MUTED")
        return response_content

    def _build_chat_system_prompt(self) -> str:
        from datetime import datetime
        memory     = load_memory()
        mem_str    = format_memory_for_prompt(memory)
        sys_prompt = _load_system_prompt()
        now        = datetime.now()
        time_str   = now.strftime("%A, %B %d, %Y — %I:%M %p")

        # Get current provider and model to enforce identity
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
        """Microphone recording and Speech-to-Text VAD loop."""
        print("[JARVIS] [Voice Wrapper] Starting microphone listener...")
        audio_queue = asyncio.Queue()
        
        def callback(indata, frames, time_info, status):
            if _engine_stop.is_set() or self.ui.muted or self._is_playing_tts or getattr(self, '_is_processing_voice', False):
                return
            data = indata.tobytes()
            # Push to visualizer
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
                    print(f"[JARVIS] ⚠️ [Voice Wrapper] Mic device {mic_dev} doesn't support 16000Hz. Falling back to device index {fallback}.")
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
            print(f"[JARVIS] ❌ [Voice Wrapper] Mic error: {e}")
            self.ui.write_log(f"ERR: No se pudo iniciar el micrófono: {e}")
            return

        print("[JARVIS] [Voice Wrapper] Microphone active and listening.")

        recording = False
        audio_buffer = []
        silence_counter = 0
        
        VAD_THRESHOLD = 0.02
        SILENCE_CHUNKS = 24  # ~1.5 seconds at 16000Hz (16 chunks/sec)

        try:
            while not _engine_stop.is_set():
                try:
                    chunk = await asyncio.wait_for(audio_queue.get(), timeout=0.1)
                except asyncio.TimeoutError:
                    continue

                if self._is_playing_tts or getattr(self, '_is_processing_voice', False):
                    recording = False
                    audio_buffer.clear()
                    silence_counter = 0
                    continue

                # Calculate RMS
                import struct
                import math
                n = len(chunk) // 2
                if n == 0:
                    continue
                samples = struct.unpack(f"{n}h", chunk)
                rms = math.sqrt(sum(s * s for s in samples) / n) / 32768.0
                
                # Check VAD
                if rms > VAD_THRESHOLD:
                    if not recording:
                        recording = True
                        print("[JARVIS] [Voice Wrapper] 🎤 Habla detectada. Grabando...")
                        self.ui.set_state("LISTENING")
                    audio_buffer.append(chunk)
                    silence_counter = 0
                else:
                    if recording:
                        audio_buffer.append(chunk)
                        silence_counter += 1
                        
                        if silence_counter >= SILENCE_CHUNKS:
                            print("[JARVIS] [Voice Wrapper] 🤐 Silencio detectado. Procesando audio...")
                            recording = False
                            silence_counter = 0
                            
                            speech_data = b"".join(audio_buffer)
                            audio_buffer.clear()
                            
                            self._is_processing_voice = True
                            asyncio.create_task(self._handle_voice_turn(speech_data))
        except Exception as e:
            print(f"[JARVIS] ❌ [Voice Wrapper] Loop exception: {e}")
        finally:
            try:
                stream.stop()
                stream.close()
            except Exception:
                pass

    async def _handle_voice_turn(self, speech_data: bytes):
        """Handle a single voice-input user turn synchronously."""
        if not speech_data or len(speech_data) < 3200:
            return

        self.ui.set_state("THINKING")
        temp_in = "temp_input.wav"

        try:
            # 1. Save PCM to WAV (We keep this temp file for Whisper.cpp CLI)
            _save_pcm_to_wav(temp_in, speech_data, sample_rate=16000)

            # 2. Transcribe WAV
            stt_engine = self.cfg.get("stt_engine", "gemini")
            self.ui.write_log(f"🎙 Transcribiendo vía {stt_engine.upper()} STT...")
            transcription = await _transcribe_audio(temp_in, self.cfg)
            if not transcription or not transcription.strip():
                print("[JARVIS] [Voice Wrapper] Transcripción vacía. Ignorando.")
                if not self.ui.muted:
                    self.ui.set_state("LISTENING")
                else:
                    self.ui.set_state("MUTED")
                return

            # 3. Process LLM message
            response_text = await self._process_message(transcription, from_voice=True)
            
            if response_text and not _engine_stop.is_set():
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
                        # Usar el módulo nativo PiperTTSProvider de forma bloqueante (en to_thread)
                        await asyncio.to_thread(self.piper_provider.speak, cleaned_text, True)
                    else:
                        # 4. Synthesize TTS 100% in-memory (RAM-Only)
                        wav_bytes = await _synthesize_speech_in_memory(response_text, self.cfg)
                        if wav_bytes:
                            # 5. Play synthetic voice WAV directly from memory
                            spk_cfg = self.cfg.get("audio_output_device")
                            import platform
                            if isinstance(spk_cfg, int) and spk_cfg in (0, 2) and platform.system() == "Windows":
                                spk_dev = None
                            elif isinstance(spk_cfg, int):
                                spk_dev = spk_cfg
                            else:
                                spk_dev = None
                                
                            vol = max(0, min(100, self.cfg.get("audio_volume", 80))) / 100.0
                            
                            # Play WAV bytes synchronously in thread to avoid freezing visualizer thread
                            await asyncio.to_thread(_play_wav_file, wav_bytes, vol, spk_dev)
                    
        except Exception as e:
            print(f"[JARVIS] ❌ [Voice Wrapper] Voice turn exception: {e}")
            self.ui.write_log(f"ERR: Error en procesamiento de voz: {e}")
        finally:
            self._is_processing_voice = False
            self._is_playing_tts = False
            if not self.ui.muted:
                self.ui.set_state("LISTENING")
            else:
                self.ui.set_state("MUTED")

            # Cleanup temp input file
            if os.path.exists(temp_in):
                try:
                    os.remove(temp_in)
                except Exception:
                    pass

    async def run(self):
        self._loop = asyncio.get_event_loop()
        prov_name = {"GeminiProvider": "Gemini", "OllamaProvider": "Ollama", "OpenRouterProvider": "OpenRouter", "LMStudioProvider": "LM Studio"}.get(self.provider.__class__.__name__, self.provider.__class__.__name__)
        model_name = getattr(self.provider.config, 'model', 'default')
        
        print("-" * 50)
        print(f"[JARVIS] [OK] {prov_name} provider started and server ready with model: {model_name}")
        print("-" * 50)
        
        self.ui.set_state("LISTENING")
        
        if self.voice_enabled:
            print(f"[JARVIS] 🎤 Listen started ({prov_name} Voice Wrapper)")
            self.ui.write_log(f"SYS: JARVIS online ({prov_name} - Modo de Voz). Habla para comunicarte.")
            asyncio.create_task(self._voice_loop())
        else:
            print(f"[JARVIS] 💬 Text mode started ({prov_name})")
            self.ui.write_log(f"SYS: JARVIS online ({prov_name}). Escribe un mensaje para comenzar.")

        while not _engine_stop.is_set():
            await asyncio.sleep(1)


# ── Provider Factory ────────────────────────────────────────────────

def _build_provider_config() -> ProviderConfig:
    """Build a ProviderConfig from the saved config, fully provider-aware."""
    cfg = load_config()
    selected = cfg.get("selected_provider", "gemini")

    api_key = ""
    base_url = ""

    if selected == "gemini":
        api_key = cfg.get("gemini_api_key", "")
    elif selected == "openrouter":
        api_key = cfg.get("openrouter_api_key", "")
    elif selected == "ollama":
        base_url = cfg.get("ollama_url", "http://localhost:11434")
    elif selected == "lmstudio":
        base_url = cfg.get("lmstudio_url", "http://localhost:1234")

    return ProviderConfig(
        api_key=api_key,
        base_url=base_url,
        model=get_model(selected),
        system_prompt=_load_system_prompt(),
        temperature=0.7,
        max_tokens=4096,
        os_system=cfg.get("os_system", "windows"),
        extra={
            "openrouter_api_key": cfg.get("openrouter_api_key", ""),
        },
    )


def _create_engine(ui: JarvisUI):
    """Create the appropriate engine based on the saved provider config."""
    selected = load_config().get("selected_provider", "gemini")
    pconfig = _build_provider_config()

    provider = create_provider(selected, pconfig)
    prov_name = {"gemini": "Gemini", "ollama": "Ollama", "openrouter": "OpenRouter", "lmstudio": "LM Studio"}.get(selected, selected)
    
    print("\n" + "=" * 50)
    print(f"[JARVIS] 🚀 Initializing Engine: {prov_name}")
    print(f"[JARVIS] 📦 Model Configuration: {pconfig.model}")
    if selected == "gemini" and provider.supports_live_audio:
        print("[JARVIS] 🎙️ Mode: Live Audio (Real-time streaming)")
    else:
        print("[JARVIS] 💬 Mode: Text Chat (with optional Voice Wrapper)")
    print("=" * 50 + "\n")
    
    ui.write_log(f"SYS: Starting with provider: {prov_name} (Model: {pconfig.model})")

    # If Gemini and it supports live audio, use audio mode
    # Otherwise use chat mode
    if selected == "gemini" and provider.supports_live_audio:
        return JarvisLive(ui, provider)

    return JarvisChat(ui, provider)


def _switch_provider(provider_name: str, ui: JarvisUI):
    """Switch provider at runtime — signals engine to stop and restart."""
    save_config({"selected_provider": provider_name})
    prov_name = {"gemini": "Gemini", "ollama": "Ollama", "openrouter": "OpenRouter", "lmstudio": "LM Studio"}.get(provider_name, provider_name)
    
    print("\n" + "*" * 50)
    print(f"[JARVIS] 🔄 Provider switch requested: {prov_name}")
    print("*" * 50 + "\n")
    
    ui.write_log(f"SYS: Switching to {prov_name} provider...")
    _engine_restart.set()
    _engine_stop.set()


# ── Main ────────────────────────────────────────────────────────────

def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    face_path = BASE_DIR / "face.png"
    if not face_path.exists():
        face_path = BASE_DIR / "face.jpg"
    if not face_path.exists():
        face_path = BASE_DIR / "core" / "face.png"
    if not face_path.exists():
        face_path = None
    ui = JarvisUI(face_path)

    # Connect provider switch callback
    ui.on_provider_changed = lambda p: _switch_provider(p, ui)

    def runner():
        ui.wait_for_api_key()
        while True:
            _engine_stop.clear()
            engine = _create_engine(ui)
            try:
                async def run_engine():
                    try:
                        await engine.run()
                    finally:
                        if hasattr(engine, "provider") and hasattr(engine.provider, "close"):
                            await engine.provider.close()
                asyncio.run(run_engine())
            except KeyboardInterrupt:
                print("\n🔴 Shutting down...")
                break
            except Exception as e:
                # Handle asyncio proactor shutdown issues gracefully
                pass

            if not _engine_restart.is_set():
                break

            _engine_restart.clear()
            print("[JARVIS] Engine restarted with new provider.")
            ui.write_log("SYS: Engine restarted with new provider.")

    threading.Thread(target=runner, daemon=True).start()
    ui.root.mainloop()


if __name__ == "__main__":
    setup_logging()
    main()
