---
name: hf-datasets
version: 1.0.0
description: Dataset creation, structuring, validation, and management on the HuggingFace Hub. Use when building, uploading, or optimizing datasets for machine learning training and evaluation pipelines.
tags: [huggingface, datasets, parquet, arrow, csv, json, data, ml, training, versioning, streaming]
author: garri333
license: MIT
source: huggingface/skills
---

# HuggingFace Datasets Skill

## Overview

Use this skill whenever the user needs to create, structure, validate, upload, or manage datasets on the HuggingFace Hub. Covers data formats, metadata, schema definition, streaming, versioning, and optimization for training.

---

## When to Activate

- User wants to create or upload a dataset to HuggingFace Hub.
- User needs to convert data between formats (CSV, JSON, Parquet, Arrow).
- User asks about dataset cards, metadata, or YAML tags.
- User needs to define or validate a dataset schema.
- User wants train/test/validation splits.
- User asks about streaming datasets or large-scale data handling.
- User needs data augmentation or preprocessing strategies.
- User asks about versioning datasets with Git LFS.

---

## Step-by-Step Procedures

### 1. Installation & Setup

```bash
pip install datasets huggingface_hub

# Optional: for audio/image datasets
pip install datasets[audio] datasets[vision]

# For Parquet support
pip install pyarrow
```

### 2. Creating Datasets Programmatically

#### From Python dictionaries

```python
from datasets import Dataset, DatasetDict

# Simple dataset from dict
data = {
    "text": ["Hello world", "HuggingFace is great", "Datasets are powerful"],
    "label": [0, 1, 1],
}
dataset = Dataset.from_dict(data)

# Create train/test splits
dataset_dict = DatasetDict({
    "train": Dataset.from_dict({
        "text": ["example 1", "example 2", "example 3"],
        "label": [0, 1, 0],
    }),
    "test": Dataset.from_dict({
        "text": ["test 1", "test 2"],
        "label": [1, 0],
    }),
})
```

#### From Pandas DataFrame

```python
import pandas as pd
from datasets import Dataset

df = pd.read_csv("data.csv")
dataset = Dataset.from_pandas(df)
```

#### From files (CSV, JSON, Parquet)

```python
from datasets import load_dataset

# From CSV
dataset = load_dataset("csv", data_files="data.csv")

# From multiple CSV files with splits
dataset = load_dataset("csv", data_files={
    "train": "train.csv",
    "test": "test.csv",
    "validation": "val.csv",
})

# From JSON / JSON Lines
dataset = load_dataset("json", data_files="data.jsonl")

# From Parquet
dataset = load_dataset("parquet", data_files="data.parquet")

# From a directory of files
dataset = load_dataset("csv", data_dir="./data/")
```

### 3. Data Structuring & Format Optimization

#### Schema Definition with Features

```python
from datasets import Dataset, Features, Value, ClassLabel, Sequence, Image, Audio

# Define explicit features (schema)
features = Features({
    "id": Value("int32"),
    "text": Value("string"),
    "label": ClassLabel(names=["negative", "neutral", "positive"]),
    "scores": Sequence(Value("float32")),
    "metadata": {
        "source": Value("string"),
        "timestamp": Value("string"),
    },
})

dataset = Dataset.from_dict(data, features=features)
```

#### Image dataset schema

```python
features = Features({
    "image": Image(),
    "label": ClassLabel(names=["cat", "dog", "bird"]),
    "caption": Value("string"),
})
```

#### Audio dataset schema

```python
features = Features({
    "audio": Audio(sampling_rate=16000),
    "transcription": Value("string"),
    "speaker_id": Value("string"),
})
```

#### Format Conversion

```python
# Save as Parquet (recommended for Hub — compact, columnar, fast)
dataset.to_parquet("output/data.parquet")

# Save as CSV
dataset.to_csv("output/data.csv")

# Save as JSON
dataset.to_json("output/data.jsonl")

# Save as Arrow (native format, fastest I/O)
dataset.save_to_disk("output/arrow_dataset/")
```

**Format comparison:**

