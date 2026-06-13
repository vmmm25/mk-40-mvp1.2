"""
Text-to-Speech engines for MARK XL (ported from Mark-XL core/tts.py).

EdgeTTS     – free Microsoft TTS (internet required, no API key)
Kokoro      – fully offline neural TTS (~330 MB model)
ElevenLabs  – cloud API (API key required, best quality)
Piper       – local Piper TTS (lightweight, existing engine)
Gemini      – cloud Gemini TTS (existing engine)

Usage:
    player = create_tts_player(config)
    player.speak("Hello world")  # blocking — call from background thread
"""
from __future__ import annotations

import os
import queue as _queue
import threading
from typing import Callable, Optional

import numpy as np
import sounddevice as sd


# Silence verbose libs + block heavy unused backends
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


# ---------------------------------------------------------------------------
# Audio playback helpers
# ---------------------------------------------------------------------------

def _to_numpy(samples) -> np.ndarray:
    """Convert samples to float32 numpy array.

    Handles both numpy arrays and PyTorch tensors (Kokoro >= 0.9).
    Falls back via .tolist() when PyTorch/numpy version mismatch occurs.
    """
    if hasattr(samples, "detach"):  # PyTorch tensor
        t = samples.detach().cpu().float()
        try:
            return t.numpy()  # fast path
        except RuntimeError:
            return np.asarray(t.tolist(), dtype=np.float32)
    return np.asarray(samples, dtype=np.float32)


def _compress_silence(
    arr: np.ndarray,
    sample_rate: int = 24_000,
    max_silence_ms: int = 500,
    threshold: float = 0.003,
) -> np.ndarray:
    """Shorten long punctuation pauses (1-2 s → ≤500 ms).

    Conservative settings preserve natural prosody; only trims extreme pauses
    that make Kokoro/EdgeTTS sound unnaturally slow between sentences.
    """
    max_samp = int(max_silence_ms * sample_rate / 1000)
    frame_len = 240  # ~10 ms at 24 kHz
    out: list[np.ndarray] = []
    silent_acc = 0

    for i in range(0, len(arr), frame_len):
        chunk = arr[i: i + frame_len]
        if np.sqrt(np.mean(chunk ** 2) + 1e-12) < threshold:
            silent_acc += len(chunk)
            if silent_acc <= max_samp:
                out.append(chunk)
        else:
            silent_acc = 0
            out.append(chunk)

    return np.concatenate(out) if out else arr


def _play_np(samples, sample_rate: int) -> None:
    """Play float32 mono/stereo audio via sounddevice."""
    sd.play(_to_numpy(samples), sample_rate)
    sd.wait()


def _play_audio_bytes(audio_bytes: bytes) -> None:
    """Decode MP3/WAV/OGG bytes and play via sounddevice (miniaudio)."""
    import miniaudio
    decoded = miniaudio.decode(
        audio_bytes,
        output_format=miniaudio.SampleFormat.FLOAT32,
        nchannels=1,
    )
    samples = np.array(decoded.samples, dtype=np.float32)
    sd.play(samples, decoded.sample_rate)
    sd.wait()


# ---------------------------------------------------------------------------
# Engines
# ---------------------------------------------------------------------------

class EdgeTTSEngine:
    """Microsoft EdgeTTS – free, requires internet."""

    def __init__(self, voice: str = "en-US-GuyNeural"):
        self.voice = voice

    def speak(self, text: str) -> None:
        import asyncio
        loop = asyncio.new_event_loop()
        try:
            audio_bytes = loop.run_until_complete(self._synth(text))
        finally:
            loop.close()
        if audio_bytes:
            # Apply silence compression before playback
            import miniaudio
            decoded = miniaudio.decode(
                audio_bytes,
                output_format=miniaudio.SampleFormat.FLOAT32,
                nchannels=1,
            )
            samples = np.array(decoded.samples, dtype=np.float32)
            samples = _compress_silence(samples, decoded.sample_rate)
            sd.play(samples, decoded.sample_rate)
            sd.wait()

    async def _synth(self, text: str) -> bytes:
        import edge_tts
        comm = edge_tts.Communicate(text, self.voice)
        buf = bytearray()
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                buf.extend(chunk["data"])
        return bytes(buf)


