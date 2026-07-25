# Question Classification

## Overview

All 1,260 questions in the ITAMed dataset were classified into medical specialties using a **dual-annotator LLM protocol** followed by **independent expert adjudication** of disagreements by two medical specialists. This approach ensures reproducibility, transparency, and scientific rigor in the specialty taxonomy assignment.

---

## Classification Pipeline

```
┌─────────────────────┐     ┌─────────────────────┐
│   Claude Opus 4.8   │     │      GPT-5.5        │
│   (Annotator 1)     │     │   (Annotator 2)     │
└──────────┬──────────┘     └──────────┬──────────┘
           │                           │
           ▼                           ▼
┌──────────────────────────────────────────────────┐
│         Inter-Rater Agreement Analysis           │
│     (Contingency table + Cohen's Kappa)          │
└──────────────────────┬───────────────────────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
      Concordant              Discordant
      (880 questions)        (380 questions)
           │                       │
           ▼                       ▼
    Category confirmed      Expert Adjudication
                       ┌────────────┴────────────┐
                       │                         │
                  Reviewer 1               Reviewer 2
                 (independent)            (independent)
                       │                         │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       Inter-Reviewer Agreement
                        (Cohen's κ + resolution)
                                    │
                                    ▼
                            Final category
                            (dataset updated)
```

---

## Models

| Model | Provider | API Model ID | Role |
|:------|:---------|:-------------|:-----|
| Claude Opus 4.8 | Anthropic | `claude-opus-4-8` | Primary annotator |
| GPT-5.5 | OpenAI | `gpt-5.5` | Secondary annotator |

---

## Medical Specialty Taxonomy (28 categories)

The taxonomy was defined a priori based on the Italian Medical Specialization Schools (*Scuole di Specializzazione in Medicina*). Since the exam questions are in Italian, the classification prompt and category names are in Italian to preserve clinical accuracy.

| # | Italian | English |
|:-:|:--------|:--------|
| 1 | Cardiologia e Cardiochirurgia | Cardiology and Cardiac Surgery |
| 2 | Chirurgia Generale | General Surgery |
| 3 | Gastroenterologia | Gastroenterology |
| 4 | Neurologia e Neurochirurgia | Neurology and Neurosurgery |
| 5 | Pneumologia e Chirurgia Toracica | Pulmonology and Thoracic Surgery |
| 6 | Ortopedia e Traumatologia | Orthopedics and Traumatology |
| 7 | Endocrinologia | Endocrinology |
| 8 | Ginecologia e Ostetricia | Gynecology and Obstetrics |
| 9 | Pediatria | Pediatrics |
| 10 | Urologia | Urology |
| 11 | Nefrologia | Nephrology |
| 12 | Ematologia | Hematology |
| 13 | Oncologia | Oncology |
| 14 | Malattie Infettive | Infectious Diseases |
| 15 | Immunologia e Reumatologia | Immunology and Rheumatology |
| 16 | Dermatologia e Venereologia | Dermatology and Venereology |
| 17 | Psichiatria | Psychiatry |
| 18 | Oftalmologia | Ophthalmology |
| 19 | Otorinolaringoiatria | Otorhinolaryngology |
| 20 | Anestesia e Rianimazione | Anesthesia and Intensive Care |
| 21 | Igiene, Epidemiologia e Statistica | Hygiene, Epidemiology and Statistics |
| 22 | Medicina del Lavoro | Occupational Medicine |
| 23 | Medicina Legale | Forensic Medicine |
| 24 | Diagnostica per Immagini e Medicina Nucleare | Diagnostic Imaging and Nuclear Medicine |
| 25 | Genetica Medica | Medical Genetics |
| 26 | Farmacologia e Tossicologia | Pharmacology and Toxicology |
| 27 | Nutrizione Clinica | Clinical Nutrition |
| 28 | Medicina Interna | Internal Medicine |

Each question may receive **1 or 2 categories** (semicolon-separated) when clearly multidisciplinary.

---

## Classification Prompt

The prompt is **identical** for both models to ensure a fair comparison. It is written in Italian because the source material (exam questions, answer options, and medical terminology) is natively in Italian.

```
Sei un esperto medico italiano specializzato nella classificazione di domande
dell'esame SSM (Specializzazione in Medicina).

Il tuo compito è classificare ogni domanda in una o più delle seguenti
categorie mediche:

1. Cardiologia e Cardiochirurgia
2. Chirurgia Generale
[... all 28 categories ...]
28. Medicina Interna

REGOLE:
1. Assegna la categoria PRINCIPALE più appropriata per ogni domanda.
2. Se la domanda è chiaramente multispecialistica (es. un caso clinico che
   coinvolge due discipline in modo significativo), puoi assegnare fino a
   2 categorie, separate da punto e virgola.
3. NON assegnare più di 2 categorie per domanda.
4. Usa ESATTAMENTE i nomi delle categorie come elencati sopra.
5. Se una domanda riguarda un argomento trasversale (es. anatomia, fisiologia,
   biochimica) classificala in base al contesto clinico/organo/sistema coinvolto.
6. "Medicina Interna" va usata SOLO per domande generalistiche che non rientrano
   chiaramente in nessuna altra specialità.

Rispondi SOLO in formato JSON, un array di oggetti con "id" (numero della
domanda nel batch) e "categorie" (stringa con la/le categoria/e).
```

