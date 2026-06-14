---
name: youtube-downloader
version: 1.0.0
description: Descargar videos, audios y subtítulos de YouTube y otras plataformas con yt-dlp. Usa cuando necesites descargar contenido multimedia para procesarlo, transcribirlo o archivarlo.
tags: [youtube, video, audio, download, yt-dlp, ffmpeg, transcription, media]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# YouTube Downloader Skill

## Cuándo usar esta skill
- Descargar video o audio de YouTube para procesarlo
- Extraer solo el audio para transcripción con Whisper
- Descargar subtítulos de un video
- Archivar o procesar lotes de videos

## Setup

```bash
# Instalar yt-dlp
pip install yt-dlp
# O
brew install yt-dlp      # macOS
winget install yt-dlp    # Windows

# Instalar ffmpeg (necesario para conversión de formatos)
brew install ffmpeg       # macOS
winget install ffmpeg     # Windows
# Ubuntu/Debian: sudo apt install ffmpeg
```

## Comandos básicos

```bash
# Descargar video con la mejor calidad disponible
yt-dlp "https://youtube.com/watch?v=VIDEO_ID"

# Descargar solo audio (MP3)
yt-dlp -x --audio-format mp3 "URL"

# Descargar solo audio (mejor calidad)
yt-dlp -f bestaudio "URL"

# Descargar en calidad específica
yt-dlp -f "best[height<=720]" "URL"   # Máximo 720p
yt-dlp -f "137+140" "URL"             # Video 1080p + audio por separado

# Ver formatos disponibles
yt-dlp -F "URL"

# Descargar subtítulos
yt-dlp --write-sub --sub-lang es "URL"        # Subtítulos en español
yt-dlp --write-auto-sub --sub-lang es "URL"   # Auto-generados

# Solo descargar subtítulos (sin video)
yt-dlp --skip-download --write-auto-sub --sub-lang es "URL"

# Convertir subtítulos a texto plano
yt-dlp --skip-download --write-auto-sub --sub-lang es --convert-subs srt "URL"
```

## Uso en Python

```python
import yt_dlp
from pathlib import Path

def download_audio(url: str, output_dir: str = ".", filename: str = None) -> str:
    """
    Descargar solo el audio de un video
    Retorna la ruta del archivo descargado
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    output_template = str(output_dir / (filename or "%(title)s")) + ".%(ext)s"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_template,
        'quiet': False,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', 'audio')
        return str(output_dir / f"{title}.mp3")


def download_video(
    url: str,
    output_dir: str = ".",
    max_height: int = 1080,
    filename: str = None
) -> str:
    """Descargar video con calidad especificada"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    output_template = str(output_dir / (filename or "%(title)s")) + ".%(ext)s"
    
    ydl_opts = {
        'format': f'best[height<={max_height}]/bestvideo[height<={max_height}]+bestaudio/best',
        'outtmpl': output_template,
        'merge_output_format': 'mp4',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return str(output_dir / f"{info.get('title', 'video')}.mp4")


def get_subtitles(url: str, lang: str = 'es', output_dir: str = ".") -> str | None:
    """Descargar subtítulos como texto"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': [lang],
        'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
        'postprocessors': [{'key': 'FFmpegSubtitlesConvertor', 'format': 'srt'}],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', 'video')
        
        srt_path = output_dir / f"{title}.{lang}.srt"
        if srt_path.exists():
            return str(srt_path)
        
        # Buscar archivo de subtítulos con otro nombre
        for f in output_dir.glob(f"*.{lang}.srt"):
            return str(f)
    
    return None


def get_video_info(url: str) -> dict:
    """Obtener metadatos sin descargar"""
    ydl_opts = {'quiet': True}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            'title': info.get('title'),
            'duration': info.get('duration'),  # segundos
            'uploader': info.get('uploader'),
            'upload_date': info.get('upload_date'),
            'view_count': info.get('view_count'),
            'description': info.get('description', '')[:500],
            'thumbnail': info.get('thumbnail'),
        }
```

## Workflow: Transcribir video con Whisper

```python
import whisper
import yt_dlp

def transcribe_youtube_video(url: str, language: str = "es") -> str:
    """
    Pipeline completo: Descargar audio → Transcribir con Whisper
    """
    # 1. Descargar audio
    print("Descargando audio...")
    audio_path = download_audio(url, output_dir="/tmp/yt-transcribe", filename="audio")
    
    # 2. Transcribir con Whisper
    print("Transcribiendo...")
    model = whisper.load_model("base")  # base, small, medium, large
    result = model.transcribe(audio_path, language=language, fp16=False)
    
    # 3. Formatear salida
    transcript = result['text']
    
    # Con timestamps:
    segments_text = "\n".join([
        f"[{seg['start']:.0f}s] {seg['text'].strip()}"
        for seg in result['segments']
    ])
    
    return transcript


# Uso:
url = "https://youtube.com/watch?v=VIDEO_ID"
transcript = transcribe_youtube_video(url)
print(transcript)
```

## Descargar playlist completa

```bash
# Descargar toda una playlist (solo audio)
yt-dlp -x --audio-format mp3 \
  --output "%(playlist_index)s - %(title)s.%(ext)s" \
  "https://youtube.com/playlist?list=PLxxxxxx"

# Con límite de velocidad para no sobrecargar
yt-dlp --rate-limit 1M "URL"

# Continuar descargas interrumpidas
yt-dlp --continue "URL"

# Descargar solo los N primeros videos
yt-dlp --playlist-end 10 "PLAYLIST_URL"
```

## Plataformas soportadas

yt-dlp soporta más de 1000 sitios, incluyendo:
- YouTube, YouTube Music
- Vimeo
- Twitter/X
- Instagram, Facebook
- TikTok
- Twitch (VODs y clips)
- Dailymotion
- Reddit (videos)
- Soundcloud
- Bandcamp

```bash
# Ver todos los extractores disponibles
yt-dlp --list-extractors | wc -l  # ~1800 extractors
```

## Consideraciones legales

```
⚠️  Verificar los Términos de Servicio de cada plataforma
⚠️  YouTube ToS prohíbe descargas sin permiso expreso
⚠️  Solo descargar contenido con derechos para ello:
    - Videos propios
    - Creative Commons license
    - Dominio público
    - Con permiso explícito del autor
⚠️  No redistribuir contenido descargado sin derechos
```

## Referencias
- [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp)
- [yt-dlp documentación](https://github.com/yt-dlp/yt-dlp#readme)
- [OpenAI Whisper](https://github.com/openai/whisper) — para transcripción
