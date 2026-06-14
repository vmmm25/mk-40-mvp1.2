---
name: faster-whisper
version: 1.0.0
description: Transcripción de audio/voz a texto localmente con faster-whisper, 4-6x más rápido que OpenAI Whisper con la misma precisión. Usa cuando necesites transcribir audio, reuniones, notas de voz o extraer texto de videos.
tags: [whisper, speech-to-text, transcription, audio, local, faster-whisper, gpu]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Faster Whisper — Transcripción Local

## Instalación

```bash
# CPU
pip install faster-whisper

# Con soporte GPU (CUDA)
pip install faster-whisper
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
```

## Modelos disponibles

| Modelo | Tamaño | VRAM | Velocidad | Precisión |
|--------|--------|------|-----------|-----------|
| `tiny` | 75MB | ~1GB | ~32x | Baja |
| `tiny.en` | 75MB | ~1GB | ~32x | Media (solo inglés) |
| `base` | 142MB | ~1GB | ~16x | Media |
| `small` | 466MB | ~2GB | ~6x | Buena |
| `medium` | 1.5GB | ~5GB | ~2x | Muy buena |
| `large-v3` | 3GB | ~10GB | 1x | Excelente |
| `distil-large-v3` | 1.5GB | ~5GB | ~6x | Casi igual que large |

## Transcripción básica

```python
from faster_whisper import WhisperModel

# Cargar modelo (se descarga automáticamente la primera vez)
model = WhisperModel("small", device="cpu")  # O "cuda" para GPU

def transcribe(audio_path: str, language: str = None) -> str:
    """
    Transcribir un archivo de audio.
    
    Formatos soportados: mp3, wav, m4a, ogg, flac, mp4, webm, etc.
    """
    segments, info = model.transcribe(
        audio_path,
        language=language,      # None = auto-detect
        beam_size=5,
        vad_filter=True,        # Filtrar silencios (mejora velocidad y precisión)
        vad_parameters={"min_silence_duration_ms": 500},
    )
    
    return " ".join(segment.text.strip() for segment in segments)


# Transcripción básica
text = transcribe("meeting.mp3")
print(text)

# Forzar idioma (más rápido)
text_es = transcribe("nota-de-voz.m4a", language="es")
```

## Transcripción con timestamps y palabras

```python
def transcribe_with_timestamps(audio_path: str, language: str = None) -> list:
    """
    Transcribir con timestamps por segmento.
    Útil para subtítulos, búsqueda por tiempo, etc.
    """
    segments, info = model.transcribe(
        audio_path,
        language=language,
        word_timestamps=True,   # Timestamps por palabra
        beam_size=5,
        vad_filter=True,
    )
    
    result = []
    for segment in segments:
        result.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip(),
            "words": [
                {"word": w.word, "start": round(w.start, 2), "end": round(w.end, 2)}
                for w in (segment.words or [])
            ]
        })
    
    return result


def to_srt(segments: list) -> str:
    """Convertir segmentos a formato SRT (subtítulos)"""
    def format_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    
    lines = []
    for i, seg in enumerate(segments, 1):
        lines.append(str(i))
        lines.append(f"{format_time(seg['start'])} --> {format_time(seg['end'])}")
        lines.append(seg["text"])
        lines.append("")
    
    return "\n".join(lines)


def to_vtt(segments: list) -> str:
    """Convertir a formato WebVTT para el navegador"""
    def fmt(s: float) -> str:
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sec = int(s % 60)
        ms = int((s % 1) * 1000)
        return f"{h:02d}:{m:02d}:{sec:02d}.{ms:03d}"
    
    lines = ["WEBVTT", ""]
    for seg in segments:
        lines.append(f"{fmt(seg['start'])} --> {fmt(seg['end'])}")
        lines.append(seg["text"])
        lines.append("")
    
    return "\n".join(lines)
```

## Grabar y transcribir en tiempo real

```python
# pip install sounddevice soundfile
import sounddevice as sd
import soundfile as sf
import tempfile
import numpy as np

def record_and_transcribe(duration_seconds: int = 10, sample_rate: int = 16000) -> str:
    """Grabar micrófono y transcribir inmediatamente"""
    print(f"🎙️ Grabando {duration_seconds} segundos...")
    audio = sd.rec(
        int(duration_seconds * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32"
    )
    sd.wait()
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, audio, sample_rate)
        text = transcribe(tmp.name, language="es")
    
    return text


# Transcripción continua (streaming)
def live_transcribe():
    """Transcripción en tiempo real con chunks de 5 segundos"""
    print("🎙️ Escuchando... (Ctrl+C para parar)")
    buffer = []
    sample_rate = 16000
    chunk_duration = 5
    
    def callback(indata, frames, time, status):
        buffer.extend(indata[:, 0])
        if len(buffer) >= sample_rate * chunk_duration:
            audio_chunk = np.array(buffer[:sample_rate * chunk_duration])
            buffer.clear()
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                sf.write(tmp.name, audio_chunk, sample_rate)
                text = transcribe(tmp.name, language="es")
                if text.strip():
                    print(f"📝 {text}")
    
    with sd.InputStream(callback=callback, samplerate=sample_rate, channels=1):
        try:
            while True:
                sd.sleep(1000)
        except KeyboardInterrupt:
            print("\n✅ Transcripción finalizada")
```

## Extraer audio de video y transcribir

```python
# pip install yt-dlp  (o ffmpeg)
import subprocess

def extract_audio_from_video(video_path: str, output_path: str = None) -> str:
    """Extraer audio de un video con ffmpeg"""
    if not output_path:
        output_path = video_path.rsplit(".", 1)[0] + "_audio.wav"
    
    subprocess.run([
        "ffmpeg", "-i", video_path,
        "-ar", "16000",   # 16kHz óptimo para Whisper
        "-ac", "1",       # Mono
        "-y", output_path
    ], check=True, capture_output=True)
    
    return output_path


def transcribe_video(video_path: str, language: str = None) -> dict:
    """Pipeline completo: video → audio → transcripción"""
    audio_path = extract_audio_from_video(video_path)
    segments = transcribe_with_timestamps(audio_path, language)
    
    return {
        "text": " ".join(s["text"] for s in segments),
        "srt": to_srt(segments),
        "segments": segments,
    }
```

## Scripts de línea de comandos

```bash
# Transcribir archivo directamente
python -c "
from faster_whisper import WhisperModel
model = WhisperModel('small', device='cpu')
segs, _ = model.transcribe('audio.mp3', language='es', vad_filter=True)
print(''.join(s.text for s in segs))
"

# Script reutilizable: transcribe.py
# python transcribe.py audio.mp3 --language es --output transcript.txt
```

## Referencias
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — Repositorio oficial
- [Distil-Whisper](https://github.com/huggingface/distil-whisper) — Modelos destilados, muy rápidos
- [ffmpeg](https://ffmpeg.org/) — Para extraer/convertir audio
- [Whisper original](https://github.com/openai/whisper) — Modelo base de OpenAI
