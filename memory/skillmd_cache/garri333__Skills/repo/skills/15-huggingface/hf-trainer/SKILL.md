---
name: hf-trainer
version: 1.0.0
description: Model training with HuggingFace Transformers Trainer API. Covers TrainingArguments, hyperparameter tuning, distributed training, mixed precision, LoRA/QLoRA fine-tuning, PEFT, evaluation, and experiment tracking. Use when training or fine-tuning transformer models.
tags: [huggingface, training, transformers, trainer, fine-tuning, lora, qlora, peft, deepspeed, distributed, mixed-precision, ml]
author: garri333
license: MIT
source: huggingface/skills
---

# HuggingFace Trainer Skill

## Overview

Use this skill whenever the user needs to train or fine-tune models using the HuggingFace Transformers library. Covers the full training lifecycle: configuration, hyperparameter tuning, distributed training, parameter-efficient fine-tuning (PEFT), evaluation, checkpointing, and experiment tracking.

---

## When to Activate

- User wants to fine-tune a pretrained model (BERT, GPT, LLaMA, etc.).
- User asks about `TrainingArguments` or the `Trainer` API.
- User needs hyperparameter tuning (learning rate, batch size, epochs).
- User asks about distributed training (DDP, DeepSpeed, FSDP).
- User wants mixed precision training (fp16, bf16).
- User asks about LoRA, QLoRA, or PEFT fine-tuning.
- User needs gradient checkpointing or accumulation setup.
- User wants evaluation during training, early stopping, or checkpointing.
- User asks about Weights & Biases (W&B) integration.

---

## Step-by-Step Procedures

### 1. Installation

```bash
# Core
pip install transformers datasets accelerate

# For PEFT / LoRA
pip install peft bitsandbytes

# For DeepSpeed
pip install deepspeed

# For experiment tracking
pip install wandb

# For hyperparameter search
pip install optuna ray[tune]
```

### 2. Basic Training with Trainer API

```python
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)
from datasets import load_dataset

# Load data and model
dataset = load_dataset("imdb")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased", num_labels=2
)

# Tokenize
def preprocess(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=512)

dataset = dataset.map(preprocess, batched=True)

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    learning_rate=2e-5,
    weight_decay=0.01,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    logging_steps=100,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    report_to="wandb",  # or "tensorboard", "none"
    seed=42,
)

# Custom metrics
import numpy as np
from datasets import load as load_metric

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = (predictions == labels).mean()
    return {"accuracy": accuracy}

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

trainer.train()

# Save and push
trainer.save_model("./final-model")
trainer.push_to_hub("username/bert-imdb")
```

### 3. TrainingArguments Deep Dive

```python
training_args = TrainingArguments(
    # === Output ===
    output_dir="./results",
    overwrite_output_dir=True,

    # === Training Duration ===
    num_train_epochs=3,
    max_steps=-1,                         # -1 = use num_train_epochs

    # === Batch Size & Accumulation ===
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    gradient_accumulation_steps=4,        # Effective batch = 16 * 4 = 64

    # === Learning Rate & Schedule ===
    learning_rate=2e-5,
    lr_scheduler_type="cosine",           # linear, cosine, constant, polynomial
    warmup_ratio=0.1,                     # 10% of total steps
    warmup_steps=0,                       # Alternative: fixed warmup steps
    weight_decay=0.01,
    adam_beta1=0.9,
    adam_beta2=0.999,
    adam_epsilon=1e-8,
    max_grad_norm=1.0,                    # Gradient clipping

    # === Mixed Precision ===
    fp16=True,                            # NVIDIA GPUs (Volta+)
    bf16=False,                           # Ampere+ GPUs, TPUs
    tf32=True,                            # Ampere+ (enabled by default)

    # === Evaluation ===
    eval_strategy="steps",                # "no", "steps", "epoch"
    eval_steps=500,
    metric_for_best_model="eval_loss",
    greater_is_better=False,

    # === Saving & Checkpointing ===
    save_strategy="steps",
    save_steps=500,
    save_total_limit=3,                   # Keep only last 3 checkpoints
    load_best_model_at_end=True,

    # === Logging ===
    logging_dir="./logs",
    logging_steps=100,
    logging_first_step=True,
    report_to=["wandb", "tensorboard"],

    # === Memory Optimization ===
    gradient_checkpointing=True,          # Trade compute for memory
    optim="adamw_torch",                  # or "adamw_8bit", "adafactor"

    # === Distributed ===
    dataloader_num_workers=4,
    ddp_find_unused_parameters=False,

    # === Reproducibility ===
    seed=42,
    data_seed=42,

    # === Hub ===
    push_to_hub=True,
    hub_model_id="username/my-model",
    hub_strategy="end",                   # "end", "every_save", "checkpoint"
)
```

