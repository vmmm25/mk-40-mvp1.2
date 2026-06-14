---
name: hf-cli
version: 1.0.0
description: HuggingFace CLI interface skill for authentication, repository management, model/dataset upload and download, Space management, and environment configuration. Use when interacting with the HuggingFace Hub from the command line.
tags: [huggingface, cli, models, datasets, spaces, hub, ml, ai, upload, download]
author: garri333
license: MIT
source: huggingface/skills
---

# HuggingFace CLI Skill

## Overview

Use this skill whenever the user needs to interact with the HuggingFace Hub via the command line — authenticating, managing repositories (models, datasets, Spaces), uploading or downloading artifacts, or configuring the local HF environment.

---

## When to Activate

- User asks to log in or authenticate with HuggingFace.
- User wants to create, clone, delete, or list HuggingFace repositories.
- User needs to upload models, datasets, or files to the Hub.
- User needs to download models or datasets from the Hub.
- User wants to manage or deploy HuggingFace Spaces.
- User asks about HuggingFace environment configuration or tokens.

---

## Step-by-Step Procedures

### 1. Installation

```bash
# Install the huggingface_hub library (includes the CLI)
pip install huggingface_hub

# Verify installation
huggingface-cli --help

# Upgrade to latest
pip install --upgrade huggingface_hub
```

### 2. Authentication

```bash
# Interactive login — prompts for token
huggingface-cli login

# Login with token directly (non-interactive, CI/CD friendly)
huggingface-cli login --token hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Verify who you are
huggingface-cli whoami

# Logout (removes stored token)
huggingface-cli logout
```

**Token types:**
- **Read** (`read`): Download public/private models and datasets.
- **Write** (`write`): Upload, create repos, push changes.
- **Fine-grained**: Scoped to specific repos or organizations.

**Environment variable alternative:**

```bash
# Set token via environment variable (useful for CI/CD)
export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# On Windows PowerShell
$env:HF_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 3. Repository Management

#### Create a repository

```bash
# Create a model repository
huggingface-cli repo create my-model --type model

# Create a dataset repository
huggingface-cli repo create my-dataset --type dataset

# Create a Space
huggingface-cli repo create my-space --type space --space-sdk gradio

# Create a private repository
huggingface-cli repo create my-private-model --type model --private

# Create under an organization
huggingface-cli repo create my-model --type model --organization my-org
```

#### Clone a repository

```bash
# Clone using git (LFS required for large files)
git lfs install
git clone https://huggingface.co/username/my-model

# Clone a dataset
git clone https://huggingface.co/datasets/username/my-dataset

# Clone a Space
git clone https://huggingface.co/spaces/username/my-space
```

#### Delete a repository

```bash
# Delete a repo (interactive confirmation)
huggingface-cli repo delete username/my-model --type model

# Delete a dataset repo
huggingface-cli repo delete username/my-dataset --type dataset
```

### 4. Upload Files

```bash
# Upload a single file to a model repo
huggingface-cli upload username/my-model ./model.safetensors

# Upload an entire folder
huggingface-cli upload username/my-model ./output-dir

# Upload to a specific path in the repo
huggingface-cli upload username/my-model ./local-file.bin --path-in-repo models/file.bin

# Upload to a specific revision/branch
huggingface-cli upload username/my-model ./model.safetensors --revision dev

# Upload a dataset
huggingface-cli upload username/my-dataset ./data --repo-type dataset

# Upload with commit message
huggingface-cli upload username/my-model ./model.safetensors --commit-message "Add fine-tuned weights v2"
```

**Programmatic upload (Python):**

```python
from huggingface_hub import HfApi

api = HfApi()

# Upload a single file
api.upload_file(
    path_or_fileobj="./model.safetensors",
    path_in_repo="model.safetensors",
    repo_id="username/my-model",
    repo_type="model",
    commit_message="Upload model weights",
)

# Upload an entire folder
api.upload_folder(
    folder_path="./output",
    repo_id="username/my-model",
    repo_type="model",
    commit_message="Upload training output",
)
```

### 5. Download Files

```bash
# Download an entire model repo
huggingface-cli download username/my-model

# Download to a specific local directory
huggingface-cli download username/my-model --local-dir ./models/my-model

# Download specific files only
huggingface-cli download username/my-model config.json model.safetensors

# Download a dataset
huggingface-cli download username/my-dataset --repo-type dataset

