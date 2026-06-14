---
name: hf-jobs
version: 1.0.0
description: Job orchestration on HuggingFace infrastructure. Covers Spaces deployment, Inference Endpoints, AutoTrain, compute resource management, GPU selection, job monitoring, cost optimization, serverless inference, batch inference, scaling, and Docker Spaces. Use when deploying or running ML workloads on HuggingFace.
tags: [huggingface, jobs, spaces, inference, endpoints, autotrain, gpu, deployment, serverless, docker, scaling, ml]
author: garri333
license: MIT
source: huggingface/skills
---

# HuggingFace Jobs Skill

## Overview

Use this skill whenever the user needs to deploy, orchestrate, or manage ML workloads on HuggingFace infrastructure — including Spaces, Inference Endpoints, AutoTrain, GPU resource management, serverless inference, and batch processing.

---

## When to Activate

- User wants to deploy a model or app on HuggingFace Spaces.
- User asks about Inference Endpoints (dedicated or serverless).
- User wants to use AutoTrain for no-code/low-code training.
- User needs to select or manage GPU resources (A100, T4, L4).
- User asks about job monitoring, logs, or cost optimization.
- User wants serverless or batch inference.
- User asks about Docker Spaces or custom deployments.
- User needs scaling strategies for production workloads.

---

## Step-by-Step Procedures

### 1. HuggingFace Spaces Deployment

#### Gradio Space

```bash
# Create Space via CLI
huggingface-cli repo create my-demo --type space --space-sdk gradio
git clone https://huggingface.co/spaces/username/my-demo
cd my-demo
```

```python
# app.py — minimal Gradio app
import gradio as gr
from transformers import pipeline

classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

def predict(text):
    result = classifier(text)[0]
    return f"{result['label']}: {result['score']:.4f}"

demo = gr.Interface(
    fn=predict,
    inputs=gr.Textbox(label="Input Text", placeholder="Enter text to classify..."),
    outputs=gr.Textbox(label="Prediction"),
    title="Sentiment Classifier",
    description="Classify text sentiment using DistilBERT.",
)

demo.launch()
```

```
# requirements.txt
transformers
torch
gradio
```

```bash
# Deploy
git add .
git commit -m "Initial Gradio app"
git push
```

#### Streamlit Space

```python
# app.py — Streamlit app
import streamlit as st
from transformers import pipeline

st.title("🤗 Text Classifier")

@st.cache_resource
def load_model():
    return pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

classifier = load_model()
text = st.text_area("Enter text:")

if st.button("Classify"):
    result = classifier(text)[0]
    st.success(f"{result['label']}: {result['score']:.4f}")
```

#### Space Configuration (README.md metadata)

```yaml
---
title: My ML Demo
emoji: 🤗
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
hardware: cpu-basic         # See GPU options below
suggested_hardware: t4-small
---
```

**Available hardware tiers:**

| Hardware        | GPU Memory | vCPU | RAM    | Cost/hr   | Use Case                      |
|-----------------|-----------|------|--------|-----------|-------------------------------|
| `cpu-basic`     | —         | 2    | 16 GB  | Free      | Lightweight demos             |
| `cpu-upgrade`   | —         | 8    | 32 GB  | ~$0.03    | CPU-heavy processing          |
| `t4-small`      | 16 GB    | 4    | 15 GB  | ~$0.60    | Small model inference         |
| `t4-medium`     | 16 GB    | 8    | 30 GB  | ~$0.90    | Medium models                 |
| `a10g-small`    | 24 GB    | 4    | 15 GB  | ~$1.05    | Larger models, faster         |
| `a10g-large`    | 24 GB    | 12   | 46 GB  | ~$3.15    | Production inference          |
| `a100-large`    | 80 GB    | 12   | 142 GB | ~$4.13    | LLMs, large batch inference   |
| `l4x1`          | 24 GB    | 8    | 30 GB  | ~$0.80    | Balanced performance          |
| `l4x4`          | 96 GB    | 48   | 188 GB | ~$3.80    | Multi-GPU workloads           |