| Format  | Size  | Load Speed | Streaming | Hub Default |
|---------|-------|------------|-----------|-------------|
| Parquet | Small | Fast       | ✅ Yes    | ✅ Yes      |
| Arrow   | Medium| Fastest    | ❌ No     | ❌ No       |
| CSV     | Large | Slow       | ✅ Yes    | ❌ No       |
| JSON(L) | Large | Medium     | ✅ Yes    | ❌ No       |

### 4. Train/Test/Validation Splits

```python
# Automatic random split
dataset = dataset.train_test_split(test_size=0.2, seed=42)
# Returns DatasetDict with 'train' and 'test'

# Three-way split
train_test = dataset.train_test_split(test_size=0.2, seed=42)
train_val = train_test["train"].train_test_split(test_size=0.125, seed=42)  # 0.125 * 0.8 = 0.1

dataset_dict = DatasetDict({
    "train": train_val["train"],       # 70%
    "validation": train_val["test"],   # 10%
    "test": train_test["test"],        # 20%
})

# Stratified split (preserves label distribution)
dataset = dataset.train_test_split(test_size=0.2, seed=42, stratify_by_column="label")
```

### 5. Data Validation & Quality

```python
# Inspect dataset
print(dataset)
print(dataset.features)
print(dataset.column_names)
print(dataset.num_rows)

# Check for nulls
import pandas as pd
df = dataset.to_pandas()
print(df.isnull().sum())

# Validate label distribution
from collections import Counter
print(Counter(dataset["label"]))

# Remove duplicates
dataset = dataset.filter(
    lambda example, idx: idx == 0 or example["text"] not in dataset[:idx]["text"],
    with_indices=True,
)
# Or more efficiently:
df = dataset.to_pandas()
df = df.drop_duplicates(subset=["text"])
dataset = Dataset.from_pandas(df)

# Filter invalid rows
dataset = dataset.filter(lambda x: x["text"] is not None and len(x["text"].strip()) > 0)
```

### 6. Dataset Card (README.md Metadata)

Every dataset repo must include a `README.md` with YAML frontmatter:

```markdown
---
language:
  - en
  - es
license: mit
task_categories:
  - text-classification
  - token-classification
task_ids:
  - sentiment-analysis
size_categories:
  - 10K<n<100K
tags:
  - nlp
  - sentiment
  - curated
pretty_name: My Sentiment Dataset
dataset_info:
  features:
    - name: text
      dtype: string
    - name: label
      dtype:
        class_label:
          names:
            '0': negative
            '1': neutral
            '2': positive
  splits:
    - name: train
      num_examples: 8000
    - name: test
      num_examples: 2000
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/train-*
      - split: test
        path: data/test-*
---

# My Sentiment Dataset

## Dataset Description

A curated sentiment analysis dataset covering product reviews in English and Spanish.

### Supported Tasks
- **Sentiment Analysis**: Classify text as negative, neutral, or positive.

### Languages
English (`en`), Spanish (`es`)

## Dataset Structure

### Data Fields
- `text` (string): The review text.
- `label` (ClassLabel): Sentiment label — 0 (negative), 1 (neutral), 2 (positive).

## Dataset Creation

### Curation Rationale
[Describe why the dataset was created]

### Source Data
[Describe the source]

### Annotations
[Describe how labels were assigned]

## Considerations for Using the Data

### Social Impact
[Considerations]

### Bias
[Known biases]

## Citation

```bibtex
@dataset{my_sentiment_2026,
  title={My Sentiment Dataset},
  author={Author Name},
  year={2026}
}
```
```

### 7. Uploading to HuggingFace Hub

```python
from datasets import DatasetDict

# Push directly from Python
dataset_dict.push_to_hub(
    "username/my-dataset",
    private=True,
    commit_message="Initial dataset upload",
)

# Push with specific config name
dataset_dict.push_to_hub(
    "username/my-dataset",
    config_name="v1",
)
```

```bash
# Or via CLI
huggingface-cli upload username/my-dataset ./data --repo-type dataset \
  --commit-message "Upload raw dataset files"
```

