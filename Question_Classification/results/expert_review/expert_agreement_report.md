# Expert Reviewer Agreement — Inter-Rater Analysis

## Overview

Two independent medical specialists (Reviewer 1 and Reviewer 2) adjudicated 380 questions for which the two LLM annotators (Claude Opus 4.8 and GPT-5.5) produced discordant specialty classifications. Each reviewer worked independently without access to the other's decisions.

> **Note:** 1 question(s) were excluded from analysis due to missing reviewer annotations. Analysis is based on 379 questions.

---

## 1. Overall Agreement Statistics

| Metric | Value |
|:-------|------:|
| Questions reviewed | 379 |
| Primary-category agreement | 243/379 (64.1%) |
| Exact-match agreement (full string) | 127/379 (33.5%) |
| Set-based agreement (order-independent) | 158/379 (41.7%) |
| **Cohen's κ (primary category)** | **κ = 0.6231** |
| Remaining discordances | 136 |

### Interpretation (Landis & Koch, 1977)

| κ Range | Interpretation |
|:--------|:---------------|
| < 0.00 | Poor |
| 0.00–0.20 | Slight |
| 0.21–0.40 | Fair |
| 0.41–0.60 | Moderate |
| 0.61–0.80 | Substantial |
| **0.81–1.00** | **Almost perfect** |

The inter-reviewer **κ = 0.6231** indicates **substantial agreement** between the two medical specialists.

---

## 2. Per-Category Agreement (one-vs-all κ)

| Category | κ | Interpretation |
|:---------|--:|:---------------|
| Ortopedia e Traumatologia | 0.9258 | Almost perfect |
| Dermatologia e Venereologia | 0.8973 | Almost perfect |
| Ginecologia e Ostetricia | 0.8011 | Substantial |
| Oftalmologia | 0.7987 | Substantial |
| Urologia | 0.7759 | Substantial |
| Immunologia e Reumatologia | 0.7551 | Substantial |
| Medicina Legale | 0.7475 | Substantial |
| Nefrologia | 0.7036 | Substantial |
| Neurologia e Neurochirurgia | 0.6957 | Substantial |
| Malattie Infettive | 0.6730 | Substantial |
| Psichiatria | 0.6640 | Substantial |
| Chirurgia Generale | 0.6576 | Substantial |
| Cardiologia e Cardiochirurgia | 0.6527 | Substantial |
| Pediatria | 0.6275 | Substantial |
| Diagnostica per Immagini e Medicina Nucleare | 0.6085 | Moderate |
| Ematologia | 0.5970 | Moderate |
| Pneumologia e Chirurgia Toracica | 0.5583 | Moderate |
| Endocrinologia | 0.5450 | Moderate |
| Medicina del Lavoro | 0.5393 | Moderate |
| Anestesia e Rianimazione | 0.5230 | Moderate |
| Oncologia | 0.5105 | Moderate |
| Gastroenterologia | 0.4883 | Moderate |
| Farmacologia e Tossicologia | 0.3981 | Fair |
| Genetica Medica | 0.3286 | Fair |
| Otorinolaringoiatria | 0.3171 | Fair |
| Igiene, Epidemiologia e Statistica | 0.2425 | Fair |
| Medicina Interna | 0.2186 | Fair |

---

## 3. Agreement by Year

| Year | N | Primary Agreement | % | Exact Agreement | % |
|:-----|--:|------------------:|--:|----------------:|--:|
| 2017 | 39 | 23/39 | 59.0% | 10/39 | 25.6% |
| 2018 | 43 | 26/43 | 60.5% | 14/43 | 32.6% |
| 2019 | 43 | 24/43 | 55.8% | 15/43 | 34.9% |
| 2020 | 40 | 23/40 | 57.5% | 14/40 | 35.0% |
| 2021 | 42 | 31/42 | 73.8% | 17/42 | 40.5% |
| 2022 | 44 | 34/44 | 77.3% | 16/44 | 36.4% |
| 2023 | 50 | 31/50 | 62.0% | 13/50 | 26.0% |
| 2024 | 32 | 19/32 | 59.4% | 9/32 | 28.1% |
| 2025 | 46 | 32/46 | 69.6% | 19/46 | 41.3% |

---

## 4. Reviewer–LLM Alignment

For each question, we checked whether the reviewer's primary category matched Claude's, GPT's, or neither (third option).

| Metric | Reviewer 1 | Reviewer 2 |
|:-------|:---------:|:---------:|
| Agreed with Claude (only) | 60 (15.8%) | 76 (20.1%) |
| Agreed with GPT (only) | 56 (14.8%) | 47 (12.4%) |
| Chose third option | 84 (22.2%) | 36 (9.5%) |
| Matched LLM consensus* | 179 (47.2%) | 220 (58.0%) |

\* *Questions where both LLMs had the same primary category (discordance was only in secondary categories). The reviewer confirmed that shared primary.*

---

## 5. Reviewer Discordance Categorization

Of the 379 reviewed questions, **136** (35.9%) have a primary-category disagreement between the two reviewers and require final resolution.

| Discordance pattern | Count |
|:--------------------|------:|
| R2=Claude, R1=third | 58 |
| R1=GPT, R2=Claude | 31 |
| R1=Claude, R2=GPT | 18 |
| R1=Claude, R2=third | 14 |
| R2=GPT, R1=third | 7 |
| Both=third (different) | 5 |
| R1=GPT, R2=third | 3 |

---

## 6. Summary — Full Classification Pipeline

| Stage | Questions | Agreement | κ |
|:------|:---------:|:---------:|:-:|
| LLM annotation (Claude vs GPT) | 1,260 | 880/1,260 (69.8%) | 0.8950 |
| Expert adjudication (R1 vs R2) | 379 | 243/379 (64.1%) | 0.6231 |
| **Resolved after adjudication** | **1123/1,260** | **89.1%** | — |
| Remaining for resolution | 136 | — | — |