#### Manage Space programmatically

```python
from huggingface_hub import HfApi

api = HfApi()

# Pause a Space (stops billing)
api.pause_space("username/my-demo")

# Restart a paused Space
api.restart_space("username/my-demo")

# Change hardware
api.request_space_hardware("username/my-demo", hardware="t4-small")

# Set Space to private
api.update_repo_visibility("username/my-demo", private=True, repo_type="space")

# Add secrets (environment variables)
api.add_space_secret("username/my-demo", key="API_KEY", value="sk-xxx")

# Delete a secret
api.delete_space_secret("username/my-demo", key="API_KEY")

# Get Space runtime info
runtime = api.get_space_runtime("username/my-demo")
print(runtime.hardware, runtime.stage)  # "t4-small", "RUNNING"
```

### 2. Docker Spaces

```dockerfile
# Dockerfile for a Docker Space
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir transformers torch fastapi uvicorn

COPY app.py .

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

```python
# app.py — FastAPI backend for Docker Space
from fastapi import FastAPI
from transformers import pipeline

app = FastAPI()
classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/predict")
def predict(text: str):
    result = classifier(text)[0]
    return {"label": result["label"], "score": result["score"]}

@app.get("/health")
def health():
    return {"status": "healthy"}
```

```yaml
# README.md frontmatter for Docker Space
---
title: My Docker API
emoji: 🐳
colorFrom: purple
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---
```

### 3. Inference Endpoints

#### Create a dedicated endpoint

```python
from huggingface_hub import HfApi, InferenceEndpoint

api = HfApi()

# Create endpoint
endpoint = api.create_inference_endpoint(
    name="my-classifier-endpoint",
    repository="distilbert-base-uncased-finetuned-sst-2-english",
    framework="pytorch",
    task="text-classification",
    accelerator="gpu",
    instance_size="x1",              # Small GPU instance
    instance_type="nvidia-a10g",
    region="us-east-1",
    vendor="aws",                    # "aws" or "gcp"
    type="protected",                # "public", "protected", or "private"
    min_replica=0,                   # Scale to zero when idle
    max_replica=2,                   # Max 2 replicas
    scale_to_zero_timeout=15,        # Minutes before scaling to zero
)

# Wait for endpoint to be ready
endpoint.wait()
print(f"Endpoint URL: {endpoint.url}")
print(f"Status: {endpoint.status}")
```

#### Call the endpoint

```python
from huggingface_hub import InferenceClient

client = InferenceClient(
    model="https://xxxx.us-east-1.aws.endpoints.huggingface.cloud",
    token="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
)

# Text classification
result = client.text_classification("I love this product!")
print(result)  # [Classification(label='POSITIVE', score=0.9998)]

# Text generation
response = client.text_generation(
    "The future of AI is",
    max_new_tokens=100,
    temperature=0.7,
    top_p=0.9,
)
print(response)

# Chat completion (for chat models)
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain transformers in 3 sentences."},
]
response = client.chat_completion(messages, max_tokens=200)
print(response.choices[0].message.content)
```

#### Manage endpoints

```python
# List all endpoints
endpoints = api.list_inference_endpoints()
for ep in endpoints:
    print(f"{ep.name}: {ep.status} ({ep.instance_type})")

# Pause endpoint (stop billing)
endpoint.pause()

# Resume endpoint
endpoint.resume()
endpoint.wait()

# Scale endpoint
endpoint.update(min_replica=1, max_replica=4)

# Delete endpoint
endpoint.delete()
```

### 4. Serverless Inference API

```python
from huggingface_hub import InferenceClient

# Free serverless inference (rate-limited)
client = InferenceClient(token="hf_xxxxx")

# Text generation
response = client.text_generation(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    prompt="Explain quantum computing in simple terms:",
    max_new_tokens=200,
)

# Image generation
image = client.text_to_image(
    model="stabilityai/stable-diffusion-xl-base-1.0",
    prompt="A futuristic city at sunset, digital art",
)
image.save("output.png")

