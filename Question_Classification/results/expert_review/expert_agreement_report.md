# Expert Reviewer Agreement — Inter-Rater Analysis

## Overview

Two independent medical specialists (Reviewer 1 and Reviewer 2) adjudicated 380 questions for which the two LLM annotators (Claude Opus 4.8 and GPT-5.5) produced discordant specialty classifications. Each reviewer worked independently without access to the other's decisions.


---

## 1. Overall Agreement Statistics

| Metric | Value |
|:-------|------:|
| Questions reviewed | 380 |
| Primary-category agreement | 294/380 (77.4%) |
| Exact-match agreement (full string) | 205/380 (53.9%) |
| Set-based agreement (order-independent) | 223/380 (58.7%) |
| **Cohen's κ (primary category)** | **κ = 0.7618** |
| Remaining discordances | 86 |

### Interpretation (Landis & Koch, 1977)

| κ Range | Interpretation |
|:--------|:---------------|
| < 0.00 | Poor |
| 0.00–0.20 | Slight |
| 0.21–0.40 | Fair |
| 0.41–0.60 | Moderate |
| 0.61–0.80 | Substantial |
| **0.81–1.00** | **Almost perfect** |

The inter-reviewer **κ = 0.7618** indicates **substantial agreement** between the two medical specialists.

---

## 2. Per-Category Agreement (one-vs-all κ)

| Category | κ | Interpretation |
|:---------|--:|:---------------|
| Oftalmologia | 1.0000 | Almost perfect |
| Psichiatria | 1.0000 | Almost perfect |
| Ortopedia e Traumatologia | 0.9258 | Almost perfect |
| Neurologia e Neurochirurgia | 0.8986 | Almost perfect |
| Dermatologia e Venereologia | 0.8973 | Almost perfect |
| Pediatria | 0.8527 | Almost perfect |
| Immunologia e Reumatologia | 0.8381 | Almost perfect |
| Anestesia e Rianimazione | 0.8319 | Almost perfect |
| Urologia | 0.8279 | Almost perfect |
| Ginecologia e Ostetricia | 0.8011 | Substantial |
| Malattie Infettive | 0.7959 | Substantial |
| Ematologia | 0.7762 | Substantial |
| Medicina Legale | 0.7475 | Substantial |
| Chirurgia Generale | 0.7432 | Substantial |
| Cardiologia e Cardiochirurgia | 0.7414 | Substantial |
| Nefrologia | 0.7315 | Substantial |
| Medicina del Lavoro | 0.7233 | Substantial |
| Endocrinologia | 0.7192 | Substantial |
| Oncologia | 0.7027 | Substantial |
| Pneumologia e Chirurgia Toracica | 0.6844 | Substantial |
| Gastroenterologia | 0.6808 | Substantial |
| Diagnostica per Immagini e Medicina Nucleare | 0.6774 | Substantial |
| Otorinolaringoiatria | 0.6222 | Substantial |
| Farmacologia e Tossicologia | 0.5697 | Moderate |
| Genetica Medica | 0.5682 | Moderate |
| Medicina Interna | 0.3949 | Fair |
| Igiene, Epidemiologia e Statistica | 0.2792 | Fair |

---

## 3. Agreement by Year

| Year | N | Primary Agreement | % | Exact Agreement | % |
|:-----|--:|------------------:|--:|----------------:|--:|
| 2017 | 39 | 36/39 | 92.3% | 21/39 | 53.8% |
| 2018 | 43 | 26/43 | 60.5% | 14/43 | 32.6% |
| 2019 | 43 | 24/43 | 55.8% | 15/43 | 34.9% |
| 2020 | 40 | 23/40 | 57.5% | 14/40 | 35.0% |
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
| Agreed with Claude (only) | 63 (16.6%) | 75 (19.7%) |
| Agreed with GPT (only) | 54 (14.2%) | 50 (13.2%) |
| Chose third option | 75 (19.7%) | 36 (9.5%) |
| Matched LLM consensus* | 188 (49.5%) | 219 (57.6%) |

\* *Questions where both LLMs had the same primary category (discordance was only in secondary categories). The reviewer confirmed that shared primary.*

---

## 5. Reviewer Discordance Categorization

Of the 380 reviewed questions, **86** (22.6%) have a primary-category disagreement between the two reviewers and require final resolution.

| Discordance pattern | Count |
|:--------------------|------:|
| R2=Claude, R1=third | 41 |
| R1=GPT, R2=Claude | 18 |
| R1=Claude, R2=GPT | 9 |
| R1=Claude, R2=third | 7 |
| R2=GPT, R1=third | 6 |
| Both=third (different) | 4 |
| R1=GPT, R2=third | 1 |

---

## 6. Summary — Full Classification Pipeline

| Stage | Questions | Agreement | κ |
|:------|:---------:|:---------:|:-:|
| LLM annotation (Claude vs GPT) | 1,260 | 880/1,260 (69.8%) | 0.8950 |
| Expert adjudication (R1 vs R2) | 380 | 294/380 (77.4%) | 0.7618 |
| **Resolved after adjudication** | **1174/1,260** | **93.2%** | — |
| Remaining for resolution | 86 | — | — |