### 8. Streaming Support

```python
# Load dataset in streaming mode (no full download)
from datasets import load_dataset

dataset = load_dataset("username/my-dataset", streaming=True)

# Iterate without loading everything into memory
for example in dataset["train"]:
    process(example)

# Apply transformations in streaming mode
dataset = dataset.map(lambda x: {"text_lower": x["text"].lower()})
dataset = dataset.filter(lambda x: len(x["text"]) > 10)

# Take first N examples
first_100 = list(dataset["train"].take(100))
```

### 9. Versioning with Git LFS

```bash
# Initialize Git LFS in a dataset repo
git lfs install

# Track large files
git lfs track "*.parquet"
git lfs track "*.arrow"
git lfs track "*.csv"
git lfs track "*.tar.gz"

# Commit and push
git add .gitattributes
git add data/
git commit -m "Add dataset v1.0"
git push

# Create a version tag
git tag v1.0
git push --tags

# Use branches for experimental versions
git checkout -b experiment/augmented-v2
```

### 10. Data Augmentation Strategies

```python
# Text augmentation with nlpaug
import nlpaug.augmenter.word as naw

aug = naw.SynonymAug(aug_src="wordnet")

def augment_text(example):
    example["text_augmented"] = aug.augment(example["text"])[0]
    return example

augmented = dataset.map(augment_text)

# Back-translation augmentation
from transformers import pipeline

translator_en_fr = pipeline("translation_en_to_fr", model="Helsinki-NLP/opus-mt-en-fr")
translator_fr_en = pipeline("translation_fr_to_en", model="Helsinki-NLP/opus-mt-fr-en")

def back_translate(example):
    fr = translator_en_fr(example["text"], max_length=512)[0]["translation_text"]
    back = translator_fr_en(fr, max_length=512)[0]["translation_text"]
    example["text_augmented"] = back
    return example

# Image augmentation with torchvision
from torchvision import transforms

augment_transform = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
])
```

---

## Best Practices

1. **Use Parquet format** — It's the Hub default, columnar, compressed, and supports streaming.
2. **Always write a dataset card** — Include task categories, language, license, features, and splits in YAML.
3. **Define explicit features** — Avoid relying on auto-inference; declare `Features` with types.
4. **Stratify splits** — Use `stratify_by_column` to preserve class distribution across splits.
5. **Validate before uploading** — Check for nulls, duplicates, label balance, and encoding issues.
6. **Version your data** — Use Git tags for releases and branches for experiments.
7. **Enable streaming** — Structure data so `streaming=True` works (Parquet files, sharded).
8. **Shard large datasets** — Split into multiple Parquet files (e.g., 500MB each) for parallel loading.
9. **Use `seed` in splits** — Ensure reproducibility with a fixed random seed.
10. **Document preprocessing** — Include how raw data was cleaned and transformed in the dataset card.

---

## Examples

### End-to-end text classification dataset

```python
from datasets import Dataset, DatasetDict, Features, Value, ClassLabel

features = Features({
    "text": Value("string"),
    "label": ClassLabel(names=["spam", "ham"]),
})

train_data = {"text": [...], "label": [...]}
test_data = {"text": [...], "label": [...]}

ds = DatasetDict({
    "train": Dataset.from_dict(train_data, features=features),
    "test": Dataset.from_dict(test_data, features=features),
})

# Validate
print(ds)
print(ds["train"].features)

# Upload
ds.push_to_hub("username/spam-detector-dataset", private=False)
```

### Large-scale sharded upload

```python
import pandas as pd
from datasets import Dataset

# Process in chunks and save as sharded Parquet
for i, chunk in enumerate(pd.read_csv("huge_data.csv", chunksize=500_000)):
    ds = Dataset.from_pandas(chunk)
    ds.to_parquet(f"data/train-{i:05d}-of-00020.parquet")

# Upload the data directory
from huggingface_hub import HfApi
api = HfApi()
api.upload_folder(
    folder_path="data",
    repo_id="username/large-dataset",
    repo_type="dataset",
    path_in_repo="data",
)
```