### 4. Hyperparameter Tuning

#### With Optuna

```python
def hp_space_optuna(trial):
    return {
        "learning_rate": trial.suggest_float("learning_rate", 1e-6, 1e-4, log=True),
        "per_device_train_batch_size": trial.suggest_categorical(
            "per_device_train_batch_size", [8, 16, 32]
        ),
        "num_train_epochs": trial.suggest_int("num_train_epochs", 2, 5),
        "weight_decay": trial.suggest_float("weight_decay", 0.0, 0.3),
        "warmup_ratio": trial.suggest_float("warmup_ratio", 0.0, 0.2),
    }

best_run = trainer.hyperparameter_search(
    direction="maximize",
    backend="optuna",
    hp_space=hp_space_optuna,
    n_trials=20,
    compute_objective=lambda metrics: metrics["eval_accuracy"],
)

print(f"Best hyperparameters: {best_run.hyperparameters}")
```

#### With Ray Tune

```python
def hp_space_ray(trial):
    from ray import tune
    return {
        "learning_rate": tune.loguniform(1e-6, 1e-4),
        "per_device_train_batch_size": tune.choice([8, 16, 32]),
        "num_train_epochs": tune.choice([2, 3, 4, 5]),
    }

best_run = trainer.hyperparameter_search(
    direction="maximize",
    backend="ray",
    hp_space=hp_space_ray,
    n_trials=20,
)
```

### 5. Distributed Training

#### DataParallel (single node, multi-GPU — automatic)

```bash
# Trainer uses all visible GPUs by default
python train.py
# or restrict GPUs:
CUDA_VISIBLE_DEVICES=0,1 python train.py
```

#### DistributedDataParallel (DDP)

```bash
# Using torchrun (recommended)
torchrun --nproc_per_node=4 train.py

# Multi-node
torchrun --nproc_per_node=4 --nnodes=2 \
         --node_rank=0 --master_addr=192.168.1.1 --master_port=29500 \
         train.py
```

#### With Accelerate (recommended wrapper)

```bash
# Configure once
accelerate config

# Launch training
accelerate launch train.py

# Or specify directly
accelerate launch --multi_gpu --num_processes=4 train.py
```

#### DeepSpeed Integration

```python
# In TrainingArguments
training_args = TrainingArguments(
    output_dir="./results",
    deepspeed="ds_config.json",
    fp16=True,
)
```

**DeepSpeed ZeRO Stage 2 config (`ds_config.json`):**

```json
{
    "zero_optimization": {
        "stage": 2,
        "offload_optimizer": {
            "device": "cpu",
            "pin_memory": true
        },
        "allgather_partitions": true,
        "allgather_bucket_size": 2e8,
        "reduce_scatter": true,
        "reduce_bucket_size": 2e8,
        "overlap_comm": true
    },
    "fp16": {
        "enabled": true,
        "loss_scale": 0,
        "loss_scale_window": 1000,
        "initial_scale_power": 16,
        "hysteresis": 2,
        "min_loss_scale": 1
    },
    "gradient_accumulation_steps": 4,
    "gradient_clipping": 1.0,
    "train_batch_size": "auto",
    "train_micro_batch_size_per_gpu": "auto"
}
```

**DeepSpeed ZeRO Stage 3 (for very large models):**

```json
{
    "zero_optimization": {
        "stage": 3,
        "offload_optimizer": { "device": "cpu", "pin_memory": true },
        "offload_param": { "device": "cpu", "pin_memory": true },
        "overlap_comm": true,
        "contiguous_gradients": true,
        "sub_group_size": 1e9,
        "stage3_max_live_parameters": 1e9,
        "stage3_max_reuse_distance": 1e9,
        "stage3_gather_16bit_weights_on_model_save": true
    }
}
```

```bash
# Launch with DeepSpeed
deepspeed --num_gpus=4 train.py --deepspeed ds_config.json

# Or via accelerate
accelerate launch --use_deepspeed --deepspeed_config_file ds_config.json train.py
```

