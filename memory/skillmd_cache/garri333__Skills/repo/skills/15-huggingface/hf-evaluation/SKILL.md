---
name: hf-evaluation
version: 1.0.0
description: Standardized model evaluation using HuggingFace evaluate library. Covers metrics (accuracy, F1, BLEU, ROUGE, perplexity), bias evaluation, benchmark suites (GLUE, SuperGLUE, MMLU), leaderboard submission, custom metrics, and reproducibility. Use when evaluating or comparing ML models.
tags: [huggingface, evaluation, metrics, benchmark, glue, bleu, rouge, f1, accuracy, bias, leaderboard, ml]
author: garri333
license: MIT
source: huggingface/skills
---

# HuggingFace Evaluation Skill

## Overview

Use this skill whenever the user needs to evaluate ML models in a standardized, reproducible way. Covers the `evaluate` library, built-in and custom metrics, benchmark suites, bias detection, model comparison, and leaderboard submission.

---

## When to Activate

- User asks how to evaluate a model's performance.
- User needs specific metrics (accuracy, F1, BLEU, ROUGE, perplexity, etc.).
- User wants to run benchmarks (GLUE, SuperGLUE, MMLU).
- User asks about bias or fairness evaluation.
- User wants to compare multiple models systematically.
- User asks about custom metric creation.
- User wants to submit results to the Open LLM Leaderboard or other leaderboards.
- User needs reproducible evaluation pipelines.

---

## Step-by-Step Procedures

### 1. Installation

```bash
pip install evaluate datasets transformers

# Optional: for specific metric dependencies
pip install rouge_score nltk sacrebleu bert_score
pip install jiwer  # for WER (speech)
pip install mauve-text  # for MAUVE
```

### 2. Loading and Using Metrics

#### Basic metrics

```python
import evaluate
import numpy as np

# Load a metric
accuracy = evaluate.load("accuracy")

# Compute
predictions = [0, 1, 1, 0, 1]
references =  [0, 1, 0, 0, 1]
result = accuracy.compute(predictions=predictions, references=references)
print(result)  # {'accuracy': 0.8}
```

#### Classification metrics

```python
# F1 Score
f1 = evaluate.load("f1")
result = f1.compute(predictions=predictions, references=references, average="weighted")
# average options: "micro", "macro", "weighted", "binary"

# Precision
precision = evaluate.load("precision")
result = precision.compute(predictions=predictions, references=references, average="weighted")

# Recall
recall = evaluate.load("recall")
result = recall.compute(predictions=predictions, references=references, average="weighted")

# Matthews Correlation Coefficient
mcc = evaluate.load("matthews_correlation")
result = mcc.compute(predictions=predictions, references=references)

# Combine multiple metrics
clf_metrics = evaluate.combine(["accuracy", "f1", "precision", "recall"])
result = clf_metrics.compute(predictions=predictions, references=references)
print(result)
# {'accuracy': 0.8, 'f1': 0.8, 'precision': 0.833, 'recall': 0.8}
```

#### Text generation metrics

```python
# BLEU (machine translation)
bleu = evaluate.load("bleu")
predictions = ["the cat sat on the mat"]
references = [["the cat is on the mat"]]
result = bleu.compute(predictions=predictions, references=references)
print(result)  # {'bleu': 0.61, 'precisions': [...], 'brevity_penalty': 1.0, ...}

# SacreBLEU (standardized BLEU)
sacrebleu = evaluate.load("sacrebleu")
result = sacrebleu.compute(predictions=predictions, references=references)

# ROUGE (summarization)
rouge = evaluate.load("rouge")
predictions = ["The model generates high quality summaries."]
references = ["The model produces excellent summaries."]
result = rouge.compute(predictions=predictions, references=references)
print(result)  # {'rouge1': 0.66, 'rouge2': 0.4, 'rougeL': 0.66, 'rougeLsum': 0.66}

# BERTScore (semantic similarity)
bertscore = evaluate.load("bertscore")
result = bertscore.compute(
    predictions=predictions,
    references=references,
    lang="en",
    model_type="microsoft/deberta-xlarge-mnli",
)

# METEOR
meteor = evaluate.load("meteor")
result = meteor.compute(predictions=predictions, references=references)
```

#### Perplexity (language models)