# ---------------------------------------------------------------------------
# Kokoro import helper
# ---------------------------------------------------------------------------

_KOKORO_COMPAT_ERRORS = ("AlbertModel", "AutoModel", "cannot import name")


def _import_kokoro_pipeline():
    """Import KPipeline, auto-upgrading kokoro if version mismatch."""
    import sys

    def _try_import():
        from kokoro import KPipeline  # noqa: PLC0415
        return KPipeline

    try:
        return _try_import()
    except Exception as first_err:
        err_msg = str(first_err)
        if not any(marker in err_msg for marker in _KOKORO_COMPAT_ERRORS):
            raise RuntimeError(
                f"Kokoro import failed: {first_err}\n"
                "Run: pip install kokoro>=0.9 soundfile"
            ) from first_err

        print("[TTS] Kokoro/transformers version mismatch — upgrading kokoro…")
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "kokoro>=0.9",
             "--upgrade", "--quiet", "--disable-pip-version-check"],
            capture_output=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.decode(errors="replace").strip()
            raise RuntimeError(
                f"Kokoro auto-upgrade failed: {stderr[:200]}\n"
                "Run manually: pip install kokoro>=0.9 soundfile"
            ) from first_err

        stale = [k for k in sys.modules if k == "kokoro" or k.startswith("kokoro.")]
        for key in stale:
            del sys.modules[key]

        print("[TTS] Kokoro upgraded — retrying import…")
        try:
            return _try_import()
        except Exception as retry_err:
            raise RuntimeError(
                f"Kokoro still broken after upgrade: {retry_err}\n"
                "Run manually: pip install --upgrade kokoro transformers"
            ) from retry_err


_KOKORO_LANG_CODES = {
    "a": "a", "b": "b", "j": "j", "z": "z", "s": "s",
    "f": "f", "h": "h", "i": "i", "p": "p", "r": "r", "e": "e",
}


class KokoroTTSEngine:
    """Fully offline Kokoro neural TTS.

    Model (~330 MB) downloads from HuggingFace on first use,
    then caches locally.  Warmup compiles PyTorch JIT graph.
    """

    def __init__(self, voice: str = "af_heart", speed: float = 1.0):
        self.voice = voice
        self.speed = speed
        self._pipeline = None
        self._lock = threading.Lock()
        # Init runs in background thread (called from factory or worker)
        self._init()

    @property
    def _lang_code(self) -> str:
        prefix = self.voice[0].lower() if self.voice else "a"
        return _KOKORO_LANG_CODES.get(prefix, "a")

    def _init(self) -> None:
        if self._pipeline is not None:
            return

        lang = self._lang_code

        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            if device == "cpu":
                n_threads = max(1, min(4, (os.cpu_count() or 4) // 2))
                try:
                    torch.set_num_threads(n_threads)
                    torch.set_num_interop_threads(2)
                except RuntimeError:
                    pass
        except Exception:
            device = "cpu"

        print(f"[TTS] Kokoro — loading (lang='{lang}', device='{device}')…")
        KPipeline = _import_kokoro_pipeline()

        def _create_pipeline():
            try:
                return KPipeline(lang_code=lang, device=device)
            except TypeError:
                return KPipeline(lang_code=lang)

        try:
            self._pipeline = _create_pipeline()
        except Exception as _first_err:
            _e = str(_first_err).lower()
            if any(k in _e for k in ("offline", "not found", "cache", "localentry", "does not exist")):
                print("[TTS] Kokoro model not cached — downloading (first run)…")
                os.environ.pop("HF_HUB_OFFLINE", None)
                os.environ.pop("TRANSFORMERS_OFFLINE", None)
                os.environ.pop("HF_DATASETS_OFFLINE", None)
                self._pipeline = _create_pipeline()
            else:
                raise

        # Warmup: compile PyTorch JIT graph
        print("[TTS] Kokoro compiling (first-time only)…")
        try:
            for _ in self._pipeline("hello", voice=self.voice, speed=self.speed):
                pass
            print("[TTS] Kokoro ready.")
        except Exception as e:
            print(f"[TTS] Kokoro warmup warning: {e}")

    def speak(self, text: str) -> None:
        with self._lock:
            if self._pipeline is None:
                self._init()

        # Producer/consumer for concurrent synth + playback
        audio_q: "_queue.Queue[np.ndarray | None]" = _queue.Queue(maxsize=4)
        synth_error: list[Exception] = []

        def _synth():
            try:
                for _, _, audio in self._pipeline(
                    text, voice=self.voice, speed=self.speed
                ):
                    if audio is not None:
                        arr = _to_numpy(audio)
                        arr = _compress_silence(arr)
                        if arr.size > 0:
                            audio_q.put(arr)
            except Exception as exc:
                synth_error.append(exc)
            finally:
                audio_q.put(None)

        synth_thread = threading.Thread(target=_synth, daemon=True)
        synth_thread.start()

        while True:
            arr = audio_q.get()
            if arr is None:
                break
            _play_np(arr, 24000)

        synth_thread.join()
        if synth_error:
            raise synth_error[0]


class ElevenLabsTTSEngine:
    """ElevenLabs cloud TTS – API key required."""

    def __init__(self, api_key: str, voice_id: str = "pNInz6obpgDQGcFmaJgB"):
        self.api_key = api_key
        self.voice_id = voice_id

    def speak(self, text: str) -> None:
        import requests
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }
        resp = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}",
            json=payload, headers=headers, timeout=30,
        )
        resp.raise_for_status()
        _play_audio_bytes(resp.content)