#### FSDP (Fully Sharded Data Parallel)

```bash
# Configure via accelerate
accelerate config  # Select FSDP option

# Or via TrainingArguments
training_args = TrainingArguments(
    output_dir="./results",
    fsdp="full_shard auto_wrap",
    fsdp_config={
        "fsdp_min_num_params": 1e6,
        "fsdp_transformer_layer_cls_to_wrap": "BertLayer",
    },
)
```

### 6. Mixed Precision Training

```python
# FP16 (most NVIDIA GPUs)
training_args = TrainingArguments(
    fp16=True,
    fp16_opt_level="O1",              # Apex optimization level
    half_precision_backend="auto",
    ...
)

# BF16 (Ampere+, A100, H100, TPUs — better numeric stability)
training_args = TrainingArguments(
    bf16=True,
    ...
)

# TF32 (Ampere+ — automatic, no code change, ~2x faster matmul)
import torch
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
```

### 7. Gradient Checkpointing & Accumulation

```python
training_args = TrainingArguments(
    # Gradient checkpointing — recompute activations during backward pass
    # Reduces memory ~60% at cost of ~20% slower training
    gradient_checkpointing=True,
    gradient_checkpointing_kwargs={"use_reentrant": False},

    # Gradient accumulation — simulate larger batch sizes
    # Effective batch = per_device_train_batch_size * gradient_accumulation_steps * num_gpus
    gradient_accumulation_steps=8,
    per_device_train_batch_size=4,  # Effective batch = 4 * 8 = 32 per GPU
    ...
)
```

### 8. LoRA / QLoRA Fine-Tuning with PEFT

#### LoRA (Low-Rank Adaptation)

```python
from peft import LoraConfig, get_peft_model, TaskType

# Configure LoRA
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,        # or SEQ_CLS, SEQ_2_SEQ_LM, TOKEN_CLS
    r=16,                                 # Rank — lower = fewer params, higher = more capacity
    lora_alpha=32,                        # Scaling factor (alpha/r)
    lora_dropout=0.1,
    target_modules=["q_proj", "v_proj"],  # Which layers to adapt
    bias="none",                          # "none", "all", "lora_only"
)

# Apply LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Output: trainable params: 4,194,304 || all params: 6,742,609,920 || trainable%: 0.062

# Train normally with Trainer
trainer = Trainer(model=model, args=training_args, ...)
trainer.train()

# Save PEFT adapter (small file)
model.save_pretrained("./lora-adapter")

# Merge adapter with base model for inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("./merged-model")
```

#### QLoRA (Quantized LoRA — 4-bit training)

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",            # Normalized Float4
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,       # Double quantization
)

# Load model in 4-bit
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_config,
    device_map="auto",
)

# Prepare for k-bit training
model = prepare_model_for_kbit_training(model)