```python
perplexity = evaluate.load("perplexity", module_type="metric")

# Evaluate on text data
texts = ["This is a test sentence.", "Another sentence for evaluation."]
result = perplexity.compute(
    predictions=texts,
    model_id="gpt2",
    add_start_token=True,
    batch_size=8,
)
print(result)  # {'mean_perplexity': 42.3, 'perplexities': [35.1, 49.5]}
```

#### Word Error Rate (speech)

```python
wer = evaluate.load("wer")
predictions = ["hello world how are you"]
references = ["hello world how is you"]
result = wer.compute(predictions=predictions, references=references)
print(result)  # 0.2 (1 error out of 5 words)
```

### 3. Evaluation During Training (Trainer Integration)

```python
from transformers import Trainer, TrainingArguments
import evaluate
import numpy as np

# Load multiple metrics
accuracy = evaluate.load("accuracy")
f1 = evaluate.load("f1")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    acc = accuracy.compute(predictions=predictions, references=labels)
    f1_result = f1.compute(predictions=predictions, references=labels, average="weighted")
    return {**acc, **f1_result}

training_args = TrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",
    metric_for_best_model="f1",
    greater_is_better=True,
    load_best_model_at_end=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics,
)

# Run evaluation separately
results = trainer.evaluate()
print(results)
```

### 4. Benchmark Suites

#### GLUE Benchmark

```python
from datasets import load_dataset
import evaluate

# GLUE tasks and their metrics
GLUE_TASKS = {
    "cola": "matthews_correlation",    # Linguistic acceptability
    "sst2": "accuracy",               # Sentiment
    "mrpc": "f1",                      # Paraphrase
    "stsb": "pearsonr",               # Semantic similarity
    "qqp": "f1",                       # Question pair equivalence
    "mnli": "accuracy",               # Natural language inference
    "qnli": "accuracy",               # Question NLI
    "rte": "accuracy",                # Textual entailment
    "wnli": "accuracy",               # Winograd NLI
}

# Load a GLUE task
dataset = load_dataset("glue", "sst2")
metric = evaluate.load("glue", "sst2")

# Evaluate
result = metric.compute(predictions=predictions, references=references)
```

#### SuperGLUE Benchmark

```python
# SuperGLUE tasks
SUPERGLUE_TASKS = {
    "boolq": "accuracy",              # Boolean questions
    "cb": "f1",                        # CommitmentBank
    "copa": "accuracy",               # Choice of plausible alternatives
    "multirc": "f1",                   # Multi-sentence reading comprehension
    "record": "f1",                    # Reading comp. with commonsense
    "rte": "accuracy",                # Textual entailment
    "wic": "accuracy",                # Word-in-context
    "wsc": "accuracy",                # Winograd schema challenge
}

dataset = load_dataset("super_glue", "boolq")
metric = evaluate.load("super_glue", "boolq")
result = metric.compute(predictions=predictions, references=references)
```

#### MMLU (Massive Multitask Language Understanding)

```python
from datasets import load_dataset

# Load MMLU
dataset = load_dataset("cais/mmlu", "all")

# Subjects include: abstract_algebra, anatomy, astronomy, business_ethics,
# clinical_knowledge, college_biology, college_chemistry, college_physics,
# computer_science, ... (57 subjects total)

# Evaluate LLM on MMLU
from transformers import pipeline

pipe = pipeline("text-generation", model="your-model", device_map="auto")

correct = 0
total = 0
for example in dataset["test"]:
    question = example["question"]
    choices = example["choices"]
    answer = example["answer"]  # 0-3 index

    prompt = f"Question: {question}\nA) {choices[0]}\nB) {choices[1]}\nC) {choices[2]}\nD) {choices[3]}\nAnswer:"
    response = pipe(prompt, max_new_tokens=1)[0]["generated_text"]

    predicted = parse_answer(response)
    if predicted == answer:
        correct += 1
    total += 1

print(f"MMLU Accuracy: {correct / total:.4f}")
```

### 5. Bias & Fairness Evaluation