# ---------------------------------------------------------------------------
# Thread-safe player wrapper
# ---------------------------------------------------------------------------

class TTSPlayer:
    """Wraps any engine.  Blocking speak() meant for background thread."""

    def __init__(self, engine):
        self._engine = engine
        self._playing = False
        self._lock = threading.Lock()

    @property
    def is_playing(self) -> bool:
        return self._playing

    def speak(
        self,
        text: str,
        on_start: Optional[Callable] = None,
        on_done: Optional[Callable] = None,
    ) -> None:
        """Synthesise and play text. BLOCKING – call from dedicated thread."""
        try:
            with self._lock:
                self._playing = True
            if on_start:
                on_start()
            self._engine.speak(text)
        except Exception as e:
            print(f"[TTS] Error: {e}")
        finally:
            with self._lock:
                self._playing = False
            if on_done:
                on_done()

    def stop(self) -> None:
        sd.stop()
        with self._lock:
            self._playing = False


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_tts_player(config: dict) -> TTSPlayer:
    """Create a TTSPlayer from config dict.

    Config keys used:
        tts_engine       — "edgetts" | "kokoro" | "elevenlabs" | "piper" | "gemini"
        tts_voice        — voice name/id
        tts_speed        — speed multiplier (Kokoro)
        elevenlabs_api_key — API key for ElevenLabs
    """
    engine_name = config.get("tts_engine", "edgetts").lower()

    if engine_name == "kokoro":
        voice = config.get("tts_voice", "af_heart")
        speed = float(config.get("tts_speed", 1.0))
        engine = KokoroTTSEngine(voice=voice, speed=speed)

    elif engine_name == "elevenlabs":
        api_key = config.get("elevenlabs_api_key", "")
        voice_id = config.get("tts_voice", "pNInz6obpgDQGcFmaJgB")
        engine = ElevenLabsTTSEngine(api_key=api_key, voice_id=voice_id)

    elif engine_name == "piper":
        # Wrap existing Piper engine — adapt config keys to PiperTTSProvider
        from core.tts_piper import PiperTTSProvider  # noqa: PLC0415
        try:
            engine = PiperTTSProvider()
        except FileNotFoundError:
            print("[TTS] Piper not configured — falling back to EdgeTTS")
            engine = EdgeTTSEngine()

    elif engine_name == "gemini":
        # Wrap Gemini TTS from engine/audio
        # (Gemini TTS is handled via _synthesize_speech_in_memory)
        print("[TTS] Gemini TTS — use engine.audio._synthesize_speech_in_memory directly")
        engine = EdgeTTSEngine()  # fallback

    else:  # edgetts (default)
        voice = config.get("tts_voice", "en-US-GuyNeural")
        engine = EdgeTTSEngine(voice=voice)

    return TTSPlayer(engine)