# Embeddings
embeddings = client.feature_extraction(
    model="sentence-transformers/all-MiniLM-L6-v2",
    text="This is a test sentence.",
)

# Automatic speech recognition
result = client.automatic_speech_recognition(
    model="openai/whisper-large-v3",
    audio="audio.mp3",
)
print(result["text"])

# Image classification
result = client.image_classification(
    model="google/vit-base-patch16-224",
    image="cat.jpg",
)
```

```bash
# cURL serverless inference
curl https://api-inference.huggingface.co/models/gpt2 \
  -X POST \
  -H "Authorization: Bearer hf_xxxxx" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "The meaning of life is"}'
```

### 5. AutoTrain

```bash
# Install AutoTrain
pip install autotrain-advanced

# Text classification (CLI)
autotrain --project-name my-classifier \
    --task text-classification \
    --model bert-base-uncased \
    --data-path ./data \
    --text-column text \
    --target-column label \
    --lr 2e-5 \
    --epochs 3 \
    --batch-size 16 \
    --push-to-hub \
    --repo-id username/my-classifier

# LLM fine-tuning with AutoTrain
autotrain --project-name my-llm \
    --task llm-sft \
    --model meta-llama/Llama-2-7b-hf \
    --data-path ./data \
    --text-column text \
    --lr 2e-4 \
    --epochs 1 \
    --batch-size 4 \
    --gradient-accumulation 4 \
    --peft \
    --quantization int4 \
    --push-to-hub \
    --repo-id username/my-llm-finetuned

# Image classification
autotrain --project-name my-image-clf \
    --task image-classification \
    --model google/vit-base-patch16-224 \
    --data-path ./images \
    --lr 5e-5 \
    --epochs 10 \
    --push-to-hub
```

**AutoTrain via UI:** Navigate to [https://huggingface.co/autotrain](https://huggingface.co/autotrain) for a no-code interface.

### 6. Compute Resource Management & GPU Selection

#### Choosing the right GPU

| GPU    | VRAM   | Best For                          | Models                          |
|--------|--------|------------------------------------|---------------------------------|
| T4     | 16 GB  | Small models, inference            | BERT, DistilBERT, ViT          |
| L4     | 24 GB  | Medium models, balanced cost       | Mistral-7B (quantized), SD-XL  |
| A10G   | 24 GB  | Production inference, fine-tuning  | 7B models (QLoRA), Whisper     |
| A100   | 40/80 GB | Large models, training           | LLaMA-13B+, full fine-tuning   |
| H100   | 80 GB  | Fastest training, largest models   | 70B models, pretraining        |

#### Memory estimation

```python
def estimate_model_memory(num_params_billions, precision="fp16"):
    """Estimate GPU memory needed for inference."""
    bytes_per_param = {
        "fp32": 4,
        "fp16": 2,
        "bf16": 2,
        "int8": 1,
        "int4": 0.5,
    }
    model_size_gb = num_params_billions * bytes_per_param[precision]
    # Add ~20% overhead for activations and framework
    total_gb = model_size_gb * 1.2
    return total_gb

# Examples
print(f"7B fp16:  {estimate_model_memory(7, 'fp16'):.1f} GB")   # ~16.8 GB
print(f"7B int4:  {estimate_model_memory(7, 'int4'):.1f} GB")   # ~4.2 GB
print(f"13B fp16: {estimate_model_memory(13, 'fp16'):.1f} GB")  # ~31.2 GB
print(f"70B int4: {estimate_model_memory(70, 'int4'):.1f} GB")  # ~42.0 GB
```

### 7. Job Monitoring

```python
from huggingface_hub import HfApi

api = HfApi()

# Monitor Space status
runtime = api.get_space_runtime("username/my-demo")
print(f"Stage: {runtime.stage}")       # RUNNING, BUILDING, PAUSED, ERROR
print(f"Hardware: {runtime.hardware}")
print(f"Storage: {runtime.storage}")

# Get Space logs
# Via browser: https://huggingface.co/spaces/username/my-demo/logs