```python
# Regard metric (bias in text generation)
regard = evaluate.load("regard")
texts = [
    "The woman worked as a",
    "The man worked as a",
]
result = regard.compute(data=texts)

# Toxicity
toxicity = evaluate.load("toxicity")
result = toxicity.compute(predictions=[
    "This is a normal sentence.",
    "This sentence contains hateful content.",
])

# Bias evaluation across demographic groups
def evaluate_fairness(model, tokenizer, dataset, protected_attribute):
    """Evaluate model performance across demographic groups."""
    results = {}
    for group in dataset[protected_attribute].unique():
        group_data = dataset.filter(lambda x: x[protected_attribute] == group)
        predictions = predict(model, tokenizer, group_data)
        f1 = evaluate.load("f1")
        score = f1.compute(predictions=predictions, references=group_data["label"], average="weighted")
        results[group] = score["f1"]

    # Calculate disparity
    max_score = max(results.values())
    min_score = min(results.values())
    disparity = max_score - min_score
    results["disparity"] = disparity

    return results

# Honest metric (bias probing)
honest = evaluate.load("honest", "en")
completions = [["The woman is a doctor", "The woman is a nurse"]]
result = honest.compute(predictions=completions)
```

### 6. Model Comparison Methodology

```python
import evaluate
from datasets import load_dataset
import pandas as pd

def compare_models(model_ids, dataset_name, metric_names, task="text-classification"):
    """Compare multiple models on the same dataset and metrics."""
    dataset = load_dataset(dataset_name, split="test")
    metrics = {name: evaluate.load(name) for name in metric_names}

    results = []
    for model_id in model_ids:
        pipe = pipeline(task, model=model_id, device_map="auto")
        predictions = pipe(dataset["text"], batch_size=32)
        pred_labels = [p["label"] for p in predictions]

        model_scores = {"model": model_id}
        for name, metric in metrics.items():
            score = metric.compute(predictions=pred_labels, references=dataset["label"])
            model_scores.update(score)
        results.append(model_scores)

    df = pd.DataFrame(results)
    print(df.to_markdown(index=False))
    return df

# Usage
compare_models(
    model_ids=["bert-base-uncased", "roberta-base", "distilbert-base-uncased"],
    dataset_name="imdb",
    metric_names=["accuracy", "f1", "precision", "recall"],
)
```

### 7. Custom Metric Creation

```python
import evaluate
import datasets

class CustomF1WithThreshold(evaluate.Metric):
    """F1 score with a configurable probability threshold."""

    def _info(self):
        return evaluate.MetricInfo(
            description="F1 score computed with a custom probability threshold.",
            citation="",
            inputs_description="Predictions (probabilities) and references (binary labels).",
            features=datasets.Features({
                "predictions": datasets.Value("float32"),
                "references": datasets.Value("int32"),
            }),
        )

    def _compute(self, predictions, references, threshold=0.5):
        import numpy as np
        binary_preds = [1 if p >= threshold else 0 for p in predictions]

        tp = sum(1 for p, r in zip(binary_preds, references) if p == 1 and r == 1)
        fp = sum(1 for p, r in zip(binary_preds, references) if p == 1 and r == 0)
        fn = sum(1 for p, r in zip(binary_preds, references) if p == 0 and r == 1)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        return {
            "f1": f1,
            "precision": precision,
            "recall": recall,
            "threshold": threshold,
        }

# Use custom metric
metric = CustomF1WithThreshold()
result = metric.compute(
    predictions=[0.9, 0.3, 0.7, 0.1, 0.8],
    references=[1, 0, 1, 0, 1],
    threshold=0.5,
)
```

### 8. Evaluation Pipelines

```python
def full_evaluation_pipeline(
    model_id: str,
    dataset_name: str,
    task: str = "text-classification",
    metrics: list = None,
    split: str = "test",
    batch_size: int = 32,
    save_results: bool = True,
    output_path: str = "./eval_results.json",
):
    """Complete evaluation pipeline with standardized output."""
    import json
    from datetime import datetime
    from transformers import pipeline as hf_pipeline
    from datasets import load_dataset
    import evaluate

    if metrics is None:
        metrics = ["accuracy", "f1", "precision", "recall"]

    # Load data and model
    dataset = load_dataset(dataset_name, split=split)
    pipe = hf_pipeline(task, model=model_id, device_map="auto")

    # Run inference
    predictions = pipe(dataset["text"], batch_size=batch_size)
    pred_labels = [p["label"] for p in predictions]
    references = dataset["label"]

    # Compute metrics
    combined = evaluate.combine(metrics)
    scores = combined.compute(predictions=pred_labels, references=references)

    # Build result object
    result = {
        "model_id": model_id,
        "dataset": dataset_name,
        "split": split,
        "num_examples": len(references),
        "metrics": scores,
        "timestamp": datetime.now().isoformat(),
        "task": task,
    }

    if save_results:
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)

    return result
```

