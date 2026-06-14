---
name: voxtral-transcription
version: 1.0.0
description: >
  Voice-to-text transcription using Mistral AI's Voxtral Transcribe 2. Open-source (Apache 2.0),
  runs locally on phones and laptops with latency under 200ms for real-time translation.
  Supports 13 languages. Variants include Voxtral Mini Transcribe V2 ($0.003/min cloud) and
  Voxtral Realtime (open-source local). Integrates with faster-whisper for fallback. Use cases:
  meeting transcription, dictation, accessibility, and multilingual communication.
tags:
  - voice-to-text
  - transcription
  - mistral-ai
  - voxtral
  - speech-recognition
  - real-time
  - multilingual
  - accessibility
  - open-source
  - productivity
author: garri333
license: MIT
source: Mistral AI Voxtral Transcribe 2 (launched Feb 5, 2026) — Apache 2.0
compatible:
  - claude-code
  - claude-desktop
  - skill-md-standard
---

# voxtral-transcription

Voice-to-text transcription using Mistral AI's Voxtral Transcribe 2. Open-source, runs locally with sub-200ms latency. Supports 13 languages, real-time streaming, and integrates with faster-whisper for fallback.

---

## When to Activate

Activate this skill when the user:

- Wants to **transcribe audio or video** files to text
- Needs **real-time speech-to-text** for live transcription
- Asks about **meeting transcription** or recording processing
- Wants to set up **voice dictation** for hands-free coding or writing
- Needs **multilingual transcription** or translation
- Asks about **Voxtral**, **Mistral AI speech**, or **open-source ASR**
- Wants to run **speech recognition locally** without cloud APIs
- Needs **accessibility features** for hearing-impaired users
- Asks about **faster-whisper** alternatives or fallback strategies
- Wants to integrate transcription into an **automation pipeline**
- Uses keywords: `transcribe`, `voice to text`, `speech recognition`, `voxtral`, `dictation`, `meeting notes`, `real-time transcription`

---

## Step-by-Step Instructions

### 1. Voxtral Model Family Overview

```
VOXTRAL TRANSCRIBE 2 — MODEL FAMILY
══════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│                  VOXTRAL TRANSCRIBE 2                       │
│            Released: February 5, 2026                       │
│            License: Apache 2.0 (open-source)               │
│            Languages: 13                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
┌────────▼───────┐ ┌───▼──────────┐ ┌▼───────────────────┐
│ Voxtral Mini   │ │ Voxtral      │ │ Voxtral Realtime   │
│ Transcribe V2  │ │ Transcribe 2 │ │                    │
│                │ │ (Full)       │ │ • Open-source      │
│ • Cloud API    │ │              │ │ • Local execution  │
│ • $0.003/min   │ │ • Highest    │ │ • Sub-200ms latency│
│ • Low latency  │ │   accuracy   │ │ • Streaming mode   │
│ • Lightweight  │ │ • 13 langs   │ │ • Phone/laptop     │
│ • Mobile-ready │ │ • Batch +    │ │ • No cloud needed  │
│                │ │   streaming  │ │                    │
└────────────────┘ └──────────────┘ └────────────────────┘

SUPPORTED LANGUAGES (13):
  English, French, Spanish, German, Italian, Portuguese,
  Dutch, Russian, Chinese (Mandarin), Japanese, Korean,
  Arabic, Hindi

PERFORMANCE BENCHMARKS:
  • Word Error Rate (WER): 4.2% (English) — state-of-the-art
  • Latency (Realtime): < 200ms end-to-end
  • Latency (Cloud Mini): ~500ms per request
  • Throughput: 10x real-time on modern GPU
  • CPU inference: ~3x real-time (laptop, no GPU)
══════════════════════════════════════════════════════════════
```

---

### 2. Installation & Setup

#### Local Installation (Voxtral Realtime)

```bash
# Option A: pip install (recommended)
pip install voxtral-transcribe

# Option B: From source
git clone https://github.com/mistralai/voxtral-transcribe.git
cd voxtral-transcribe
pip install -e .

# Download model weights (auto-downloaded on first use)
voxtral download --model voxtral-realtime-v2

# Verify installation
voxtral --version
voxtral test --microphone
```

#### System Requirements

```yaml
requirements:
  minimum:
    cpu: "4 cores (x86_64 or ARM64)"
    ram: "4 GB"
    storage: "2 GB (model weights)"
    os: "Linux, macOS, Windows 10+"
    python: "3.9+"

  recommended:
    cpu: "8+ cores"
    ram: "8 GB"
    gpu: "NVIDIA GPU with 4GB+ VRAM (CUDA 11.8+)"
    storage: "5 GB"

  mobile:
    platform: "iOS 16+ / Android 12+"
    ram: "3 GB minimum"
    model: "Voxtral Mini (quantized INT8)"
```

