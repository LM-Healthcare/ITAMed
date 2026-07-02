"""
==============================================================================
ITAMed — Medical Specialty Classification Script
==============================================================================

Purpose:
    Classifies extracted SSM (Specializzazione in Medicina) questions into
    medical specialties using the Anthropic Claude API.

    Each question is assigned one or two categories from a standardized
    taxonomy of 28 Italian medical specialties, based on its clinical
    content, question stem, and answer options.

Input:
    XLSX files in 'Dataset/IT/xlsx/' containing the verified questions
    (columns: Anno, Numero Domanda, Codice Domanda, Domanda,
    Risposta A–E, Risposta Corretta, Categoria, Immagine, ...).

Output:
    Classified JSON files in 'Question_Classification/results/claude/' with
    the assigned specialty(ies) for each question.
    Intermediate JSON files are saved for resume support.

Requirements:
    - anthropic>=0.42 (Claude API client)
    - openpyxl (XLSX read/write)
    - ANTHROPIC_API_KEY environment variable must be set

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python classify_claude.py

Author: ITAMed Dataset Team
==============================================================================
"""

import os
import sys
import json
import time
from collections import Counter

import openpyxl
import anthropic

# ==============================================================================
# Configuration
# ==============================================================================

QC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(QC_DIR)
DATA_DIR = os.path.join(REPO_ROOT, "Data")
OUTPUT_DIR = os.path.join(QC_DIR, "results", "claude")

MODEL = "claude-opus-4-8"
BATCH_SIZE = 10
YEARS = list(range(2017, 2026))
EXPECTED_QUESTIONS = 140

# ==============================================================================
# Medical Specialty Taxonomy (28 categories)
# ==============================================================================

CATEGORIES = [
    "Cardiologia e Cardiochirurgia",
    "Chirurgia Generale",
    "Gastroenterologia",
    "Neurologia e Neurochirurgia",
    "Pneumologia e Chirurgia Toracica",
    "Ortopedia e Traumatologia",
    "Endocrinologia",
    "Ginecologia e Ostetricia",
    "Pediatria",
    "Urologia",
    "Nefrologia",
    "Ematologia",
    "Oncologia",
    "Malattie Infettive",
    "Immunologia e Reumatologia",
    "Dermatologia e Venereologia",
    "Psichiatria",
    "Oftalmologia",
    "Otorinolaringoiatria",
    "Anestesia e Rianimazione",
    "Igiene, Epidemiologia e Statistica",
    "Medicina del Lavoro",
    "Medicina Legale",
    "Diagnostica per Immagini e Medicina Nucleare",
    "Genetica Medica",
    "Farmacologia e Tossicologia",
    "Nutrizione Clinica",
    "Medicina Interna",
]

CATEGORIES_STR = "\n".join(f"{i+1}. {cat}" for i, cat in enumerate(CATEGORIES))

# ==============================================================================
# LLM Prompt
# ==============================================================================

SYSTEM_PROMPT = f"""Sei un esperto medico italiano specializzato nella classificazione di domande dell'esame SSM (Specializzazione in Medicina).

Il tuo compito è classificare ogni domanda in una o più delle seguenti categorie mediche:

{CATEGORIES_STR}

REGOLE:
1. Assegna la categoria PRINCIPALE più appropriata per ogni domanda.
2. Se la domanda è chiaramente multispecialistica (es. un caso clinico che coinvolge due discipline in modo significativo), puoi assegnare fino a 2 categorie, separate da punto e virgola.
3. NON assegnare più di 2 categorie per domanda.
4. Usa ESATTAMENTE i nomi delle categorie come elencati sopra.
5. Se una domanda riguarda un argomento trasversale (es. anatomia, fisiologia, biochimica) classificala in base al contesto clinico/organo/sistema coinvolto.
6. "Medicina Interna" va usata SOLO per domande generalistiche che non rientrano chiaramente in nessuna altra specialità.

Rispondi SOLO in formato JSON, un array di oggetti con "id" (numero della domanda nel batch) e "categorie" (stringa con la/le categoria/e).
"""


# ==============================================================================
# Classification Logic
# ==============================================================================