Each question is presented to the model in the following format:

```
--- Domanda N ---
Codice: ssmYYYYXX
Testo: [question text]
Risposta Corretta: [correct answer text]
```

**Translation of the rules** (for reference):
1. Assign the most appropriate PRIMARY category for each question.
2. If clearly multidisciplinary, assign up to 2 categories (semicolon-separated).
3. Do NOT assign more than 2 categories per question.
4. Use EXACTLY the category names as listed.
5. For cross-cutting topics (anatomy, physiology, biochemistry), classify based on the clinical context.
6. Use "Medicina Interna" ONLY for generalist questions that do not clearly fit any other specialty.

---

## Execution Parameters

| Parameter | Claude Opus 4.8 | GPT-5.5 |
|:----------|:----------------|:--------|
| Temperature | default | 1 |
| Max output tokens | 2,000 | 2,000 |
| Batch size | 10 questions | 10 questions |
| Retries on error | 3 attempts | 3 attempts |
| Rate limit pause | 1s between batches | 1s between batches |
| Output format | JSON array | JSON array |

---

## Input Data

- **Total questions**: 1,260 (140 questions × 9 years: 2017–2025)
- **Source**: Verified dataset files (`Dataset/IT/xlsx/ITAMed_{year}.xlsx`)
- **Provided to models**: question code, question text, correct answer (always option A)
- **NOT provided**: incorrect answer options (B–E), year, images (to avoid classification bias)

---

## Results — Inter-Rater Agreement

### Overall Statistics

| Metric | Value |
|:-------|------:|
| Total questions | 1,260 |
| Primary-category agreement | 1,134 / 1,260 (90.0%) |
| Exact-match agreement (full string) | 880 / 1,260 (69.8%) |
| **Cohen's Kappa (primary category)** | **κ = 0.8950** |
| **Total discordances (exact-match)** | **380** |

### Interpretation (Landis & Koch, 1977)

| κ Range | Interpretation |
|:--------|:---------------|
| < 0.00 | Poor |
| 0.00–0.20 | Slight |
| 0.21–0.40 | Fair |
| 0.41–0.60 | Moderate |
| 0.61–0.80 | Substantial |
| **0.81–1.00** | **Almost perfect** |

The value **κ = 0.8950** indicates **almost perfect agreement** between the two LLM annotators, well above the conventional threshold of 0.80 for taxonomy reliability.

### Per-Category Kappa (one-vs-all)

| Category | κ |
|:---------|--:|
| Medicina Interna | 1.0000 |
| Psichiatria | 1.0000 |
| Oftalmologia | 0.9814 |
| Ortopedia e Traumatologia | 0.9579 |
| Immunologia e Reumatologia | 0.9457 |
| Neurologia e Neurochirurgia | 0.9447 |
| Ginecologia e Ostetricia | 0.9440 |
| Endocrinologia | 0.9411 |
| Medicina del Lavoro | 0.9367 |
| Urologia | 0.9330 |
| Cardiologia e Cardiochirurgia | 0.9268 |
| Genetica Medica | 0.9177 |
| Ematologia | 0.9167 |
| Igiene, Epidemiologia e Statistica | 0.9165 |
| Otorinolaringoiatria | 0.9103 |
| Nutrizione Clinica | 0.9087 |
| Dermatologia e Venereologia | 0.9008 |
| Pneumologia e Chirurgia Toracica | 0.9005 |
| Gastroenterologia | 0.8822 |
| Anestesia e Rianimazione | 0.8775 |
| Malattie Infettive | 0.8731 |
| Medicina Legale | 0.8698 |
| Nefrologia | 0.8643 |
| Chirurgia Generale | 0.8319 |
| Pediatria | 0.8142 |
| Farmacologia e Tossicologia | 0.7829 |
| Oncologia | 0.7184 |
| Diagnostica per Immagini e Medicina Nucleare | 0.6951 |

All categories reach at least "substantial" agreement (κ > 0.60).

### Discordances by Year (exact-match)

| Year | Discordances | % |
|:-----|:-----------:|:---:|
| 2017 | 39 | 27.9% |
| 2018 | 43 | 30.7% |
| 2019 | 43 | 30.7% |
| 2020 | 40 | 28.6% |
| 2021 | 42 | 30.0% |
| 2022 | 44 | 31.4% |
| 2023 | 51 | 36.4% |
| 2024 | 32 | 22.9% |
| 2025 | 46 | 32.9% |

Year 2023 shows a slightly higher discordance rate, likely due to its atypical PDF format.

---

## Expert Adjudication Process

All **380 questions with any classification disagreement** (primary and/or secondary category) were reviewed by **two independent medical specialists** (Reviewer 1 and Reviewer 2). Each reviewer worked **separately and independently**, without access to the other's decisions.

