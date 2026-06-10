<p align="center">
  <h1 align="center">ITAMed</h1>
  <p align="center">
    <strong>Italian Medical Specialization Exam Dataset (2017–2025)</strong>
  </p>
  <p align="center">
    <a href="https://huggingface.co/datasets/Filo-White/ITAMed"><img src="https://img.shields.io/badge/🤗%20HuggingFace-Dataset-yellow" alt="HuggingFace Dataset"/></a>
    <a href="https://huggingface.co/spaces/Filo-White/ITAMed-Explorer"><img src="https://img.shields.io/badge/🤗%20HuggingFace-Demo-orange" alt="HuggingFace Demo"/></a>
    <a href="#citation"><img src="https://img.shields.io/badge/Scientific%20Data-paper-blue" alt="Paper"/></a>
    <a href="#license"><img src="https://img.shields.io/badge/License-TBD-lightgrey" alt="License"/></a>
  </p>
</p>

---

## Overview

**ITAMed** is a comprehensive, bilingual (Italian/English) dataset of **1,260 multiple-choice medical questions** from the Italian National Medical Specialization Entrance Exam (*Concorso SSM — Scuole di Specializzazione in Medicina*), spanning **9 consecutive years** (2017–2025, 140 questions/year).

Every question is enriched with:
- **Medical specialty classification** across a standardized taxonomy of 28 categories
- **Image metadata** — presence flag, image type (21 categories), and file path to the extracted image
- **Bilingual text** — original Italian + English translation produced by Claude (claude-opus-4-8)

### Quick Start

```python
# Via HuggingFace
from datasets import load_dataset

dataset = load_dataset("Filo-White/ITAMed", split="train")

# Filter by year, specialty, or image presence
cardiology = dataset.filter(lambda x: "Cardiology" in x["category"])
with_images = dataset.filter(lambda x: x["has_image"])
```

---

## Repository Structure

```
ITAMed/
├── Official/                          # Final dataset (ready to use)
│   ├── IT/                            #   Italian — XLSX per year + complete XLSX/JSON
│   ├── EN/                            #   English — XLSX per year + complete XLSX/JSON
│   ├── images/                        #   Extracted question images, organized by year
│   ├── ITAMed_Distribution.xlsx       #   Category & image distribution tables (IT)
│   └── ITAMed_Distribution_EN.xlsx    #   Category & image distribution tables (EN)
│
├── Pdf_Data/                          # Source PDFs (official SSM exams)
│
├── scripts/                           # Reproducible pipeline
│   ├── extract_ssm_standalone.py      #   PDF → structured data (2020–2025)
│   ├── extract_ssm_scenario.py        #   PDF → structured data (2017–2019)
│   ├── classify_questions.py          #   LLM-based specialty classification
│   └── translate_questions.py         #   LLM-based IT→EN medical translation
│
├── Charts/                            # Distribution visualizations (IT)
├── Charts_EN/                         # Distribution visualizations (EN)
│
├── DATASET_CONSTRUCTION.md            # Full construction methodology
└── README.md                          # This file
```

---

## Dataset Schema

| Field | IT Column | EN Column | Type | Description |
|:------|:----------|:----------|:-----|:------------|
| Year | `Anno` | `Year` | int | Exam year (2017–2025) |
| Question Number | `Numero Domanda` | `Question Number` | int | Position within year (1–140) |
| Question Code | `Codice Domanda` | `Question Code` | str | Official unique identifier |
| Question | `Domanda` | `Question` | str | Clinical vignette + question stem |
| Answer A | `Risposta A` | `Answer A` | str | **Always the correct answer** |
| Answer B–E | `Risposta B–E` | `Answer B–E` | str | Distractor options |
| Correct Answer | `Risposta Corretta` | `Correct Answer` | str | Always `"A"` |
| Category | `Categoria` | `Category` | str | Medical specialty (1–2, semicolon-separated) |
| Image | `Immagine` | `Image` | str | `Si`/`No` (IT) or `Yes`/`No` (EN) |
| Image Category | `Categoria Immagine` | `Image Category` | str | Diagnostic image type |
| Image Path | `Percorso Immagine` | `Image Path` | str | Relative path to image file |

---

## Medical Specialty Categories (28)

<details>
<summary>Click to expand full taxonomy</summary>

