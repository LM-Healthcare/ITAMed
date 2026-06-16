<p align="center">
  <img src="https://img.shields.io/badge/LLM%20%C3%97%20Healthcare-Research-blue?style=for-the-badge" alt="LLM × Healthcare Research"/>
  <br/>
  <img src="https://img.shields.io/badge/Sapienza-Università%20di%20Roma-8C1515?style=flat-square" alt="Sapienza"/>
  <img src="https://img.shields.io/badge/UGA-Université%20Grenoble%20Alpes-0055A4?style=flat-square" alt="UGA"/>
</p>

# LM-Healthcare

**Exploring Large and Small Language Models for Clinical Decision Support, Medical Benchmarking, and Diagnostic AI**

A joint research initiative between the **[DIAG Department](https://www.diag.uniroma1.it/)** at **Sapienza Università di Roma** and the **[SANGRIA Team](https://www.liglab.fr/fr/recherche/equipes-recherche/sangria-sante-numerique-grenoble-intelligence-artificielle)** at **[LIG Laboratory](https://www.liglab.fr/)**, **Université Grenoble Alpes (UGA)**.

---

## What We Do

We investigate how **Large Language Models (LLMs)** and **Small Language Models (SLMs)** can be applied to real-world healthcare scenarios — from standardized medical exam benchmarking to on-premise clinical assistants deployed in hospital settings.

Our research covers the full lifecycle:

- **Dataset Curation** — Building high-quality, annotated medical datasets for rigorous LLM evaluation
- **Medical Benchmarking** — Evaluating LLMs, SLMs, and quantized models on real clinical exam questions, with a focus on prompting strategies and their impact on diagnostic accuracy
- **Clinical Decision Support** — Developing privacy-preserving, on-premise conversational assistants for structured patient interviews and longitudinal monitoring
- **Diagnostic AI** — Leveraging LLMs for incremental clinical reasoning with multimodal evidence (clinical notes, biomarkers, imaging)

All tools are designed with **clinical deployment** in mind: GDPR-compliant, on-premise, and validated against real-world medical standards.

---

## Projects

| Repository | Description | Status |
|:-----------|:------------|:------:|
| [**ITAMed**](https://github.com/LM-Healthcare/ITAMed) | 📋 Comprehensive bilingual dataset (IT/EN) of 1,260 medical exam questions from the Italian SSM (2017–2025) — specialty classification, image metadata, and multimodal content | [![Paper](https://img.shields.io/badge/Scientific%20Data-in%20progress-yellow)](.) |
| [**LLM-EVAL-Education**](https://github.com/LM-Healthcare/LLM-EVAL-Education) | 📊 Benchmarking closed-source, open-weight, and quantized LLMs on the Italian Medical Specialization Exam (SSM 2020–2024) | [![Paper](https://img.shields.io/badge/Discover%20AI-in%20revision-orange)](.) |
| [**LLM-EVAL-PROMPT**](https://github.com/LM-Healthcare/LLM-EVAL-PROMPT) | 🧪 Evaluating LLM performance on medical MCQs using different prompting strategies — towards optimized clinical deployment | [![Status](https://img.shields.io/badge/status-active-green)](.) |
| [**AURORA**](https://github.com/LM-Healthcare/AURORA) | 🏥 On-premise conversational clinical assistant for structured remote anamnesis (Parkinson's Disease). FHIR-compatible, GDPR-native, fully offline | [![Status](https://img.shields.io/badge/status-active-green)](.) |
| [**LLM_DEMENTIA**](https://github.com/LM-Healthcare/LLM_DEMENTIA) | 🧠 LLM/SLM-based dementia diagnosis via incremental 3-step analysis: clinical data + RAG, plasma biomarkers, and CSF data | [![Status](https://img.shields.io/badge/status-active-green)](.) |

---

## Affiliations

<table>
  <tr>
    <td align="center" width="50%">
      <strong>Sapienza Università di Roma</strong><br/>
      Department of Computer, Control, and Management Engineering (DIAG)<br/>
      Rome, Italy
    </td>
    <td align="center" width="50%">
      <strong>Université Grenoble Alpes (UGA)</strong><br/>
      LIG Laboratory — SANGRIA Team<br/>
      Grenoble, France
    </td>
  </tr>
</table>

---

## Publications

| Title | Venue | Year |
|:------|:------|:----:|
| Quantized Medical LLMs for Edge Deployment: A Privacy-Preserving RAG System | — | 2025 |

<details>
<summary>Abstract</summary>

> Cloud-based medical AI systems raise concerns regarding data privacy and regulatory compliance under GDPR and EU AI Act frameworks. We present a privacy-preserving, edge-deployable clinical decision support system achieving 81.20% accuracy on Italian National Medical Specialization Exams (2020–2024) while operating entirely on local hardware. The system combines a T5-base retriever with a 6-bit quantized Meditron3-8B model (8B parameters), requiring no external APIs and processing queries in 0.45s on consumer GPUs. While proprietary models (GPT-4.1, Claude-4.5) achieve 96% accuracy with 1T+ parameters and cloud dependencies, our system demonstrates that optimized open-source models can deliver clinically relevant performance at two orders of magnitude fewer parameters while preserving complete data sovereignty required for GDPR and EU AI Act compliance.

</details>

---

## Links

- 🤗 [HuggingFace — Datasets & Demos](https://huggingface.co/Filo-White)
- 📄 More publications coming soon

---

<p align="center">
  <sub>Maintained by <a href="https://github.com/Filo-White">@Filo-White</a></sub>
</p>