For each discordant question, each reviewer received:

- The full question text and all five answer options
- The category assigned by Claude Opus 4.8
- The category assigned by GPT-5.5

Each reviewer independently selected the correct classification (or proposed a third option if neither LLM assignment was adequate).

### Inter-Reviewer Agreement

After both reviewers completed their independent review, their decisions were compared to compute inter-reviewer agreement.

| Metric | Value |
|:-------|------:|
| Questions reviewed | 380 |
| Primary-category agreement | 328/380 (86.3%) |
| Exact-match agreement (full string) | 254/380 (66.8%) |
| Set-based agreement (order-independent) | 270/380 (71.1%) |
| **Cohen's Kappa (primary category)** | **κ = 0.8557** |
| Remaining discordances | **52** |

The value **κ = 0.8557** indicates **almost perfect agreement** between the two medical reviewers, demonstrating high consistency in expert adjudication even on questions that were ambiguous enough to cause disagreement between two state-of-the-art LLMs.

### Reviewer–LLM Alignment

For each discordant question, we analyzed whether each reviewer's primary category aligned with Claude's, GPT's, or neither:

| Alignment | Reviewer 1 | Reviewer 2 |
|:----------|:---------:|:---------:|
| Agreed with Claude (only) | 61 (16.1%) | 74 (19.5%) |
| Agreed with GPT (only) | 59 (15.5%) | 51 (13.4%) |
| Chose third option | 63 (16.6%) | 40 (10.5%) |
| Matched LLM consensus\* | 197 (51.8%) | 215 (56.6%) |

\* *Questions where both LLMs shared the same primary category (discordance was only in secondary categories) and the reviewer confirmed that primary.*

### Discordance Resolution

The **52 remaining discordances** between the two reviewers will be resolved through consensus discussion between the reviewers. The final adjudicated categories will be applied to the official dataset using the `apply_expert_review.py` script.

---

## Folder Structure

```
Question_Classification/
├── README.md                              ← This file
│
├── scripts/
│   ├── classify_claude.py                 # Classification with Claude Opus 4.8
│   ├── classify_gpt.py                    # Classification with GPT-5.5
│   ├── compute_agreement.py              # LLM inter-rater agreement analysis
│   ├── compute_reviewer_agreement.py     # Expert reviewer agreement analysis
│   └── apply_expert_review.py            # Apply expert decisions to dataset
│
├── results/
│   ├── claude/                            # JSON: Claude classifications (1 file/year)
│   │   ├── 2017_classifications_claude.json
│   │   ├── ...
│   │   └── 2025_classifications_claude.json
│   │
│   ├── gpt/                              # JSON: GPT classifications (1 file/year)
│   │   ├── 2017_classifications_gpt.json
│   │   ├── ...
│   │   └── 2025_classifications_gpt.json
│   │
│   └── agreement/                         # Agreement analysis outputs
│       ├── agreement_report.txt           #   Full text report
│       ├── contingency_table.xlsx         #   28×28 contingency matrix
│       ├── discordances.xlsx              #   Complete discordance list
│       └── discordances.json              #   Discordances in JSON format
│
├── expert_review/
│   ├── discordances_to_review_REW_1_EMILIANO.xlsx    # Reviewer 1 template
│   ├── discordances_to_review_REW_2_EDOARDO.xlsx     # Reviewer 2 template
│   └── instructions.md                                # Compilation instructions
│
└── results/expert_review/                              # Expert agreement analysis
    ├── expert_agreement_report.md                      #   Full markdown report
    ├── reviewer_discordances.xlsx                      #   52 remaining discordances
    ├── reviewer_discordances.json                      #   Same in JSON format
    └── reviewer_confusion_matrix.xlsx                  #   Reviewer confusion matrix
```

---

## Reproducibility

To re-run the full pipeline from scratch:

```bash
# 1. Claude classification (requires ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY="sk-ant-..."
python scripts/classify_claude.py

# 2. GPT classification (requires OPENAI_API_KEY)
export OPENAI_API_KEY="sk-..."
python scripts/classify_gpt.py

# 3. Compute LLM inter-rater agreement
python scripts/compute_agreement.py

# 4. Compute expert reviewer agreement
python scripts/compute_reviewer_agreement.py

# 5. Apply expert-reviewed categories to the dataset
python scripts/apply_expert_review.py
```

---

## Methodological Note

The dual-annotator LLM protocol follows established best practices for annotated dataset construction:

1. **Independence** — The two models classify without knowledge of each other's output
2. **Identical prompt** — Ensures fairness in the comparison
3. **Cohen's Kappa** — Standard inter-annotator agreement metric that corrects for chance
4. **Expert adjudication** — Disagreements are resolved by two independent medical specialists, not by the algorithm
5. **Inter-reviewer agreement** — The two reviewers' decisions are compared for consistency before final resolution

This approach is more robust than single-model classification because it:
- Identifies ambiguous or boundary questions between specialties
- Provides a quantitative measure of taxonomy reliability
- Ensures every contested assignment is validated independently by two human experts
