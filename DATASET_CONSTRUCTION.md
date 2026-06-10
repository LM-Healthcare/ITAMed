# Dataset Construction Procedure

## Overview

This document describes the end-to-end procedure used to construct the ITAMed dataset, from raw PDF acquisition to the final annotated multilingual dataset.

---

## 1. Source Data Acquisition

**Source**: Official PDF documents from the Italian National Medical Specialization Exam (Concorso SSM), years 2017–2025.

**Format**: Each PDF contains 140 multiple-choice questions with 5 answer options (A–E). The correct answer is always repositioned to option A in the official released documents.

**PDF characteristics**:
- **2017–2019**: Scenario-based format. Questions are grouped under clinical scenarios, with each question explicitly referencing its scenario number.
- **2020–2025**: Standalone format. Each question is self-contained with its own clinical vignette.

---

## 2. Text Extraction

### Tools
- Python 3.x with `pdfplumber` for PDF text extraction
- `openpyxl` for XLSX file generation
- Custom regex-based parsing scripts

### Process

#### Years 2020–2025 (standalone format)
1. Full text extracted from each page of the PDF using `pdfplumber`.
2. Headers and footers (repeated page markers) removed via regex.
3. Questions identified by pattern: `Domanda N: (codice domanda: XXXXX):`
4. Answer options identified by pattern: `A)`, `B)`, `C)`, `D)`, `E)`
5. Each question parsed into structured fields: question number, code, text, and five answer options.

#### Years 2017–2019 (scenario-based format)
1. Same extraction pipeline as above.
2. Additional parsing for scenario blocks: `Scenario N:`
3. Questions referencing a scenario (`riferita allo scenario n.X`) have the full scenario text prepended to the question text, making each question self-contained.
4. Questions without a scenario reference are treated as standalone.

### Validation
- Verified 140 questions extracted per year (1,260 total).
- Checked for empty cells in all fields.
- Manual spot-checks against original PDFs for text fidelity.

---

## 3. Medical Specialty Classification

### Taxonomy
A unified taxonomy of **28 medical specialties** was defined by harmonizing the inconsistent category names used across official distribution documents (available for 2020–2024 only). The taxonomy covers all specialties represented in the Italian medical specialization system.

### Method
- **Model**: Anthropic Claude (claude-opus-4-8)
- **Approach**: Batch classification (10 questions per API request)
- **Prompt design**: The model was instructed to classify each question into exactly one or two categories from the predefined taxonomy, based on the clinical content of the question and answer options.
- **Output**: JSON with category assignments for each question.
- **Validation**: Categories checked against allowed list; fuzzy matching for minor variations; manual review of edge cases.

### Key decisions
- Questions clearly spanning two specialties (e.g., a forensic medicine case involving pediatrics) receive both categories, separated by semicolons.
- The taxonomy was designed to be exhaustive: every question maps to at least one category.
- For years where official distributions exist (2020–2024), our automated classification was cross-referenced with official category counts for consistency.

---

## 4. Image Metadata Annotation

### Source
- **2020–2024**: Image-related questions identified from official distribution documents.
- **2017–2019, 2025**: Image-related questions identified by bold/highlighted formatting in the original PDFs, then verified by inspecting question text for references to figures, images, tracings, or radiographs.

### Image Category Classification
Each image-related question was assigned one of **21 image categories** based on the type of diagnostic image or clinical material referenced:
- Categories determined by analyzing the question text (e.g., "ECG tracing" for electrocardiogram references, "Chest X-ray" for thoracic radiograph references).
- For years 2020–2024, pre-existing category assignments were verified.
- For years 2017–2019 and 2025, categories were assigned manually based on textual analysis of the question content.

---

## 5. Translation (Italian → English)

### Method
- **Model**: Anthropic Claude (claude-opus-4-8)
- **Approach**: Batch translation (5 questions per API request)
- **Prompt design**: The model was configured as an expert medical translator with the following specifications:
  - Use correct English medical terminology (not lay terms)
  - Produce native-level English (not literal translations)
  - Preserve all clinical details (lab values, dosages, anatomical references)
  - Maintain question structure (vignette + stem + 5 options)
  - Follow international medical examination conventions (USMLE-style English)
- **Output**: Complete English versions of all 1,260 questions with all five answer options.

### Quality considerations
- Medical terminology verified against standard English usage (e.g., "infarto miocardico" → "myocardial infarction", not "heart attack").
- Clinical abbreviations preserved where standard in both languages.
- Proper nouns and drug names kept in their international nonproprietary name (INN) form.

---

## 6. Final Dataset Assembly

### Structure
Each question record contains:
1. **Identification**: year, question number (1–140), question code
2. **Content**: question text + 5 answer options (in both IT and EN)
3. **Correct answer**: Always "A"
4. **Classification**: medical specialty (1–2 categories)
5. **Image metadata**: presence flag + image category

### Output formats
- **XLSX**: One file per year (convenient for manual inspection)
- **CSV**: Single file with all 1,260 questions (machine-readable, tabular)
- **JSON**: Single file with all 1,260 questions (structured, API-friendly)

### Folder structure
```
Official/
├── IT/    (Italian: XLSX per year + CSV + JSON)
└── EN/    (English: XLSX per year + CSV + JSON)
```

---

## 7. Tools and Dependencies

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.x | Pipeline orchestration |
| pdfplumber | latest | PDF text extraction |
| openpyxl | latest | XLSX read/write |
| anthropic | 0.42+ | Claude API client |
| matplotlib | 3.9+ | Visualization |
| seaborn | 0.13+ | Statistical plots |

---

## 8. Reproducibility

All scripts used in the construction pipeline are available in the `scripts/` directory:
- `extract_ssm_standalone.py` — Extraction for standalone-format PDFs (2020–2025)
- `extract_ssm_scenario.py` — Extraction for scenario-based PDFs (2017–2019)
- `classify_questions.py` — LLM-based specialty classification
- `translate_questions.py` — LLM-based medical translation (IT→EN)

To reproduce the full pipeline:
```bash
# 1. Extract questions from PDFs
python scripts/extract_ssm_scenario.py     # 2017–2019 (scenario-based)
python scripts/extract_ssm_standalone.py   # 2020–2025 (standalone)

# 2. Classify by medical specialty (requires Anthropic API key)
export ANTHROPIC_API_KEY="sk-ant-..."
python scripts/classify_questions.py

# 3. Translate to English (requires Anthropic API key)
python scripts/translate_questions.py
```

**Note**: Steps 2 and 3 require an Anthropic API key and incur API costs. The classification and translation outputs are provided in the `Official/` directory for direct use without re-running the pipeline.
