import asyncio
import os
import re
import logging
import numpy as np
import sounddevice as sd
from array import array

from engine.events import engine_stop

logger = logging.getLogger(__name__)

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
                    logger.warning(f"Speaker device {device} doesn't support {samplerate}Hz. Falling back to device index {fallback}.")
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
                while data and not engine_stop.is_set():
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
        logger.error(f"Play WAV error: {e}")

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
            
        logger.info(f"Transcribing with Whisper.cpp (Local) using {os.path.basename(whisper_m)}...")
        
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
        logger.info("Transcribing with Gemini (Cloud)...")
        api_key = cfg.get("gemini_api_key", "")
        if not api_key:
            raise ValueError("Falta configurar la Gemini API Key para usar la transcripción en la nube. Configúrala en la pestaña GEM de los ajustes.")
            
        from google import genai
        from google.genai import types
        
        client = genai.Client(
            api_key=api_key,
            http_options={"api_version": "v1beta"},
        )
        
        with open(wav_path, "rb") as f:
            audio_bytes = f.read()
            
        try:
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type="audio/wav",
                    ),
                    "Transcribe este archivo de audio con la mayor precisión posible. Responde únicamente con el texto transcrito en el idioma original del hablante, sin añadir explicaciones, traducciones o metadatos."
                ]
            )
            raw_text = response.text.strip() if response.text else ""
            return _clean_whisper_transcript(raw_text)
        except Exception as ge:
            whisper_p = cfg.get("whisper_path", "")
            whisper_m = cfg.get("whisper_model", "")
            if whisper_p and os.path.exists(whisper_p) and whisper_m and os.path.exists(whisper_m):
                logger.warning(f"Gemini Cloud STT failed ({ge}). Falling back to local Whisper...")
                cfg_fallback = dict(cfg)
                cfg_fallback["stt_engine"] = "whisper"
                return await _transcribe_audio(wav_path, cfg_fallback)
            else:
                logger.error(f"Gemini Cloud STT failed and Whisper is not configured: {ge}")
                raise ge


async def _synthesize_with_piper_fallback(text: str, cfg: dict, reason: str) -> bytes | None:
    """Fallback silently to local Piper speech synthesis if Cloud TTS fails."""
    logger.warning(f"Gemini Cloud TTS failed ({reason}). Falling back to local Piper...")
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
            logger.error(f"Piper fallback also failed: {pe}")
    else:
        logger.error("Local Piper is not fully configured/available for fallback.")
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
            
        logger.info(f"Synthesizing in-memory with Piper (Local) using {os.path.basename(piper_m)}...")
        
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
        logger.info("Synthesizing in-memory with Gemini (Cloud)...")
        api_key = cfg.get("gemini_api_key", "")
        if not api_key:
            return await _synthesize_with_piper_fallback(text, cfg, "No Gemini API key configured.")
            
        from google import genai
        from google.genai import types
        
        client = genai.Client(
            api_key=api_key,
            http_options={"api_version": "v1beta"},
        )
        try:
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
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
                return _pcm_to_wav_bytes(audio_bytes, sample_rate=24000)
            return await _synthesize_with_piper_fallback(text, cfg, "No audio data returned")
        except Exception as ge:
            return await _synthesize_with_piper_fallback(text, cfg, str(ge))


# ---------------------------------------------------------------------------
# Voice Activity Detection (ported from Mark-XL main.py)
# ---------------------------------------------------------------------------

class VADBuffer:
    """Energy-based VAD: buffers audio until end of utterance.

    Uses hysteresis thresholds so the detector doesn't flicker:
      - speech starts when RMS > speech_thresh
      - speech ends only when RMS < silence_thresh (half of speech_thresh)
    The gap between the two thresholds prevents mid-sentence cuts on
    natural pauses and quiet consonants.
    """

    def __init__(
        self,
        sample_rate:    int   = 16_000,
        silence_sec:    float = 0.7,    # silence after last word → send to STT
        speech_thresh:  float = 0.008,  # RMS above this = speech
        silence_thresh: float = 0.004,  # RMS below this = silence (hysteresis)
        min_speech_sec: float = 0.3,
        max_speech_sec: float = 30.0,
    ):
        self._sr            = sample_rate
        self._sil_n         = int(silence_sec * sample_rate)
        self._speech_thresh = speech_thresh
        self._sil_thresh    = silence_thresh
        self._min_n         = int(min_speech_sec * sample_rate)
        self._max_n         = int(max_speech_sec * sample_rate)
        self._buf:          list[np.ndarray] = []
        self._in_spch       = False
        self._sil_cnt       = 0

    def process(self, chunk: np.ndarray) -> np.ndarray | None:
        """Feed one audio chunk (float32 mono).

        Returns complete utterance when speech ends, otherwise None.
        """
        rms     = float(np.sqrt(np.mean(chunk ** 2)))
        total_n = sum(len(c) for c in self._buf)

        if rms > self._speech_thresh:
            self._in_spch = True
            self._sil_cnt = 0
            self._buf.append(chunk.copy())
        elif self._in_spch:
            self._buf.append(chunk.copy())
            if rms < self._sil_thresh:
                self._sil_cnt += len(chunk)

            if self._sil_cnt >= self._sil_n or total_n >= self._max_n:
                audio         = np.concatenate(self._buf)
                self._buf     = []
                self._in_spch = False
                self._sil_cnt = 0
                if len(audio) >= self._min_n:
                    return audio
        return None

    def reset(self):
        """Reset VAD state (call when starting a new listening session)."""
        self._buf     = []
        self._in_spch = False
        self._sil_cnt = 0


# ---------------------------------------------------------------------------
# Sentence streaming for TTS (ported from Mark-XL core/llm_client.py)
# ---------------------------------------------------------------------------

# Matches a sentence boundary: [.!?] followed by whitespace, or a blank line.
# Avoids splitting on decimals (3.5) because those have no space after the dot.
_SENTENCE_END_RE = re.compile(r'(?<=[.!?])\s+|(?<=\n)\s*\n')


def split_sentences(text: str) -> list[str]:
    """Split text into complete sentences, preserving sentence-ending punctuation.

    Returns a list of sentences.  Trailing whitespace or incomplete trailing
    text is discarded (it will be appended to the next chunk in streaming).
    """
    if not text:
        return []
    parts = _SENTENCE_END_RE.split(text)
    sentences = []
    buf = ""
    for part in parts:
        buf += part
        # A sentence is complete if it ends with [.!?] followed by whitespace
        # (which was consumed by the split).  We check for sentence-ending
        # punctuation in buf minus trailing whitespace.
        if buf.rstrip() and buf.rstrip()[-1] in ".!?":
            sentences.append(buf.strip())
            buf = ""
    return sentences


def iter_streaming_sentences() -> tuple[list[str], str]:
    """Generator helper for streaming LLM output into sentences.

    Usage:
        buf = ""
        for chunk in llm_stream:
            buf += chunk
            for sent in iter_streaming_sentences(buf):
                yield sent
        # After stream ends, yield remaining buf if any

    Note: this is a placeholder signature showing the pattern.
    The actual integration belongs in the provider streaming code.
    """
    # This function documents the pattern; actual usage is in providers
    pass