# Apply LoRA
lora_config = LoraConfig(
    r=64,
    lora_alpha=16,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

model = get_peft_model(model, lora_config)

# Train with appropriate args for QLoRA
training_args = TrainingArguments(
    output_dir="./qlora-output",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,
    fp16=True,
    logging_steps=10,
    save_strategy="steps",
    save_steps=100,
    optim="paged_adamw_8bit",
)

trainer = Trainer(model=model, args=training_args, ...)
trainer.train()
```

### 9. Evaluation During Training & Early Stopping

```python
from transformers import EarlyStoppingCallback

training_args = TrainingArguments(
    eval_strategy="steps",
    eval_steps=200,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    load_best_model_at_end=True,
    save_strategy="steps",
    save_steps=200,
    ...
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics,
    callbacks=[
        EarlyStoppingCallback(
            early_stopping_patience=3,      # Stop after 3 evals without improvement
            early_stopping_threshold=0.001, # Minimum improvement threshold
        ),
    ],
)
```

### 10. Model Checkpointing

```python
training_args = TrainingArguments(
    save_strategy="steps",           # "no", "steps", "epoch"
    save_steps=500,
    save_total_limit=5,              # Keep only 5 most recent checkpoints
    load_best_model_at_end=True,
    ...
)

# Resume from checkpoint
trainer.train(resume_from_checkpoint="./results/checkpoint-1500")

# Or resume from latest checkpoint
trainer.train(resume_from_checkpoint=True)
```

### 11. Weights & Biases Integration

```bash
# Login to W&B
wandb login
```

```python
import wandb

wandb.init(
    project="my-nlp-project",
    name="bert-finetune-v1",
    tags=["bert", "classification", "imdb"],
)

training_args = TrainingArguments(
    report_to="wandb",
    run_name="bert-finetune-v1",
    ...
)

# W&B automatically logs:
# - Training/eval loss curves
# - Learning rate schedule
# - GPU utilization
# - Hyperparameters
# - System metrics

# Log custom metrics
wandb.log({"custom_metric": value})

# Finish run
wandb.finish()
```

---

## Best Practices

1. **Start with a small LR** — Use `2e-5` for BERT-family, `2e-4` for LoRA, `1e-5` for large LLMs.
2. **Use warmup** — Set `warmup_ratio=0.06–0.1` to stabilize early training.
3. **Gradient accumulation over large batches** — If you OOM, reduce batch size and increase accumulation steps.
4. **Enable gradient checkpointing** — Always enable for models > 1B parameters.
5. **Use bf16 over fp16** when available — Better numeric stability, no loss scaling needed.
6. **QLoRA for LLMs** — Fine-tune 7B+ models on a single consumer GPU with 4-bit quantization.
7. **Set `save_total_limit`** — Prevent filling disk with hundreds of checkpoints.
8. **Always evaluate during training** — Use `eval_strategy="steps"` to catch overfitting early.
9. **Use `load_best_model_at_end=True`** — Ensures you keep the best model, not the last.
10. **Fix seeds** — Set `seed=42` and `data_seed=42` for reproducibility.
11. **Log everything with W&B** — Compare runs, share results, track experiments.
12. **Use `adafactor` for memory savings** — Replaces Adam with minimal quality loss for large models.

---

## Examples

### Fine-tune BERT for classification (complete)

```bash
pip install transformers datasets accelerate wandb
wandb login
```

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset
import numpy as np

dataset = load_dataset("yelp_review_full")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def tokenize(batch):
    return tokenizer(batch["text"], truncation=True, padding="max_length", max_length=256)

dataset = dataset.map(tokenize, batched=True)
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=5)

args = TrainingArguments(
    output_dir="./yelp-bert",
    num_train_epochs=3,
    per_device_train_batch_size=32,
    per_device_eval_batch_size=64,
    learning_rate=2e-5,
    warmup_ratio=0.1,
    weight_decay=0.01,
    fp16=True,
    eval_strategy="epoch",
    save_strategy="epoch",
    save_total_limit=2,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    report_to="wandb",
    seed=42,
)

def compute_metrics(eval_pred):
    preds = np.argmax(eval_pred.predictions, axis=-1)
    return {"accuracy": (preds == eval_pred.label_ids).mean()}

trainer = Trainer(model=model, args=args, train_dataset=dataset["train"],
                  eval_dataset=dataset["test"], tokenizer=tokenizer,
                  compute_metrics=compute_metrics)

trainer.train()
trainer.push_to_hub("username/yelp-bert-classifier")
```

### QLoRA fine-tune LLaMA 2 (complete)

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType
from datasets import load_dataset

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer.pad_token = tokenizer.eos_token

bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                 bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf",
                                              quantization_config=bnb_config, device_map="auto")
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(r=64, lora_alpha=16, lora_dropout=0.05, bias="none",
                          target_modules=["q_proj","k_proj","v_proj","o_proj",
                                          "gate_proj","up_proj","down_proj"],
                          task_type=TaskType.CAUSAL_LM)
model = get_peft_model(model, lora_config)

dataset = load_dataset("tatsu-lab/alpaca")

def format_example(ex):
    prompt = f"### Instruction:\n{ex['instruction']}\n\n### Response:\n{ex['output']}"
    return tokenizer(prompt, truncation=True, max_length=512, padding="max_length")

dataset = dataset["train"].map(format_example, remove_columns=dataset["train"].column_names)

args = TrainingArguments(output_dir="./qlora-llama2", num_train_epochs=1,
                          per_device_train_batch_size=4, gradient_accumulation_steps=4,
                          learning_rate=2e-4, lr_scheduler_type="cosine", warmup_ratio=0.03,
                          fp16=True, logging_steps=25, save_steps=200, save_total_limit=3,
                          optim="paged_adamw_8bit", seed=42)

trainer = Trainer(model=model, args=args, train_dataset=dataset, tokenizer=tokenizer)
trainer.train()
model.save_pretrained("./qlora-llama2-adapter")
```