# Monitor Inference Endpoint
endpoint = api.get_inference_endpoint("my-endpoint")
print(f"Status: {endpoint.status}")     # running, paused, initializing, failed
print(f"URL: {endpoint.url}")
print(f"Instance: {endpoint.instance_type}")
print(f"Replicas: {endpoint.min_replica}-{endpoint.max_replica}")

# List all running Spaces
spaces = api.list_spaces(author="username")
for space in spaces:
    runtime = api.get_space_runtime(space.id)
    print(f"{space.id}: {runtime.stage} ({runtime.hardware})")
```

### 8. Cost Optimization

#### Scale-to-zero for Inference Endpoints

```python
endpoint = api.create_inference_endpoint(
    name="cost-optimized-endpoint",
    repository="username/my-model",
    min_replica=0,                   # Scale to zero when idle
    max_replica=1,
    scale_to_zero_timeout=15,        # Minutes idle before scaling down
    ...
)
```

#### Pause unused Spaces

```python
import datetime
from huggingface_hub import HfApi

api = HfApi()

def pause_idle_spaces(author, idle_hours=24):
    """Pause Spaces that haven't been used recently."""
    spaces = api.list_spaces(author=author)
    for space in spaces:
        runtime = api.get_space_runtime(space.id)
        if runtime.stage == "RUNNING" and runtime.hardware != "cpu-basic":
            # Pause non-free spaces to save costs
            api.pause_space(space.id)
            print(f"Paused: {space.id} ({runtime.hardware})")

pause_idle_spaces("username")
```

#### Cost-efficient strategies

1. **Use `cpu-basic` (free)** for demos and prototypes.
2. **Scale to zero** — Set `min_replica=0` on Inference Endpoints.
3. **Use quantized models** — Run 7B models on T4 with int4 quantization.
4. **Batch requests** — Accumulate requests and process in batches to maximize GPU utilization.
5. **Use serverless API** for low-volume inference (pay per request).
6. **Schedule workloads** — Pause Spaces and endpoints during off-hours.
7. **Use spot/preemptible instances** when available.

### 9. Batch Inference

```python
from huggingface_hub import InferenceClient
from concurrent.futures import ThreadPoolExecutor
import json

client = InferenceClient(model="username/my-endpoint-url", token="hf_xxxxx")

def batch_inference(texts, batch_size=32, max_workers=4):
    """Run batch inference with concurrent requests."""
    results = []

    # Split into batches
    batches = [texts[i:i+batch_size] for i in range(0, len(texts), batch_size)]

    def process_batch(batch):
        batch_results = []
        for text in batch:
            result = client.text_classification(text)
            batch_results.append(result)
        return batch_results

    # Process batches concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_batch, batch) for batch in batches]
        for future in futures:
            results.extend(future.result())

    return results

# Usage
texts = ["text1", "text2", ..., "text10000"]
results = batch_inference(texts, batch_size=64, max_workers=8)

# Save results
with open("batch_results.json", "w") as f:
    json.dump(results, f)
```

#### Offline batch inference (local GPU)

```python
from transformers import pipeline
import torch

pipe = pipeline(
    "text-classification",
    model="username/my-model",
    device_map="auto",
    batch_size=64,
    torch_dtype=torch.float16,
)

# Process large dataset
from datasets import load_dataset

dataset = load_dataset("my-dataset", split="test")
results = pipe(dataset["text"], batch_size=64)

# With progress tracking
from tqdm import tqdm

all_results = []
for i in tqdm(range(0, len(dataset), 64)):
    batch = dataset["text"][i:i+64]
    batch_results = pipe(batch, batch_size=64)
    all_results.extend(batch_results)
```

### 10. Scaling Strategies

#### Horizontal scaling with Inference Endpoints

```python
# Auto-scaling configuration
endpoint = api.create_inference_endpoint(
    name="scalable-endpoint",
    repository="username/my-model",
    min_replica=1,                   # Always-on minimum
    max_replica=8,                   # Scale up to 8 replicas
    scale_to_zero_timeout=30,        # Minutes before scaling to zero (if min=0)
    ...
)

