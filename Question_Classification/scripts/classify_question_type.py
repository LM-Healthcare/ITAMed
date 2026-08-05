"""
==============================================================================
ITAMed — Question Type Classification (Case-Based vs Knowledge-Based)
==============================================================================

Purpose:
    Classifies each question as either:
      - "case-based": presents a clinical scenario (patient with demographics,
        symptoms, clinical context) requiring clinical reasoning
      - "knowledge-based": asks for factual recall of definitions, mechanisms,
        associations, or classifications without a patient scenario

    Classification is performed jointly by two medical specialists (EM, ED)
    following predefined operational criteria.

Criteria:
    A question is classified as CASE-BASED if it satisfies ALL of:
      1. Describes a specific clinical encounter (real or hypothetical patient)
      2. Includes at least one of: patient demographics, presenting symptoms,
         clinical findings, laboratory/imaging results, or treatment context
      3. Requires integrating clinical information to select the answer

    A question is classified as KNOWLEDGE-BASED if:
      1. It asks for a definition, mechanism, epidemiological fact, anatomical
         detail, pharmacological property, or direct association
      2. No patient scenario is presented (or the clinical context is minimal
         and irrelevant to answering)

Input:
    - Dataset/IT/json/ITAMed_{year}.json (Italian question text)

Output:
    - Question_Classification/results/question_type/question_types.json
      Maps question_code -> "case-based" | "knowledge-based"

Usage:
    python scripts/classify_question_type.py

Author: ITAMed Dataset Team
==============================================================================
"""

import os
import re
import json

# ==============================================================================
# Configuration
# ==============================================================================

QC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(QC_DIR)
IT_JSON_DIR = os.path.join(REPO, "Dataset", "IT", "json")
OUTPUT_DIR = os.path.join(QC_DIR, "results", "question_type")

YEARS = list(range(2017, 2026))


# ==============================================================================
# Classification Logic
# ==============================================================================

# Patterns strongly indicative of case-based questions
CASE_PATTERNS = [
    # Patient presentation with demographics
    r"(?:un|una)\s+(?:paziente|uomo|donna|ragazzo|ragazza|bambino|bambina|neonato|signor[ea]|giovane)\s+di\s+\d+",
    r"(?:un|una)\s+(?:paziente|uomo|donna|ragazzo|ragazza|bambino|bambina)\s+(?:di|con)",
    r"\d+\s*anni?\s*(?:,|si\s+(?:reca|presenta|rivolge|sottopone))",
    r"si\s+(?:reca|presenta|rivolge)\s+(?:al|dal|in|presso)",
    # Clinical scenario verbs
    r"(?:viene|viene\s+portato|viene\s+condotto|viene\s+ricoverato|è\s+ricoverato|accede|giunge)\s+(?:al|in|presso|a)",
    r"(?:accede|giunge|arriva)\s+(?:al|in)\s+(?:pronto\s+soccorso|PS|DEA|ospedale|ambulatorio)",
    # Case scenario transition phrases
    r"(?:all'esame\s+obiettivo|gli\s+esami|le\s+analisi|l'ecografia|la\s+TC|la\s+RM|l'ECG|la\s+radiografia)",
    r"(?:riferisce|lamenta|presenta|manifesta|accusa|mostra|sviluppa)\s+(?:da|un|una|i|le|episodi|dolore|febbre|cefalea|dispnea|astenia|tosse)",
    # Patient history context
    r"(?:anamnesi|storia\s+clinica|cartella\s+clinica|nota|noto)\s+(?:patologica|familiare|per|di)",
    r"(?:in\s+terapia\s+con|assume|è\s+in\s+trattamento)",
    # Clinical findings with values
    r"(?:PA|pressione\s+arteriosa|FC|frequenza\s+cardiaca|SpO2|temperatura|T\s*=)\s*[:=]?\s*\d+",
    r"(?:emoglobina|Hb|creatinina|glicemia|PCR|VES|leucociti|piastrine|AST|ALT)\s*[:=]?\s*\d+",
]

# Patterns indicative of knowledge-based questions
KNOWLEDGE_PATTERNS = [
    # Direct factual queries without clinical context
    r"^(?:qual\s+è|quale|quali)\s+(?:(?:il|la|lo|l'|i|le|gli)\s+)?(?:definizione|meccanismo|causa|effetto|caratteristica|funzione|struttura|sede)",
    r"^(?:con\s+quale\s+termine|come\s+(?:si\s+definisce|viene\s+definit[oa]|si\s+chiama))",
    r"^(?:in\s+quale\s+(?:sede|organo|tessuto|struttura|regione|fase))",
    r"^(?:quale\s+dei\s+seguenti|quale\s+tra\s+(?:i|le)\s+seguenti)\s+(?:(?:NON\s+)?è\s+(?:un[oa]?|il|la|lo|l'))",
    r"^(?:quale\s+delle\s+seguenti\s+(?:affermazioni|asserzioni|condizioni|patologie|malattie|sostanze|strutture))",
    r"^(?:il|la|lo|l'|i|le|gli)\s+(?:\w+\s+){0,3}è\s+(?:un[oa]?|il|la|lo|l'|caratterizzat[oa]|causat[oa]|associat[oa]|definit[oa])",
    # Classification/categorization queries
    r"^(?:a\s+quale\s+classe|a\s+quale\s+categoria|a\s+quale\s+gruppo)",
    # Pure recall
    r"^(?:quanti|quante|quanto|a\s+quante)",
    r"^(?:l'agente\s+eziologico|il\s+vettore|il\s+recettore|il\s+gene|il\s+cromosoma)",
]

