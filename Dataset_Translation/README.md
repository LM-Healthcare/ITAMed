# Dataset Translation (Italian → English)

## Overview

This module contains the translation pipeline used to produce the English version of the ITAMed dataset. All 1,260 medical exam questions (2017–2025) were translated from Italian to English, including clinical vignettes, question stems, and all five answer options.

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

The complete English translation was reviewed by a bilingual medical professional (native Italian, fluent English) with clinical expertise. The review covered:

- **Semantic fidelity** — Ensuring the English preserves the exact clinical meaning of the Italian source, without omissions, additions, or reinterpretation
- **Medical terminology** — Verifying that diagnoses, symptoms, procedures, drugs, and clinical concepts use accurate and standard English medical terms
- **Negation, temporality, and causality** — Checking that negations, absence/presence statements, temporal sequences, and causal relationships are faithfully preserved
- **Numerical accuracy** — Confirming that all lab values, dosages, frequencies, percentages, ranges, and measurements are correctly transferred
- **Grammar and fluency** — Correcting any grammatical issues while maintaining a neutral, professional medical register
- **Terminological consistency** — Ensuring consistent use of medical terms across the entire dataset

The reviewer examined each of the 1,260 questions individually. Where corrections were needed, the revised text was recorded alongside a brief note describing the change. Questions with accurate translations were left unchanged.

---

## Files

| File | Description |
|:-----|:------------|
| `ITAMed_complete_IT_base_for_translation.xlsx` | Italian source dataset (1,260 questions) used as input for translation |
| `ITAMed_complete_EN_translation_TO_CHECK.xlsx` | English translation with review columns: corrected text (where applicable) and reviewer notes |

### Review Columns in the English File

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

### Running the Translation

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python Dataset_Translation/scripts/translate_questions.py
```

The script reads per-year Italian XLSX files from `Dataset/IT/xlsx/` and produces English XLSX files in `Dataset/EN/xlsx/`.

---

## Quality Metrics

After the expert review, corrections were applied to the final dataset files in `Dataset/EN/`. The review process ensured that:

- All medical terminology follows standard English conventions
- Clinical meaning is preserved exactly across languages
- The English version is suitable for use in LLM benchmarking without requiring additional preprocessing