#### Cloud API Setup (Voxtral Mini)

```python
# Install Mistral AI SDK
pip install mistralai

# Configure API key
import os
os.environ["MISTRAL_API_KEY"] = "your-api-key-here"

# Or use .env file
# MISTRAL_API_KEY=your-api-key-here
```

---

### 3. Basic Transcription

#### File Transcription

```python
from voxtral import VoxtralTranscriber

# Initialize transcriber
transcriber = VoxtralTranscriber(
    model="voxtral-realtime-v2",  # or "voxtral-mini-v2"
    language="auto",               # auto-detect or specify: "en", "es", "fr"
    device="auto"                  # "cpu", "cuda", "mps" (Apple Silicon)
)

# Transcribe audio file
result = transcriber.transcribe("meeting_recording.mp3")

# Access results
print(result.text)                # Full transcription text
print(result.language)            # Detected language
print(result.duration)            # Audio duration in seconds
print(result.confidence)          # Overall confidence score (0-1)

# Word-level timestamps
for word in result.words:
    print(f"[{word.start:.2f}s - {word.end:.2f}s] {word.text} ({word.confidence:.2f})")

# Segment-level output
for segment in result.segments:
    print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}")
```

#### Supported Audio Formats

```yaml
supported_formats:
  audio:
    - mp3
    - wav
    - flac
    - ogg
    - m4a
    - aac
    - wma
    - webm
  video:
    - mp4 (audio track extracted)
    - mkv (audio track extracted)
    - avi (audio track extracted)
  max_file_size: "500 MB (local) / 25 MB (cloud API)"
  sample_rates: "8kHz - 48kHz (auto-resampled to 16kHz)"
```

---

### 4. Real-Time Streaming Transcription

```python
from voxtral import VoxtralStreamer

# Initialize real-time streamer
streamer = VoxtralStreamer(
    model="voxtral-realtime-v2",
    language="auto",
    device="auto",
    vad_enabled=True,          # Voice Activity Detection
    vad_threshold=0.5,         # Silence detection sensitivity
    chunk_duration_ms=100,     # Audio chunk size
    beam_size=5,               # Beam search width (accuracy vs speed)
    partial_results=True       # Emit partial transcriptions
)

# Stream from microphone
async def live_transcription():
    async for result in streamer.stream_microphone():
        if result.is_partial:
            # Partial result (still processing)
            print(f"\r⏳ {result.text}", end="", flush=True)
        else:
            # Final result (segment complete)
            print(f"\n✅ [{result.start:.1f}s] {result.text}")

# Stream from audio stream (e.g., WebSocket)
async def stream_from_websocket(ws):
    async for audio_chunk in ws:
        results = await streamer.process_chunk(audio_chunk)
        for result in results:
            yield result

# Stream with speaker diarization
async def transcribe_with_speakers():
    async for result in streamer.stream_microphone(diarize=True):
        print(f"[Speaker {result.speaker_id}] {result.text}")
```

---

### 5. Cloud API Usage (Voxtral Mini)

```python
from mistralai import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# Transcribe via cloud API
response = client.audio.transcribe(
    model="voxtral-mini-transcribe-v2",
    file=open("recording.mp3", "rb"),
    language="auto",
    response_format="verbose_json",  # or "text", "srt", "vtt"
    temperature=0.0,
    timestamp_granularity="word"     # or "segment"
)

# Access response
print(response.text)
print(f"Duration: {response.duration}s")
print(f"Language: {response.language}")
print(f"Cost: ${response.duration / 60 * 0.003:.4f}")

# Generate subtitles (SRT format)
srt_response = client.audio.transcribe(
    model="voxtral-mini-transcribe-v2",
    file=open("video.mp4", "rb"),
    response_format="srt"
)
with open("subtitles.srt", "w") as f:
    f.write(srt_response.text)
```

**Pricing (Cloud API)**:

```
VOXTRAL CLOUD API PRICING
══════════════════════════════════════════════════════════════
Model                    │ Price/minute │ Price/hour │ Free tier
─────────────────────────┼──────────────┼────────────┼──────────
Voxtral Mini Transcribe  │ $0.003       │ $0.18      │ 60 min/mo
Voxtral Transcribe 2     │ $0.008       │ $0.48      │ 30 min/mo
Voxtral Realtime (local) │ Free         │ Free       │ Unlimited
══════════════════════════════════════════════════════════════
```

---

### 6. faster-whisper Fallback Integration

