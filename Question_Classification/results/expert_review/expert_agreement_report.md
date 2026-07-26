# Expert Reviewer Agreement — Inter-Rater Analysis

## Overview

Two independent medical specialists (Reviewer 1 and Reviewer 2) adjudicated 380 questions for which the two LLM annotators (Claude Opus 4.8 and GPT-5.5) produced discordant specialty classifications. Each reviewer worked independently without access to the other's decisions.


---

## 1. Overall Agreement Statistics

| Metric | Value |
|:-------|------:|
| Questions reviewed | 380 |
| Primary-category agreement | 328/380 (86.3%) |
| Exact-match agreement (full string) | 254/380 (66.8%) |
| Set-based agreement (order-independent) | 264/380 (69.5%) |
| **Cohen's κ (primary category)** | **κ = 0.8557** |
| Remaining discordances | 52 |

### Interpretation (Landis & Koch, 1977)

| κ Range | Interpretation |
|:--------|:---------------|
| < 0.00 | Poor |
| 0.00–0.20 | Slight |
| 0.21–0.40 | Fair |
| 0.41–0.60 | Moderate |
| 0.61–0.80 | Substantial |
| **0.81–1.00** | **Almost perfect** |

The inter-reviewer **κ = 0.8557** indicates **almost perfect agreement** between the two medical specialists.

---

## 2. Per-Category Agreement (one-vs-all κ)

| Category | κ | Interpretation |
|:---------|--:|:---------------|
| Genetica Medica | 1.0000 | Almost perfect |
| Oftalmologia | 1.0000 | Almost perfect |
| Psichiatria | 1.0000 | Almost perfect |
| Neurologia e Neurochirurgia | 0.9804 | Almost perfect |
| Ginecologia e Ostetricia | 0.9701 | Almost perfect |
| Dermatologia e Venereologia | 0.9460 | Almost perfect |
| Ortopedia e Traumatologia | 0.9258 | Almost perfect |
| Pediatria | 0.9242 | Almost perfect |
| Urologia | 0.9204 | Almost perfect |
| Malattie Infettive | 0.9111 | Almost perfect |
| Ematologia | 0.9064 | Almost perfect |
| Immunologia e Reumatologia | 0.8973 | Almost perfect |
| Anestesia e Rianimazione | 0.8695 | Almost perfect |
| Nefrologia | 0.8517 | Almost perfect |
| Cardiologia e Cardiochirurgia | 0.8298 | Almost perfect |
| Endocrinologia | 0.8128 | Almost perfect |
| Oncologia | 0.8012 | Substantial |
| Farmacologia e Tossicologia | 0.7946 | Substantial |
| Chirurgia Generale | 0.7860 | Substantial |
| Otorinolaringoiatria | 0.7725 | Substantial |
| Pneumologia e Chirurgia Toracica | 0.7686 | Substantial |
| Diagnostica per Immagini e Medicina Nucleare | 0.7491 | Substantial |
| Medicina Legale | 0.7475 | Substantial |
| Gastroenterologia | 0.7296 | Substantial |
| Medicina del Lavoro | 0.7233 | Substantial |
| Medicina Interna | 0.6643 | Substantial |
| Igiene, Epidemiologia e Statistica | 0.3975 | Fair |

---

## 3. Agreement by Year

| Year | N | Primary Agreement | % | Exact Agreement | % |
|:-----|--:|------------------:|--:|----------------:|--:|
| 2017 | 39 | 36/39 | 92.3% | 21/39 | 53.8% |
| 2018 | 43 | 26/43 | 60.5% | 14/43 | 32.6% |
| 2019 | 43 | 43/43 | 100.0% | 43/43 | 100.0% |
| 2020 | 40 | 38/40 | 95.0% | 35/40 | 87.5% |
| 2021 | 42 | 35/42 | 83.3% | 25/42 | 59.5% |
| 2022 | 44 | 37/44 | 84.1% | 20/44 | 45.5% |
| 2023 | 51 | 40/51 | 78.4% | 29/51 | 56.9% |
| 2024 | 32 | 30/32 | 93.8% | 26/32 | 81.2% |
| 2025 | 46 | 43/46 | 93.5% | 41/46 | 89.1% |

---

## 4. Reviewer–LLM Alignment

For each question, we checked whether the reviewer's primary category matched Claude's, GPT's, or neither (third option).

| Metric | Reviewer 1 | Reviewer 2 |
|:-------|:---------:|:---------:|
| Agreed with Claude (only) | 61 (16.1%) | 74 (19.5%) |
| Agreed with GPT (only) | 59 (15.5%) | 51 (13.4%) |
| Chose third option | 63 (16.6%) | 40 (10.5%) |
| Matched LLM consensus* | 197 (51.8%) | 215 (56.6%) |

\* *Questions where both LLMs had the same primary category (discordance was only in secondary categories). The reviewer confirmed that shared primary.*

---

## 5. Reviewer Discordance Categorization

Of the 380 reviewed questions, **52** (13.7%) have a primary-category disagreement between the two reviewers and require final resolution.

| Discordance pattern | Count |
|:--------------------|------:|
| R2=Claude, R1=third | 22 |
| R1=GPT, R2=Claude | 15 |
| R2=GPT, R1=third | 5 |
| R1=Claude, R2=third | 3 |
| Both=third (different) | 3 |
| R1=Claude, R2=GPT | 3 |
| R1=GPT, R2=third | 1 |

---

## 6. Summary — Full Classification Pipeline

| Stage | Questions | Agreement | κ |
|:------|:---------:|:---------:|:-:|
| LLM annotation (Claude vs GPT) | 1,260 | 880/1,260 (69.8%) | 0.8950 |
| Expert adjudication (R1 vs R2) | 380 | 254/380 exact (66.8%) | 0.8557 |
| **Fully resolved** | **1134/1,260** | **90.0%** | — |
| Remaining for resolution (any disagreement) | 126 | — | — |

Of the 126 discordances to resolve:
- **52** differ on the primary category
- **74** agree on primary but differ on the secondary category

---

## 7. Discordance Resolution

All **126 discordances** were resolved through in-person consensus discussion between the two medical reviewers. For each discordant question, the reviewers jointly reviewed the clinical content and agreed on the final category assignment.

| Resolution outcome | Count |
|:-------------------|------:|
| Total discordances resolved | 126 |
| Final categories applied to dataset | 1,260/1,260 (100%) |

The final adjudicated categories have been applied to all official dataset files (IT + EN, JSON + XLSX, per-year + complete) using the `apply_expert_review.py` script.