| # | Italian | English |
|:-:|:--------|:--------|
| 1 | Anestesia e Rianimazione | Anesthesia and Intensive Care |
| 2 | Cardiologia e Cardiochirurgia | Cardiology and Cardiac Surgery |
| 3 | Chirurgia Generale | General Surgery |
| 4 | Dermatologia e Venereologia | Dermatology and Venereology |
| 5 | Diagnostica per Immagini e Medicina Nucleare | Diagnostic Imaging and Nuclear Medicine |
| 6 | Ematologia | Hematology |
| 7 | Endocrinologia | Endocrinology |
| 8 | Farmacologia e Tossicologia | Pharmacology and Toxicology |
| 9 | Gastroenterologia | Gastroenterology |
| 10 | Genetica Medica | Medical Genetics |
| 11 | Ginecologia e Ostetricia | Gynecology and Obstetrics |
| 12 | Igiene, Epidemiologia e Statistica | Hygiene, Epidemiology and Statistics |
| 13 | Immunologia e Reumatologia | Immunology and Rheumatology |
| 14 | Malattie Infettive | Infectious Diseases |
| 15 | Medicina del Lavoro | Occupational Medicine |
| 16 | Medicina Interna | Internal Medicine |
| 17 | Medicina Legale | Forensic Medicine |
| 18 | Nefrologia | Nephrology |
| 19 | Neurologia e Neurochirurgia | Neurology and Neurosurgery |
| 20 | Nutrizione Clinica | Clinical Nutrition |
| 21 | Oftalmologia | Ophthalmology |
| 22 | Oncologia | Oncology |
| 23 | Ortopedia e Traumatologia | Orthopedics and Traumatology |
| 24 | Otorinolaringoiatria | Otorhinolaryngology |
| 25 | Pediatria | Pediatrics |
| 26 | Pneumologia e Chirurgia Toracica | Pulmonology and Thoracic Surgery |
| 27 | Psichiatria | Psychiatry |
| 28 | Urologia | Urology |

</details>

## Image Categories (21)

<details>
<summary>Click to expand image taxonomy</summary>

| Category | Example Context |
|:---------|:----------------|
| Audiometry report | Otorhinolaryngology hearing assessment |
| Brain CT scan | Neurological emergency imaging |
| Brain MRI | Neurology/neurosurgery diagnostic |
| Chest CT scan | Pulmonary/thoracic evaluation |
| Chest X-ray | Cardiopulmonary assessment |
| Clinical study table | Epidemiology/statistics questions |
| ECG tracing | Cardiology rhythm analysis |
| Endoscopic image | Gastroenterology/pulmonology procedures |
| Forensic photograph | Forensic medicine cases |
| Fundus examination | Ophthalmology retinal assessment |
| Histological image | Pathology tissue analysis |
| Knee arthroscopy image and knee MRI | Orthopedic evaluation |
| Lower limb X-ray | Orthopedic/traumatology assessment |
| Otoscopic image | Otorhinolaryngology ear examination |
| Pelvic X-ray | Orthopedic/gynecological imaging |
| Peripheral blood smear | Hematology microscopy |
| Photograph of a skin lesion | Dermatology clinical assessment |
| Radiological image | General diagnostic imaging |
| Spine MRI | Neurosurgery/orthopedic evaluation |
| Spirometry report | Pulmonology functional testing |
| Upper limb X-ray | Orthopedic/traumatology assessment |

</details>

---

## Key Statistics

| Metric | Value |
|:-------|------:|
| Total questions | 1,260 |
| Years covered | 2017–2025 (9 years) |
| Questions per year | 140 |
| Questions with images | 76 (6.0%) |
| Medical specialty categories | 28 |
| Image categories | 21 |
| Languages | Italian (original) + English (translated) |

---

## Data Source

Questions were extracted from the official PDF documents of the Italian National Medical Specialization Entrance Exam (*Concorso per l'ammissione alle Scuole di Specializzazione in Medicina e Chirurgia*), administered annually by the Italian Ministry of University and Research (MUR).

**Key characteristics:**
- **2017–2019**: Scenario-based format — questions grouped under shared clinical scenarios
- **2020–2025**: Standalone format — each question self-contained
- **All years**: Correct answer always in position A (official release format)
- **2023**: Unique PDF format (no word spacing, commentary blocks)

---

## Reproducibility

The full pipeline is documented in [`DATASET_CONSTRUCTION.md`](DATASET_CONSTRUCTION.md) and all scripts are provided in the `scripts/` directory.

```bash
# 1. Extract questions from official PDFs
python scripts/extract_ssm_scenario.py     # 2017–2019
python scripts/extract_ssm_standalone.py   # 2020–2025

# 2. Classify by medical specialty (requires Anthropic API key)
export ANTHROPIC_API_KEY="sk-ant-..."
python scripts/classify_questions.py

# 3. Translate to English (requires Anthropic API key)
python scripts/translate_questions.py
```

### Requirements

```
pdfplumber
openpyxl
anthropic>=0.42
```

---

## Related Work

| Project | Description |
|:--------|:------------|
| [LLM-EVAL-Education](https://github.com/LM-Healthcare/LLM-EVAL-Education) | Benchmarking LLMs on SSM 2020–2024 (closed, open, quantized) |
| [AURORA](https://github.com/LM-Healthcare/AURORA) | On-premise clinical assistant for structured remote anamnesis |
| [LLM_DEMENTIA](https://github.com/LM-Healthcare/LLM_DEMENTIA) | LLM-based dementia diagnosis with incremental clinical evidence |

---

## Citation

If you use this dataset, please cite:

```bibtex
@article{itamed2025,
  title   = {ITAMed: A Comprehensive Bilingual Dataset of Italian Medical Specialization Exam Questions (2017--2025)},
  author  = {[Authors]},
  journal = {Scientific Data},
  year    = {2025},
  doi     = {[to be assigned]}
}
```

---

## License

[To be determined]

---

## Contact

- **GitHub**: [@Filo-White](https://github.com/Filo-White)
- **HuggingFace**: [Filo-White](https://huggingface.co/Filo-White)