```python
from voxtral import VoxtralTranscriber
from voxtral.fallback import FallbackChain

# Configure fallback chain
transcriber = FallbackChain([
    {
        "engine": "voxtral-realtime-v2",
        "priority": 1,
        "timeout": 30,
        "conditions": {
            "max_file_size_mb": 500,
            "languages": "all"
        }
    },
    {
        "engine": "faster-whisper",
        "priority": 2,
        "model": "large-v3",
        "timeout": 60,
        "conditions": {
            "fallback_on": ["timeout", "error", "low_confidence"],
            "min_confidence": 0.7
        }
    }
])

# Transcribe with automatic fallback
result = transcriber.transcribe("audio.mp3")
print(f"Engine used: {result.engine}")  # voxtral-realtime-v2 or faster-whisper
print(f"Text: {result.text}")
print(f"Confidence: {result.confidence}")

# Manual faster-whisper usage
from faster_whisper import WhisperModel

whisper = WhisperModel("large-v3", device="cuda", compute_type="float16")
segments, info = whisper.transcribe("audio.mp3", beam_size=5)

for segment in segments:
    print(f"[{segment.start:.2f}s → {segment.end:.2f}s] {segment.text}")
```

---

### 7. Use Cases & Integration Patterns

#### Meeting Transcription Pipeline

```python
from voxtral import VoxtralTranscriber
from datetime import datetime

def transcribe_meeting(audio_path, output_dir="./meetings"):
    transcriber = VoxtralTranscriber(
        model="voxtral-realtime-v2",
        language="auto",
        diarize=True,         # Speaker identification
        punctuate=True,        # Auto-punctuation
        paragraphs=True        # Auto-paragraph segmentation
    )

    result = transcriber.transcribe(audio_path)

    # Generate meeting notes
    meeting_notes = f"""# Meeting Transcription
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Duration**: {result.duration / 60:.1f} minutes
**Language**: {result.language}
**Speakers**: {len(set(s.speaker_id for s in result.segments))}

---

## Transcript

"""
    for segment in result.segments:
        speaker = f"**Speaker {segment.speaker_id}**"
        timestamp = f"[{segment.start:.1f}s]"
        meeting_notes += f"{timestamp} {speaker}: {segment.text}\n\n"

    # Save
    output_path = f"{output_dir}/meeting_{datetime.now():%Y%m%d_%H%M}.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(meeting_notes)

    return output_path
```

#### Voice Dictation for Coding

```python
import asyncio
from voxtral import VoxtralStreamer

async def code_dictation():
    """Real-time voice dictation optimized for code."""
    streamer = VoxtralStreamer(
        model="voxtral-realtime-v2",
        language="en",
        vocabulary_boost=[
            # Boost recognition of programming terms
            "function", "const", "let", "var", "async", "await",
            "import", "export", "return", "class", "interface",
            "typescript", "javascript", "python", "react", "vue",
            "API", "endpoint", "middleware", "database", "query",
            "git commit", "git push", "pull request", "merge"
        ],
        formatting={
            "numbers_to_digits": True,    # "forty two" → "42"
            "code_formatting": True,       # Recognize code patterns
            "punctuation_commands": True    # "period" → ".", "new line" → "\n"
        }
    )

    print("🎤 Code dictation active. Say 'stop dictation' to end.\n")

    async for result in streamer.stream_microphone():
        if result.text.strip().lower() == "stop dictation":
            break
        if not result.is_partial:
            print(result.text, end=" ", flush=True)
```

#### Accessibility: Live Captions

```python
from voxtral import VoxtralStreamer
import websockets
import json

async def live_caption_server(host="localhost", port=8765):
    """WebSocket server for real-time captions."""
    streamer = VoxtralStreamer(
        model="voxtral-realtime-v2",
        language="auto",
        partial_results=True
    )

    async def handle_client(websocket):
        async for result in streamer.stream_microphone():
            caption = {
                "type": "partial" if result.is_partial else "final",
                "text": result.text,
                "language": result.language,
                "confidence": result.confidence,
                "timestamp": result.start
            }
            await websocket.send(json.dumps(caption))

    async with websockets.serve(handle_client, host, port):
        print(f"🔴 Live caption server running on ws://{host}:{port}")
        await asyncio.Future()  # Run forever
```

#### Multilingual Communication

```python
from voxtral import VoxtralTranscriber

def transcribe_multilingual(audio_path, target_language="en"):
    """Transcribe audio and translate to target language."""
    transcriber = VoxtralTranscriber(
        model="voxtral-realtime-v2",
        language="auto",
        translate_to=target_language  # Auto-translate during transcription
    )

    result = transcriber.transcribe(audio_path)

    return {
        "original_language": result.source_language,
        "target_language": target_language,
        "original_text": result.original_text,
        "translated_text": result.text,
        "confidence": result.confidence
    }

# Example: Transcribe Spanish audio to English
output = transcribe_multilingual("spanish_meeting.mp3", target_language="en")
print(f"[{output['original_language']}→{output['target_language']}]")
print(f"Original: {output['original_text'][:100]}...")
print(f"Translated: {output['translated_text'][:100]}...")
```

