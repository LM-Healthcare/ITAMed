---
language:
  - it
  - en
license: cc-by-4.0
size_categories:
  - 1K<n<10K
task_categories:
  - question-answering
  - multiple-choice
tags:
  - medical
  - clinical
  - exam
  - italian
  - bilingual
  - multimodal
  - mcq
  - benchmark
  - ssm
  - specialization
pretty_name: ITAMed - Italian Medical Specialization Exam Dataset
dataset_info:
  features:
    - name: year
      dtype: int32
    - name: question_number
      dtype: int32
    - name: question_code
      dtype: string
    - name: question
      dtype: string
    - name: answer_a
      dtype: string
    - name: answer_b
      dtype: string
    - name: answer_c
      dtype: string
    - name: answer_d
      dtype: string
    - name: answer_e
      dtype: string
    - name: correct_answer
      dtype: string
    - name: category
      dtype: string
    - name: has_image
      dtype: bool
    - name: image_category
      dtype: string
    - name: image_path
      dtype: string
  splits:
    - name: train
      num_examples: 1260
  config_name: default
configs:
  - config_name: it
    data_files: "data/ITAMed_IT.json"
    default: true
  - config_name: en
    data_files: "data/ITAMed_EN.json"
---

# ITAMed: Italian Medical Specialization Exam Dataset (2017–2025)

<p align="center">
  <a href="https://github.com/LM-Healthcare/ITAMed"><img src="https://img.shields.io/badge/GitHub-Repository-black?logo=github" alt="GitHub"/></a>
  <a href="https://huggingface.co/spaces/Filo-White/ITAMed-Explorer"><img src="https://img.shields.io/badge/🤗-Interactive%20Demo-orange" alt="Demo"/></a>
  <a href="#citation"><img src="https://img.shields.io/badge/Scientific%20Data-paper-blue" alt="Paper"/></a>
</p>

## Dataset Description

**ITAMed** is a comprehensive, bilingual dataset of **1,260 multiple-choice medical questions** from the Italian National Medical Specialization Entrance Exam (*Concorso SSM*), spanning 9 consecutive years (2017–2025).

### Key Features

- **1,260 questions** — 140 per year across 9 years
- **Bilingual** — Original Italian + expert English translation
- **28 medical specialties** — Standardized taxonomy with per-question classification
- **76 image-bearing questions** — With 21 image-type categories and extracted images
- **Ready for benchmarking** — Standard MCQ format compatible with LLM evaluation frameworks

## Quick Start

```python
from datasets import load_dataset

# Load Italian version (default)
dataset = load_dataset("Filo-White/ITAMed", "it")

# Load English version
dataset_en = load_dataset("Filo-White/ITAMed", "en")

# Filter examples
cardiology = dataset["train"].filter(lambda x: "Cardiology" in x["category"])
year_2024 = dataset["train"].filter(lambda x: x["year"] == 2024)
with_images = dataset["train"].filter(lambda x: x["has_image"])
```

## Dataset Schema

| Field | Type | Description |
|:------|:-----|:------------|
| `year` | `int` | Exam year (2017–2025) |
| `question_number` | `int` | Position within the year (1–140) |
| `question_code` | `string` | Official unique question identifier |
| `question` | `string` | Full question text (clinical vignette + stem) |
| `answer_a` | `string` | Answer option A (**always correct**) |
| `answer_b` – `answer_e` | `string` | Distractor options |
| `correct_answer` | `string` | Always `"A"` |
| `category` | `string` | Medical specialty (1–2, semicolon-separated) |
| `has_image` | `bool` | Whether the question references an image |
| `image_category` | `string` | Type of diagnostic image (21 categories) |
| `image_path` | `string` | Relative path to image file |

## Statistics

| Metric | Value |
|:-------|------:|
| Total questions | 1,260 |
| Years covered | 2017–2025 |
| Questions per year | 140 |
| Questions with images | 76 (6.0%) |
| Medical specialties | 28 |
| Image categories | 21 |
| Languages | IT + EN |

### Yearly Image Distribution

| Year | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|:-----|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|
| Images | 14 | 9 | 5 | 6 | 6 | 4 | 11 | 8 | 13 |

## Data Source

Questions were extracted from the official PDF documents of the Italian National Medical Specialization Entrance Exam, administered annually by the Italian Ministry of University and Research (MUR).

- **2017–2019**: Scenario-based format (questions grouped under shared clinical scenarios)
- **2020–2025**: Standalone format (self-contained questions)
- **Correct answer**: Always option A (as per official released PDF format)

## Construction Pipeline

1. **PDF Extraction** — Automated text extraction using `pdfplumber` with custom regex parsers
2. **Specialty Classification** — LLM-based classification (Claude claude-opus-4-8) into 28 medical categories
3. **Image Annotation** — Manual identification and categorization of image-bearing questions
4. **Translation** — LLM-based medical translation (Claude claude-opus-4-8, IT→EN)
5. **Quality Control** — Manual review and validation against official source documents

Full methodology documented in each module's README: [Data_Extraction](https://github.com/LM-Healthcare/ITAMed/tree/main/Data_Extraction), [Question_Classification](https://github.com/LM-Healthcare/ITAMed/tree/main/Question_Classification), [Dataset_Translation](https://github.com/LM-Healthcare/ITAMed/tree/main/Dataset_Translation)

## Use Cases

- **LLM Medical Benchmarking** — Evaluate language models on real clinical exam questions
- **Cross-lingual Medical NLP** — Compare model performance across Italian and English
- **Medical Education Research** — Analyze question difficulty, topic distribution, and trends
- **Multimodal Medical AI** — Evaluate vision-language models on image-bearing questions

## Limitations

- The correct answer is always in position A. For benchmarking, answer positions should be **shuffled** before evaluation to prevent position bias.
- Image-bearing questions (6%) require the associated image for complete understanding.
- Translation was performed by an LLM; while quality was reviewed, some nuances may differ from human medical translation.

## Citation

```bibtex
@article{itamed2025,
  title   = {ITAMed: A Comprehensive Bilingual Dataset of Italian Medical Specialization Exam Questions (2017--2025)},
  author  = {[Authors]},
  journal = {Scientific Data},
  year    = {2025},
  doi     = {[to be assigned]}
}
```

## License

CC BY 4.0