def classify_batch(client: anthropic.Anthropic, questions_batch: list, batch_start_idx: int) -> list | None:
    """
    Classify a batch of questions using the Claude API.

    Args:
        client: Anthropic API client instance.
        questions_batch: List of question dicts with keys 'codice', 'domanda', 'A'–'E'.
        batch_start_idx: Starting index of this batch (for logging).

    Returns:
        List of classification results, or None if all retries failed.
    """
    
    # Format questions for the prompt
    questions_text = ""
    for i, q in enumerate(questions_batch):
        questions_text += f"\n--- Domanda {i+1} ---\n"
        questions_text += f"Codice: {q['codice']}\n"
        questions_text += f"Testo: {q['domanda']}\n"
        questions_text += f"A: {q['A']}\n"
        questions_text += f"B: {q['B']}\n"
        questions_text += f"C: {q['C']}\n"
        questions_text += f"D: {q['D']}\n"
        questions_text += f"E: {q['E']}\n"
    
    user_prompt = f"""Classifica le seguenti {len(questions_batch)} domande dell'esame SSM.

{questions_text}

Rispondi con un JSON array. Esempio:
[{{"id": 1, "categorie": "Cardiologia e Cardiochirurgia"}}, {{"id": 2, "categorie": "Neurologia e Neurochirurgia; Oncologia"}}]
"""
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            # Parse response
            response_text = response.content[0].text.strip()
            
            # Extract JSON from response (handle potential markdown code blocks)
            if "```" in response_text:
                json_match = response_text.split("```")[1]
                if json_match.startswith("json"):
                    json_match = json_match[4:]
                response_text = json_match.strip()
            
            results = json.loads(response_text)
            
            # Validate results
            if len(results) != len(questions_batch):
                print(f"  WARNING: Expected {len(questions_batch)} results, got {len(results)}. Retrying...")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
            
            return results
            
        except json.JSONDecodeError as e:
            print(f"  JSON parse error (attempt {attempt+1}): {e}")
            print(f"  Response: {response_text[:200]}")
            if attempt < max_retries - 1:
                time.sleep(2)
        except anthropic.RateLimitError:
            print(f"  Rate limited. Waiting 30s...")
            time.sleep(30)
        except Exception as e:
            print(f"  API error (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
    
    return None


def load_questions(xlsx_path: str) -> list:
    """Load questions from an XLSX file produced by the extraction scripts."""
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active
    questions = []
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        questions.append({
            'codice': row[0].value,
            'domanda': row[1].value,
            'A': row[2].value,
            'B': row[3].value,
            'C': row[4].value,
            'D': row[5].value,
            'E': row[6].value,
        })
    return questions


def validate_categories(categories_str: str) -> str:
    """
    Validate and normalize category string against the allowed taxonomy.

    Performs exact matching first, then fuzzy substring matching for minor
    variations. Invalid categories are preserved for manual review.
    """
    cats = [c.strip() for c in categories_str.split(";")]
    valid = []
    for cat in cats:
        if cat in CATEGORIES:
            valid.append(cat)
        else:
            # Try fuzzy match
            matched = False
            for allowed in CATEGORIES:
                if cat.lower() in allowed.lower() or allowed.lower() in cat.lower():
                    valid.append(allowed)
                    matched = True
                    break
            if not matched:
                print(f"    INVALID CATEGORY: '{cat}' - keeping as-is for review")
                valid.append(cat)
    return "; ".join(valid)


def process_year(year: int, client: anthropic.Anthropic) -> dict | None:
    """
    Process all questions for a given year: load, classify, validate, and save.

    Supports resuming from intermediate results if the process was interrupted.

    Args:
        year: Exam year (2017–2025).
        client: Anthropic API client instance.

    Returns:
        Dictionary mapping question numbers to categories, or None on failure.
    """
    xlsx_path = os.path.join(DATA_DIR, f"{year}_answers.xlsx")
    
    if not os.path.exists(xlsx_path):
        print(f"  File not found: {xlsx_path}")
        return
    
    questions = load_questions(xlsx_path)
    print(f"  Loaded {len(questions)} questions")
    
    # Check if we have a partial results file (for resuming)
    results_json_path = os.path.join(OUTPUT_DIR, f"{year}_classifications.json")
    existing_results = {}
    if os.path.exists(results_json_path):
        with open(results_json_path, 'r', encoding='utf-8') as f:
            existing_results = json.load(f)
        print(f"  Resuming from {len(existing_results)} previously classified questions")
    
    # Process in batches
    all_results = existing_results.copy()
    
    for batch_start in range(0, len(questions), BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, len(questions))
        
        # Check if this batch is already done (1-indexed)
        batch_keys = [str(i+1) for i in range(batch_start, batch_end)]
        if all(k in all_results for k in batch_keys):
            continue
        
        batch = questions[batch_start:batch_end]
        print(f"  Processing questions {batch_start+1}-{batch_end}...")
        
        results = classify_batch(client, batch, batch_start)
        
        if results:
            for i, result in enumerate(results):
                q_idx = batch_start + i + 1  # 1-indexed
                categories = validate_categories(result.get("categorie", ""))
                all_results[str(q_idx)] = categories
            
            # Save intermediate results
            with open(results_json_path, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
        else:
            print(f"  FAILED to classify batch {batch_start+1}-{batch_end}")
        
        # Rate limiting pause
        time.sleep(1)
    
    # Create output xlsx with classifications
    output_path = os.path.join(OUTPUT_DIR, f"{year}_answers_classified.xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "SSM_Test"
    
    headers = ['Codice Domanda', 'Domanda', 'Risposta A', 'Risposta B', 
               'Risposta C', 'Risposta D', 'Risposta E', 'Categoria']
    ws.append(headers)
    
    for i, q in enumerate(questions):
        category = all_results.get(str(i+1), "NON CLASSIFICATA")  # 1-indexed
        ws.append([q['codice'], q['domanda'], q['A'], q['B'], q['C'], q['D'], q['E'], category])
    
    wb.save(output_path)
    print(f"  Saved classified file: {output_path}")
    
    # Summary
    cat_counts = Counter()
    for cat_str in all_results.values():
        for cat in cat_str.split("; "):
            cat_counts[cat.strip()] += 1
    
    print(f"\n  Distribution for {year}:")
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {count}")
    
    return all_results


# ==============================================================================
# Main Execution
# ==============================================================================


def main():
    """
    Main entry point. Classifies all SSM questions (2017–2025) by medical
    specialty using the Claude API.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        print("  Linux/macOS: export ANTHROPIC_API_KEY='sk-ant-...'")
        print("  Windows:     $env:ANTHROPIC_API_KEY = 'sk-ant-...'")
        sys.exit(1)

    print("=" * 70)
    print("ITAMed — Medical Specialty Classification")
    print("=" * 70)
    print(f"  Model:            {MODEL}")
    print(f"  Input directory:  {DATA_DIR}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"  Batch size:       {BATCH_SIZE}")
    print(f"  Years:            {YEARS}")
    print()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    client = anthropic.Anthropic(api_key=api_key)

    for year in YEARS:
        print(f"\n{'='*70}")
        print(f"Processing {year}...")
        print(f"{'='*70}")
        process_year(year, client)

    print(f"\n{'='*70}")
    print("CLASSIFICATION COMPLETE")
    print(f"Results saved in: {OUTPUT_DIR}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