---

### 8. Speech-to-Speech Translation Roadmap (End of 2026)

```
VOXTRAL ROADMAP — 2026
══════════════════════════════════════════════════════════════

Q1 2026 (✅ Released):
  • Voxtral Transcribe 2 — Feb 5, 2026
  • Voxtral Mini Transcribe V2 — Cloud API
  • Voxtral Realtime — Open-source local model
  • 13 language support

Q2 2026 (Planned):
  • Speaker diarization improvements
  • Code-aware transcription mode
  • Mobile SDK (iOS/Android)
  • 8 additional languages

Q3 2026 (Planned):
  • Voxtral Transcribe 3 — Next-gen accuracy
  • On-device quantized models (INT4)
  • Custom vocabulary fine-tuning
  • Enterprise API tier

Q4 2026 (Roadmap):
  • 🚀 Speech-to-Speech Translation
    - Direct audio-to-audio translation
    - No intermediate text step
    - Sub-500ms latency
    - Voice cloning for natural output
    - Initial: EN↔FR, EN↔ES, EN↔DE
  • Real-time meeting translation
  • Voxtral Realtime V3

══════════════════════════════════════════════════════════════
```

---

## Best Practices

1. **Choose the right variant**: Use Realtime for local/privacy-sensitive, Mini for low-cost cloud, Full for highest accuracy
2. **Enable VAD (Voice Activity Detection)**: Reduces processing of silence and background noise
3. **Set language explicitly when known**: Auto-detect adds latency; specify language for faster results
4. **Use vocabulary boosting**: Add domain-specific terms to improve recognition accuracy
5. **Implement fallback chains**: Always have a secondary engine (faster-whisper) for reliability
6. **Stream, don't batch**: For real-time use cases, use streaming mode for sub-200ms latency
7. **Handle audio quality**: Pre-process noisy audio with noise reduction before transcription
8. **Respect privacy**: Local transcription (Voxtral Realtime) keeps all audio data on-device
9. **Monitor confidence scores**: Flag low-confidence segments for human review
10. **Cache results**: Store transcriptions to avoid re-processing the same audio

---

## Examples

### Example 1: Transcribe a Meeting Recording

**User**: "Transcribe yesterday's meeting recording."

**Agent**:
1. Locates the audio file (e.g., `meeting_2026-02-21.mp3`)
2. Initializes Voxtral with speaker diarization
3. Produces a formatted transcript:

```markdown
# Meeting Transcript — February 21, 2026
**Duration**: 47 minutes | **Speakers**: 4 | **Language**: English

[0:00] **Speaker 1**: Good morning everyone. Let's start with the sprint review.
[0:05] **Speaker 2**: Sure. We completed 18 of 21 story points this sprint.
[0:12] **Speaker 1**: Great progress. What about the authentication module?
[0:15] **Speaker 3**: It's done. We implemented JWT with refresh tokens...
```

### Example 2: Set Up Real-Time Dictation

**User**: "I want to dictate code using my voice."

**Agent**:
1. Installs Voxtral Realtime locally
2. Configures code-aware vocabulary boosting
3. Starts streaming transcription with code formatting:

```
🎤 Code dictation active (English, Voxtral Realtime V2)
   Latency: ~180ms | Device: CPU (Apple M2)

You say: "create a function called process order that takes an order object and returns a promise"

Output: function processOrder(order) { return new Promise() }

You say: "add error handling with try catch"

Output: try { } catch (error) { }
```

### Example 3: Batch Transcribe Multiple Files

**User**: "Transcribe all MP3 files in the recordings/ folder."

**Agent**:

```python
import glob
from voxtral import VoxtralTranscriber

transcriber = VoxtralTranscriber(model="voxtral-realtime-v2")

files = glob.glob("recordings/*.mp3")
print(f"Found {len(files)} files to transcribe.\n")

for i, filepath in enumerate(files, 1):
    print(f"[{i}/{len(files)}] Transcribing {filepath}...")
    result = transcriber.transcribe(filepath)
    output_path = filepath.replace(".mp3", ".txt")
    with open(output_path, "w") as f:
        f.write(result.text)
    print(f"  ✅ Done ({result.duration:.0f}s audio, {len(result.text)} chars)")

print(f"\n✅ All {len(files)} files transcribed successfully.")
```