# Download a specific revision
huggingface-cli download username/my-model --revision v1.0

# Download with include/exclude patterns
huggingface-cli download username/my-model --include "*.safetensors" --exclude "*.bin"

# Resume an interrupted download
huggingface-cli download username/my-model --resume-download
```

**Programmatic download (Python):**

```python
from huggingface_hub import hf_hub_download, snapshot_download

# Download a single file
file_path = hf_hub_download(
    repo_id="username/my-model",
    filename="model.safetensors",
    cache_dir="./cache",
)

# Download entire repo snapshot
snapshot_download(
    repo_id="username/my-model",
    local_dir="./models/my-model",
    allow_patterns=["*.safetensors", "*.json"],
)
```

### 6. Space Management

```bash
# Create a Gradio Space
huggingface-cli repo create my-app --type space --space-sdk gradio

# Create a Streamlit Space
huggingface-cli repo create my-dashboard --type space --space-sdk streamlit

# Create a Docker Space
huggingface-cli repo create my-service --type space --space-sdk docker

# Upload files to a Space
huggingface-cli upload username/my-app ./app.py --repo-type space

# Pause a Space (stop compute costs)
# Via Python API
from huggingface_hub import HfApi
api = HfApi()
api.pause_space("username/my-app")

# Restart a paused Space
api.restart_space("username/my-app")
```

### 7. Environment Configuration

```bash
# Set default cache directory
export HF_HOME=/path/to/custom/cache

# Set specific cache for Hub downloads
export HF_HUB_CACHE=/path/to/hub/cache

# Disable telemetry
export HF_HUB_DISABLE_TELEMETRY=1

# Set offline mode (use cached files only)
export HF_HUB_OFFLINE=1

# Set endpoint (for enterprise/on-prem)
export HF_ENDPOINT=https://my-hf-instance.com

# Check environment info
huggingface-cli env
```

### 8. Integration with Transformers & Datasets

```python
from transformers import AutoModel, AutoTokenizer

# Download and load automatically via transformers
model = AutoModel.from_pretrained("username/my-model")
tokenizer = AutoTokenizer.from_pretrained("username/my-model")

# Push model to Hub directly from transformers
model.push_to_hub("username/my-model")
tokenizer.push_to_hub("username/my-model")

# With datasets library
from datasets import load_dataset

dataset = load_dataset("username/my-dataset")
dataset.push_to_hub("username/my-dataset")
```

---

## Best Practices

1. **Use fine-grained tokens** — Scope tokens to specific repos when possible; avoid using write tokens globally.
2. **Prefer `safetensors` format** — More secure and faster than pickle-based formats.
3. **Use `.gitignore` in repos** — Exclude logs, checkpoints, and temp files from uploads.
4. **Set `HF_HOME`** — Keep cache organized, especially on shared systems.
5. **Use `--include`/`--exclude` patterns** — Download only what you need to save time and bandwidth.
6. **Add model/dataset cards** — Every repo should have a well-written `README.md` with YAML metadata.
7. **Use commit messages** — Provide meaningful commit messages on uploads for traceability.
8. **CI/CD integration** — Use `HF_TOKEN` environment variable and non-interactive login in pipelines.
9. **Verify with `whoami`** — Always confirm your authentication context before pushing.
10. **Use LFS** — For files > 10MB, ensure Git LFS is installed and tracking large files.

---

## Examples

### Full model upload workflow

```bash
# Authenticate
huggingface-cli login --token $HF_TOKEN

# Create repo
huggingface-cli repo create bert-finetuned-ner --type model --private

# Upload model artifacts
huggingface-cli upload username/bert-finetuned-ner ./output \
  --commit-message "Initial fine-tuned NER model release"

# Verify
huggingface-cli whoami
```

### Download and cache a model for offline use

```bash
# Pre-download everything
huggingface-cli download meta-llama/Llama-2-7b-hf --local-dir ./llama2

# Set offline mode for later use
export HF_HUB_OFFLINE=1
python my_inference_script.py
```

### CI/CD pipeline snippet

```yaml
# GitHub Actions example
- name: Push model to HuggingFace Hub
  env:
    HF_TOKEN: ${{ secrets.HF_TOKEN }}
  run: |
    pip install huggingface_hub
    huggingface-cli upload my-org/my-model ./trained-model \
      --commit-message "Auto-deploy from CI build ${{ github.run_id }}"
```