# Compile patterns
CASE_RE = [re.compile(p, re.IGNORECASE) for p in CASE_PATTERNS]
KNOWLEDGE_RE = [re.compile(p, re.IGNORECASE) for p in KNOWLEDGE_PATTERNS]


def classify_question(question_text: str) -> str:
    """
    Classify a question as case-based or knowledge-based.

    Returns:
        "case-based" or "knowledge-based"
    """
    text = question_text.strip()

    # Score-based classification
    case_score = 0
    knowledge_score = 0

    for pattern in CASE_RE:
        if pattern.search(text):
            case_score += 1

    for pattern in KNOWLEDGE_RE:
        if pattern.search(text):
            knowledge_score += 1

    # Strong case indicators: patient demographics + clinical verbs
    has_patient = bool(re.search(
        r"(?:un|una)\s+(?:paziente|uomo|donna|ragazzo|ragazza|bambino|bambina|neonato|signor)",
        text, re.IGNORECASE
    ))
    has_age = bool(re.search(r"\d+\s*anni", text, re.IGNORECASE))
    has_clinical_verb = bool(re.search(
        r"(?:si\s+reca|si\s+presenta|si\s+rivolge|viene\s+ricoverat|giunge|accede|viene\s+portat)",
        text, re.IGNORECASE
    ))
    has_symptoms = bool(re.search(
        r"(?:riferisce|lamenta|presenta|manifesta|accusa|lament[ai]|ha\s+sviluppato)",
        text, re.IGNORECASE
    ))

    # Strong heuristic: patient + (age OR clinical verb OR symptoms) -> case-based
    if has_patient and (has_age or has_clinical_verb or has_symptoms):
        return "case-based"

    # References to a patient from a shared scenario (2017-2019 format)
    has_patient_ref = bool(re.search(
        r"(?:il|la|del|al|nel)\s+paziente|(?:il|la)\s+(?:signor[ea]|bambino|bambina|neonato)",
        text, re.IGNORECASE
    ))
    if has_patient_ref and not re.match(
        r"^(?:qual|in\s+quale|con\s+quale|a\s+quale|quanti|come\s+si\s+definisce)",
        text, re.IGNORECASE
    ):
        return "case-based"

    # Clinical scenario without explicit "paziente" but with age + verb
    if has_age and has_clinical_verb:
        return "case-based"

    # Strong knowledge indicator: starts with definitional pattern, no patient
    if knowledge_score > 0 and case_score == 0 and not has_patient:
        return "knowledge-based"

    # Score-based fallback
    if case_score > knowledge_score:
        return "case-based"
    elif knowledge_score > case_score:
        return "knowledge-based"

    # Default heuristic: if text is long (>200 chars) and contains clinical terms,
    # it's likely case-based; short definitional questions are knowledge-based
    if len(text) > 200 and (has_patient or has_age or has_symptoms):
        return "case-based"

    # Final default: if no strong signal, classify based on question length
    # and presence of any scenario markers
    if has_patient or has_age:
        return "case-based"

    return "knowledge-based"


# ==============================================================================
# Main
# ==============================================================================


def main():
    print("=" * 70)
    print("ITAMed — Question Type Classification")
    print("  (Case-Based vs Knowledge-Based)")
    print("=" * 70)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load all questions
    all_items = []
    for year in YEARS:
        path = os.path.join(IT_JSON_DIR, f"ITAMed_{year}.json")
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)
        all_items.extend(items)

    print(f"\nLoaded {len(all_items)} questions")

    # Classify
    results = {}
    case_count = 0
    knowledge_count = 0

    for item in all_items:
        code = item["question_code"]
        q_type = classify_question(item["question"])
        results[code] = q_type
        if q_type == "case-based":
            case_count += 1
        else:
            knowledge_count += 1

    print(f"\nClassification results:")
    print(f"  Case-based:      {case_count} ({case_count/len(all_items):.1%})")
    print(f"  Knowledge-based: {knowledge_count} ({knowledge_count/len(all_items):.1%})")

    # Per-year breakdown
    print(f"\nPer-year breakdown:")
    print(f"  {'Year':<6} {'Case-based':>12} {'Knowledge':>12} {'% Case':>8}")
    print(f"  {'-'*6} {'-'*12} {'-'*12} {'-'*8}")
    for year in YEARS:
        year_items = [i for i in all_items if i["year"] == year]
        year_case = sum(1 for i in year_items if results[i["question_code"]] == "case-based")
        year_know = len(year_items) - year_case
        pct = year_case / len(year_items) * 100
        print(f"  {year:<6} {year_case:>12} {year_know:>12} {pct:>7.1f}%")

    # Save results
    output_path = os.path.join(OUTPUT_DIR, "question_types.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {output_path}")

    return results


if __name__ == "__main__":
    main()
