# ITAMed — Bilingual Italian–English dataset of clinical case questions from medical specialization exams

## Overview

**ITAMed** is a comprehensive, bilingual (Italian/English) dataset of **1,260 multiple-choice clinical case questions** from the Italian National Medical Specialization Entrance Exam (*Concorso per l'accesso alle Scuole di Specializzazione in Medicina e Chirurgia*, SSM), administered annually by the Italian Ministry of University and Research (MUR). The dataset spans **nine consecutive years** (2017–2025), with 140 questions per year.

Each question consists of a clinical vignette followed by a stem and five answer options, of which one is correct. The dataset provides structured, machine-readable annotations including medical specialty classification (28-category taxonomy), image metadata (presence flag, image category, and file path), and a professionally reviewed English translation of the full content.

The specialty classification was performed using a dual-annotator LLM protocol (Claude Opus 4.8 and GPT-5.5) achieving a primary-category Cohen's kappa of 0.8950, with all disagreements resolved through independent adjudication by two medical specialists. The English translation was produced by Claude Opus 4.8 and subsequently reviewed in its entirety by a senior bilingual physician.

## Citation

If you use this dataset, please cite:

**Data Descriptor:**
```bibtex
@article{bianchini2026itamed,
  title   = {A bilingual Italian and English dataset of clinical case questions from medical specialization exams},
  author  = {Bianchini, Filippo and Bianchini, Edoardo and Bianchini, Emiliano and Marano, Massimo and Mecella, Massimo and Vuillerme, Nicolas},
  journal = {Scientific Data},
  year    = {2026},
  doi     = {[DOI to be added upon publication]}
}
```

**Dataset (Zenodo):**
```bibtex
@dataset{bianchini2026itamed_data,
  title     = {ITAMed: a bilingual Italian and English dataset of clinical case questions from medical specialization exams},
  author    = {Bianchini, Filippo and Bianchini, Edoardo and Bianchini, Emiliano and Marano, Massimo and Mecella, Massimo and Vuillerme, Nicolas},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.XXXXXXX}
}
```

## License

- **Data** (Dataset/, Source_documents/, Translation_review/, Classification_review/): Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Original examination questions**: public domain (Article 5, Italian Law 633/1941 — official acts of the State are not subject to copyright)

The English translations, the specialty and image annotations, the structured tabular and JSON organisation of the data, and the accompanying documentation are original contributions of the authors and are released under CC BY 4.0.

Full license text: https://creativecommons.org/licenses/by/4.0/legalcode

## Repository structure

```
ITAMed/
├── Dataset/                              # Final dataset (ready to use)
│   ├── IT/
│   │   ├── xlsx/                         #   Italian XLSX (per-year + complete)
│   │   ├── json/                         #   Italian JSON (per-year + complete)
│   │   └── ITAMed_Distribution_IT.xlsx   #   Category & image distribution (IT)
│   ├── EN/
│   │   ├── xlsx/                         #   English XLSX (per-year + complete)
│   │   ├── json/                         #   English JSON (per-year + complete)
│   │   └── ITAMed_Distribution_EN.xlsx   #   Category & image distribution (EN)
│   └── images/                           #   Extracted question images by year
│
├── Data_Extraction/                      # PDF sources & extraction scripts
│   ├── README.md                         #   Extraction methodology
│   ├── pdf_sources/                      #   Official SSM exam PDFs (2017–2025)
│   └── scripts/                          #   PDF → structured data extractors
│
├── Question_Classification/              # Dual-annotator classification module
│   ├── README.md                         #   Full methodology & results (κ=0.8950)
│   ├── scripts/                          #   Classification & agreement scripts
│   ├── results/                          #   Claude, GPT, and agreement outputs
│   └── expert_review/                    #   Expert adjudication workflow
│
├── Dataset_Translation/                  # Translation module (IT→EN)
│   ├── README.md                         #   Translation methodology & review process
│   ├── scripts/                          #   Translation & review-application scripts
│   ├── translation_corrections.json      #   Structured log of expert corrections
│   └── ITAMed_complete_EN_tracked.xlsx   #   Translation corrections (highlighted)
│
├── Charts/                               # Distribution visualizations (IT)
├── Charts_EN/                            # Distribution visualizations (EN)
│
└── README.md                             # Main repository README
```

## Dataset schema

| Field | Type | Description |
|:------|:-----|:------------|
| Year | int | Exam year (2017–2025) |
| Question Number | int | Position within year (1–140) |
| Question Code | str | Official unique identifier (e.g., `ssm20203811854`) |
| Question | str | Clinical vignette + question stem |
| Answer A | str | **Always the correct answer** |
| Answer B–E | str | Distractor options (4 incorrect alternatives) |
| Correct Answer | str | Always `"A"` |
| Category | str | Medical specialty (1–2 categories, semicolon-separated) |
| Image | str/bool | Whether the question includes a figure |
| Image Category | str | Diagnostic image type (21-category taxonomy) |
| Image Path | str | Relative path to image file |

## Provenance and processing

- **Source**: official examinations of the Italian *Concorso SSM*, 2017–2025
- **Extraction**: automated via Python pipeline (pdfplumber)
- **Specialty classification**: dual-LLM protocol (Claude Opus 4.8 + GPT-5.5) with expert adjudication by two physicians
- **Image categorisation**: joint expert review by two physicians
- **Translation**: initial LLM draft by Claude Opus 4.8, followed by full expert review by a senior bilingual physician

For full methodological details, see the Data Descriptor paper.

## How to load the dataset

### Python — JSON

```python
import json

# Load complete dataset (all years)
with open("Dataset/EN/json/ITAMed_complete_EN.json", encoding="utf-8") as f:
    dataset = json.load(f)

print(f"Total questions: {len(dataset)}")
print(dataset[0]["question"])

# Load a single year
with open("Dataset/IT/json/ITAMed_2020.json", encoding="utf-8") as f:
    year_2020 = json.load(f)
```

### Python — XLSX (pandas)

```python
import pandas as pd

# Load complete Italian dataset
df = pd.read_excel("Dataset/IT/xlsx/ITAMed_complete.xlsx")
print(df.shape)  # (1260, 11)

# Load complete English dataset
df_en = pd.read_excel("Dataset/EN/xlsx/ITAMed_complete_EN.xlsx")

# Filter by specialty
cardiology = df_en[df_en["Category"].str.contains("Cardiology")]
```

### HuggingFace

```python
from datasets import load_dataset

dataset = load_dataset("Filo-White/ITAMed", split="train")
```

## Related resources

- **Code repository (GitHub)**: https://github.com/LM-Healthcare/ITAMed
- **HuggingFace mirror**: https://huggingface.co/datasets/Filo-White/ITAMed
- **Data Descriptor paper**: [DOI to be added upon publication]

## Contact

- **Corresponding author**: Filippo Bianchini — filippo.bianchini@uniroma1.it
- **GitHub**: [@Filo-White](https://github.com/Filo-White)

## Version history

- **v1.0.0** (2026): initial release corresponding to the Data Descriptor paper