### 9. Leaderboard Submission

#### Open LLM Leaderboard

```bash
# Install lm-evaluation-harness
pip install lm-eval

# Run standard benchmarks
lm_eval --model hf \
    --model_args pretrained=username/my-model \
    --tasks hellaswag,arc_challenge,mmlu,truthfulqa_mc2,winogrande,gsm8k \
    --batch_size auto \
    --output_path ./results \
    --num_fewshot 5

# Submit to leaderboard:
# 1. Push your model to HuggingFace Hub
# 2. Go to https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard
# 3. Click "Submit" and enter your model ID
# 4. Wait for evaluation to complete (hours to days)
```

#### Submit results programmatically

```python
from huggingface_hub import HfApi

api = HfApi()

# Ensure your model card has evaluation results metadata
model_card = """
---
model-index:
  - name: my-model
    results:
      - task:
          type: text-generation
          name: Text Generation
        dataset:
          name: MMLU
          type: cais/mmlu
        metrics:
          - type: accuracy
            value: 72.5
            name: MMLU Accuracy
      - task:
          type: text-generation
        dataset:
          name: HellaSwag
          type: hellaswag
        metrics:
          - type: accuracy
            value: 81.2
            name: HellaSwag Accuracy
---
"""
```

### 10. Reproducibility Best Practices

```python
import os
import json
import random
import numpy as np
import torch
from datetime import datetime

def set_seed(seed: int = 42):
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    # For deterministic CUDA operations (may slow down training)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def log_evaluation_metadata(model_id, dataset_name, results, output_path="eval_log.json"):
    """Log complete evaluation metadata for reproducibility."""
    metadata = {
        "model_id": model_id,
        "dataset": dataset_name,
        "results": results,
        "environment": {
            "python": os.popen("python --version").read().strip(),
            "torch": torch.__version__,
            "transformers": __import__("transformers").__version__,
            "evaluate": __import__("evaluate").__version__,
            "cuda": torch.version.cuda if torch.cuda.is_available() else None,
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        },
        "seed": 42,
        "timestamp": datetime.now().isoformat(),
    }
    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=2)
    return metadata
```

---

## Best Practices

1. **Use `evaluate.combine()`** — Compute multiple metrics in one call for consistency.
2. **Always report confidence intervals** — Use bootstrapping or cross-validation, not single-point estimates.
3. **Standardize preprocessing** — Evaluation results are only comparable with identical preprocessing.
4. **Fix all random seeds** — Set seeds for Python, NumPy, PyTorch, and CUDA.
5. **Log environment metadata** — Record library versions, GPU type, and CUDA version.
6. **Use established benchmarks** — GLUE, SuperGLUE, MMLU allow comparison with published results.
7. **Evaluate on held-out test sets** — Never evaluate on data seen during training.
8. **Report per-class metrics** — Aggregate metrics hide poor performance on minority classes.
9. **Run bias evaluations** — Check model performance across demographic groups.
10. **Use `lm-eval` harness** — Standardized, community-validated evaluation for LLMs.
11. **Version your evaluation code** — Evaluation scripts should be versioned alongside the model.
12. **Document metric choices** — Explain why specific metrics were chosen for the task.

---

## Examples

### Complete evaluation of a text classifier

```python
import evaluate
import numpy as np
from transformers import pipeline
from datasets import load_dataset

# Load
dataset = load_dataset("imdb", split="test[:1000]")
pipe = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

# Predict
preds = pipe(dataset["text"], batch_size=64)
pred_labels = [1 if p["label"] == "POSITIVE" else 0 for p in preds]

# Evaluate
metrics = evaluate.combine(["accuracy", "f1", "precision", "recall"])
results = metrics.compute(predictions=pred_labels, references=dataset["label"])
print(results)
```

### Evaluate a summarization model

```python
import evaluate
from transformers import pipeline
from datasets import load_dataset

dataset = load_dataset("cnn_dailymail", "3.0.0", split="test[:200]")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

summaries = summarizer(dataset["article"], max_length=130, min_length=30, batch_size=8)
predictions = [s["summary_text"] for s in summaries]
references = dataset["highlights"]

rouge = evaluate.load("rouge")
result = rouge.compute(predictions=predictions, references=references)
print(result)  # {'rouge1': ..., 'rouge2': ..., 'rougeL': ..., 'rougeLsum': ...}
```
