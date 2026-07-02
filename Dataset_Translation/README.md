# Dataset Translation (Italian → English)

## Overview

This module contains the full translation pipeline used to produce the English version of the ITAMed dataset. All 1,260 medical exam questions (2017–2025) were translated from Italian to English, including clinical vignettes, question stems, and all five answer options.

---

## Translation Process

### Step 1 — Automated Translation (Claude)

The initial translation was performed using **Anthropic Claude (claude-opus-4-8)**, configured as an expert medical translator. The model was instructed to:

- Use correct English medical terminology (e.g., *infarto miocardico* → *myocardial infarction*, not *heart attack*)
- Produce native-level English, not literal translations
- Preserve all clinical details: lab values, dosages, anatomical references, temporal relationships
- Maintain the original question structure (vignette + stem + 5 options A–E)
- Follow international medical examination conventions (USMLE-style English)

Translation was performed in batches of 5 questions per API request, with intermediate results saved for resume support.

### Step 2 — Expert Medical Review

The complete English translation was reviewed by a bilingual medical professional (native Italian, fluent English) with clinical expertise. The reviewer examined each of the 1,260 questions individually, checking:

- **Semantic fidelity** — The English preserves the exact clinical meaning of the Italian source, without omissions, additions, or reinterpretation
- **Medical terminology** — Diagnoses, symptoms, procedures, drugs, and clinical concepts use accurate and standard English medical terms
- **Negation, temporality, and causality** — Negations, absence/presence statements, temporal sequences, and causal relationships are faithfully preserved
- **Numerical accuracy** — All lab values, dosages, frequencies, percentages, ranges, and measurements are correctly transferred
- **Grammar and fluency** — Grammatical correctness while maintaining a neutral, professional medical register
- **Terminological consistency** — Consistent use of medical terms across the entire dataset

Where corrections were needed, the revised text was recorded in the designated columns of the review file alongside a brief note describing the change. Questions with accurate translations were left unchanged.

### Step 3 — Applying Corrections to the Dataset

After the expert completed the review, the corrections were:

1. **Extracted** from the reviewed XLSX into a structured JSON file (`translation_corrections.json`) documenting all modifications
2. **Applied** to the official EN dataset files (per-year XLSX and JSON, plus the complete files)
3. **Tracked** in a dedicated XLSX file (`Dataset/EN/ITAMed_complete_EN_tracked.xlsx`) where modified cells are highlighted in yellow with cell comments showing the original pre-correction text — analogous to Word's track-changes feature

This process is fully automated by the `apply_translation_review.py` script.

---

## Review Summary

| Field | Corrections |
|:------|:-----------:|
| Question text | 305 |
| Answer A | 61 |
| Answer B | 57 |
| Answer C | 53 |
| Answer D | 40 |
| Answer E | 55 |
| **Total corrections** | **571** |
| **Questions modified (out of 1,260)** | **431** |
| Questions unchanged | 829 |

---

## Files

| File | Description |
|:-----|:------------|
| `ITAMed_complete_EN_translation_TO_CHECK.xlsx` | English translation with review columns: corrected text (where applicable) and reviewer notes |
| `translation_corrections.json` | Structured log of all corrections extracted from the reviewed file |

### Review Columns in the XLSX File

| Column | Content |
|:-------|:--------|
| A–I | Original English translation (Year, Question Number, Code, Question, Answers A–E) |
| J | Question checked — revised question text (blank if no change needed) |
| K–O | Answer A–E checked — revised answer text (blank if no change needed) |
| P | Additional comment — brief note on what was corrected |

---

## Scripts

| Script | Description |
|:-------|:------------|
| `scripts/translate_questions.py` | Automated IT→EN translation using Claude API (Step 1) |
| `scripts/apply_translation_review.py` | Extract corrections from reviewed XLSX → generate JSON → apply to dataset → produce tracked-changes file (Step 3) |

### Running the Translation

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python Dataset_Translation/scripts/translate_questions.py
```

### Applying Expert Corrections

```bash
python Dataset_Translation/scripts/apply_translation_review.py
```

The script performs the following steps:
1. Reads the reviewed file and extracts all corrections into `translation_corrections.json`
2. Creates a backup of the current EN dataset files
3. Generates the tracked-changes XLSX (`Dataset/EN/ITAMed_complete_EN_tracked.xlsx`)
4. Applies corrections to all per-year and complete EN files (XLSX + JSON)

---

## Output

After running the full pipeline, the corrected English dataset is available in:

- `Dataset/EN/xlsx/` — per-year and complete XLSX files (clean, final version)
- `Dataset/EN/json/` — per-year and complete JSON files (clean, final version)
- `Dataset/EN/ITAMed_complete_EN_tracked.xlsx` — tracked-changes version with highlighted corrections and original text in comments