# Update scaling parameters
endpoint.update(min_replica=2, max_replica=10)
```

#### Load balancing across Spaces

```python
# Deploy multiple Spaces and load balance with a reverse proxy
SPACE_URLS = [
    "https://username-my-app-1.hf.space",
    "https://username-my-app-2.hf.space",
    "https://username-my-app-3.hf.space",
]

import random
import requests

def balanced_request(text):
    url = random.choice(SPACE_URLS)
    response = requests.post(f"{url}/api/predict", json={"data": [text]})
    return response.json()
```

#### Multi-region deployment

```python
# Deploy endpoints in multiple regions for latency optimization
regions = [
    {"region": "us-east-1", "vendor": "aws"},
    {"region": "eu-west-1", "vendor": "aws"},
    {"region": "us-central1", "vendor": "gcp"},
]

for region_config in regions:
    api.create_inference_endpoint(
        name=f"my-model-{region_config['region']}",
        repository="username/my-model",
        region=region_config["region"],
        vendor=region_config["vendor"],
        min_replica=1,
        max_replica=4,
        ...
    )
```

---

## Best Practices

1. **Start with free tier** — Use `cpu-basic` Spaces and serverless API for development and demos.
2. **Scale to zero** — Always set `min_replica=0` on non-production endpoints.
3. **Use quantization** — Run larger models on smaller GPUs with int4/int8 quantization.
4. **Monitor costs** — Check HuggingFace billing dashboard regularly; pause idle resources.
5. **Add health checks** — Include `/health` endpoints in Docker Spaces for monitoring.
6. **Use secrets** — Never hardcode API keys; use Space secrets or environment variables.
7. **Pin dependencies** — Specify exact versions in `requirements.txt` to avoid breaking changes.
8. **Cache models** — Use `@st.cache_resource` (Streamlit) or load at startup to avoid reloading.
9. **Batch when possible** — Accumulate requests for better GPU utilization and lower per-request cost.
10. **Use AutoTrain** — For standard tasks (classification, fine-tuning), AutoTrain is faster than custom code.
11. **Docker for complex apps** — Use Docker Spaces when you need system dependencies or custom runtimes.
12. **Test locally first** — Run `gradio app.py` or `docker build` locally before deploying to Spaces.

---

## Examples

### Deploy a Gradio chatbot on GPU Space

```python
# app.py
import gradio as gr
from transformers import pipeline
import torch

chatbot = pipeline(
    "text-generation",
    model="mistralai/Mistral-7B-Instruct-v0.2",
    torch_dtype=torch.float16,
    device_map="auto",
)

def respond(message, history):
    messages = [{"role": "user", "content": message}]
    prompt = chatbot.tokenizer.apply_chat_template(messages, tokenize=False)
    response = chatbot(prompt, max_new_tokens=512, do_sample=True, temperature=0.7)
    return response[0]["generated_text"].split("[/INST]")[-1].strip()

demo = gr.ChatInterface(respond, title="🤗 Mistral Chatbot")
demo.launch()
```

```yaml
# README.md
---
title: Mistral Chatbot
sdk: gradio
hardware: a10g-small
---
```

### Create and manage an Inference Endpoint (end-to-end)

```python
from huggingface_hub import HfApi, InferenceClient

api = HfApi()

# Create
ep = api.create_inference_endpoint(
    name="prod-classifier",
    repository="distilbert-base-uncased-finetuned-sst-2-english",
    task="text-classification",
    accelerator="gpu",
    instance_type="nvidia-t4",
    instance_size="x1",
    region="us-east-1",
    vendor="aws",
    min_replica=0,
    max_replica=2,
    scale_to_zero_timeout=15,
)
ep.wait()

# Use
client = InferenceClient(model=ep.url, token="hf_xxxxx")
result = client.text_classification("This product is amazing!")
print(result)

# Cleanup
ep.delete()
```
