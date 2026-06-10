"""
==============================================================================
ITAMed — Scenario-Based Question Extraction Script
==============================================================================

Purpose:
    Extracts multiple-choice questions from the Italian National Medical
    Specialization Exam (Concorso SSM) PDF documents in scenario-based format
    (years 2017–2019 ONLY).

    In these years, questions are grouped under clinical scenarios. A question
    may reference a specific scenario ("riferita allo scenario n.X"), meaning
    the scenario's clinical vignette is an integral part of the question. This
    script automatically prepends the referenced scenario text to the question,
    producing fully self-contained question records.

Input:
    Official PDF answer documents located in the 'Pdf_Data/' directory.
    Expected filename format: '{year}_answers.pdf'
    Each PDF contains 140 questions with 5 answer options (A–E).

Output:
    One XLSX file per year in 'Data/' with columns:
        - Codice Domanda (question code)
        - Domanda (full question text, including scenario if referenced)
        - Risposta A through E (answer options A–E)

Format Notes:
    - The 2017–2019 exams use a scenario-based structure where multiple
      questions may refer to the same clinical scenario.
    - Questions without a scenario reference are standalone.
    - The correct answer is ALWAYS option A (as per official released format).
    - Answer options start at the beginning of a line (format: "A: ...")

Applicable Years:
    2017, 2018, 2019

    NOTE: Years 2020–2025 use a standalone format and should be processed
    with 'extract_ssm_standalone.py' instead.

Dependencies:
    - pdfplumber (PDF text extraction)
    - openpyxl (XLSX output generation)

Usage:
    python extract_ssm_scenario.py

Author: ITAMed Dataset Team
==============================================================================
"""

import os
import re
import sys
import pdfplumber
import openpyxl

# ==============================================================================
# Configuration
# ==============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(BASE_DIR, "Pdf_Data")
OUTPUT_DIR = os.path.join(BASE_DIR, "Data")

# Years to process (scenario-based format only)
YEARS = [2017, 2018, 2019]

# Expected number of questions per exam
EXPECTED_QUESTIONS = 140

# ==============================================================================
# Core Extraction Logic
# ==============================================================================

# Pattern for scenario headers: "Scenario N:"
SCENARIO_PATTERN = re.compile(r'Scenario\s+(\d+):\s*\n?')

# Pattern for question headers with optional scenario reference:
# "Domanda N: (codice domanda: XXXXX) - (riferita allo scenario n.Y) :"
QUESTION_PATTERN = re.compile(
    r'Domanda\s+(\d+):\s*\(codice domanda:\s*(\w+)\)\s*'
    r'(?:-\s*\(riferita allo scenario n\.(\d+)\))?\s*:\s*\n?'
)

# Pattern for answer options at the beginning of a line
OPTION_PATTERN = re.compile(
    r'^([A-E]):\s*(.*?)(?=\n[A-E]:\s|$)',
    re.DOTALL | re.MULTILINE
)


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text content from a PDF file.

    Args:
        pdf_path: Absolute path to the PDF file.

    Returns:
        Concatenated text from all pages, separated by newlines.
    """
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text


def clean_text(full_text: str) -> str:
    """
    Remove repeated headers and footers from the extracted text.

    The 2017–2019 PDFs include repeating page elements:
        - "In tutti i quesiti proposti la soluzione è la risposta alla lettera A)"
        - "Prova generale del DD/MM/YYYY"
        - Page numbers appearing alone

    Args:
        full_text: Raw concatenated text from all PDF pages.

    Returns:
        Cleaned text with headers/footers removed.
    """
    # Remove footer with page number
    cleaned = re.sub(
        r'In tutti i quesiti proposti la soluzione è la risposta alla lettera'
        r'\s*A\)\s*\d+',
        '',
        full_text
    )
    # Remove page header with date
    cleaned = re.sub(r'Prova generale del \d{2}/\d{2}/\d{4}\n?', '', cleaned)
    return cleaned


def parse_markers(full_text: str) -> list:
    """
    Identify and sort all structural markers (scenarios and questions).

    Markers are sorted by their position in the text, enabling linear
    processing where each marker's content extends until the next marker.

    Args:
        full_text: Cleaned text from the PDF.

    Returns:
        List of marker tuples, sorted by position. Each tuple contains:
        - For scenarios: ('scenario', number, start_pos, end_pos, match_obj)
        - For questions: ('question', number, start_pos, end_pos, match_obj,
                          code, scenario_ref_or_None)
    """
    markers = []

    # Find all scenario markers
    for m in SCENARIO_PATTERN.finditer(full_text):
        markers.append((
            'scenario',
            int(m.group(1)),
            m.start(),
            m.end(),
            m
        ))

    # Find all question markers
    for m in QUESTION_PATTERN.finditer(full_text):
        scenario_ref = int(m.group(3)) if m.group(3) else None
        markers.append((
            'question',
            int(m.group(1)),
            m.start(),
            m.end(),
            m,
            m.group(2),      # question code
            scenario_ref     # referenced scenario number or None
        ))

    # Sort by position in text (critical for linear processing)
    markers.sort(key=lambda x: x[2])
    return markers


def extract_options(block: str) -> tuple:
    """
    Extract answer options A–E from a question text block.

    Options are expected at the beginning of lines in format "X: text"
    where X is a letter A through E.

    Args:
        block: Text between this question's header and the next marker.

    Returns:
        Tuple of (options_dict, first_option_position) where options_dict
        maps letters A–E to their answer text, or (None, 0) on failure.
    """
    matches = list(OPTION_PATTERN.finditer(block))
    letters = sorted([m.group(1) for m in matches])

    if letters == ['A', 'B', 'C', 'D', 'E']:
        options = {}
        for m in matches:
            text = m.group(2).strip()
            text = re.sub(r'\s+', ' ', text).strip()
            options[m.group(1)] = text
        return options, matches[0].start()

    return None, 0


def process_year(year: int) -> list:
    """
    Process a single year's scenario-based PDF and extract all 140 questions.

    The algorithm:
        1. Extract and clean PDF text
        2. Identify all scenario and question markers
        3. Build scenario text dictionary
        4. For each question:
           a. Extract the text block
           b. Parse answer options
           c. If the question references a scenario, prepend scenario text
           d. Store the complete, self-contained question

    Args:
        year: The exam year (2017–2019).

    Returns:
        List of question dictionaries with keys:
        'number', 'code', 'question', 'A', 'B', 'C', 'D', 'E'
    """
    pdf_path = os.path.join(PDF_DIR, f"{year}_answers.pdf")

    if not os.path.exists(pdf_path):
        print(f"  ERROR: PDF not found: {pdf_path}")
        return []

    # Step 1: Extract and clean text
    full_text = extract_text_from_pdf(pdf_path)
    full_text = clean_text(full_text)

    # Step 2: Parse all structural markers
    markers = parse_markers(full_text)

    # Step 3: Process markers linearly
    scenarios = {}
    questions = []

    for i, marker in enumerate(markers):
        # Define the text block: from end of this marker to start of next
        block_start = marker[3]
        block_end = markers[i + 1][2] if i + 1 < len(markers) else len(full_text)
        block = full_text[block_start:block_end].strip()

        if marker[0] == 'scenario':
            # Store scenario text
            scenario_num = marker[1]
            scenarios[scenario_num] = re.sub(r'\s+', ' ', block).strip()

        elif marker[0] == 'question':
            q_num = marker[1]
            q_code = marker[5]
            scenario_ref = marker[6]

            # Extract answer options
            options, opts_start = extract_options(block)

            if options is None:
                print(f"  ERROR: Failed to extract options for Q{q_num} ({q_code})")
                options = {'A': '', 'B': '', 'C': '', 'D': '', 'E': ''}
                opts_start = len(block)

            # Extract question text (everything before first option)
            question_text = block[:opts_start].strip()
            question_text = re.sub(r'\s+', ' ', question_text).strip()

            # Prepend scenario text if this question references one
            if scenario_ref and scenario_ref in scenarios:
                scenario_text = scenarios[scenario_ref]
                if scenario_text:
                    question_text = scenario_text + " " + question_text

            # Remove trailing colon if present
            if question_text.endswith(':'):
                question_text = question_text[:-1].strip()

            questions.append({
                'number': q_num,
                'code': q_code,
                'question': question_text,
                'A': options.get('A', ''),
                'B': options.get('B', ''),
                'C': options.get('C', ''),
                'D': options.get('D', ''),
                'E': options.get('E', ''),
            })

    # Sort by question number
    questions.sort(key=lambda x: x['number'])

    print(f"  Scenarios found: {len(scenarios)}")
    return questions


def save_to_xlsx(questions: list, output_path: str, year: int) -> None:
    """
    Save extracted questions to an XLSX file.

    Args:
        questions: List of question dictionaries.
        output_path: Path for the output XLSX file.
        year: Exam year (used for sheet title).
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"SSM_{year}"

    # Header row
    headers = [
        'Codice Domanda', 'Domanda',
        'Risposta A', 'Risposta B', 'Risposta C',
        'Risposta D', 'Risposta E'
    ]
    ws.append(headers)

    # Data rows
    for q in questions:
        ws.append([
            q['code'], q['question'],
            q['A'], q['B'], q['C'], q['D'], q['E']
        ])

    wb.save(output_path)


def validate_extraction(questions: list, year: int) -> bool:
    """
    Validate the extracted questions for completeness and correctness.

    Checks:
        - Exactly 140 questions extracted
        - All question numbers 1–140 are present
        - No empty question text
        - All questions have 5 non-empty options

    Args:
        questions: List of extracted question dictionaries.
        year: Exam year for reporting.

    Returns:
        True if all validations pass, False otherwise.
    """
    valid = True

    # Check count
    if len(questions) != EXPECTED_QUESTIONS:
        print(f"  FAIL: {len(questions)} questions (expected {EXPECTED_QUESTIONS})")
        valid = False

    # Check completeness
    found_nums = set(q['number'] for q in questions)
    expected_nums = set(range(1, EXPECTED_QUESTIONS + 1))
    missing = expected_nums - found_nums
    if missing:
        print(f"  FAIL: Missing question numbers: {sorted(missing)}")
        valid = False

    # Check for empty content
    empty_questions = [q['number'] for q in questions if not q['question']]
    if empty_questions:
        print(f"  FAIL: Empty question text for: {empty_questions}")
        valid = False

    empty_options = [
        q['number'] for q in questions
        if not all(q[opt] for opt in 'ABCDE')
    ]
    if empty_options:
        print(f"  FAIL: Incomplete options for: {empty_options}")
        valid = False

    return valid


# ==============================================================================
# Main Execution
# ==============================================================================

def main():
    """
    Main entry point. Processes all scenario-based PDFs (2017–2019),
    extracts questions with their referenced scenarios, validates results,
    and saves to XLSX.
    """
    print("=" * 70)
    print("ITAMed — Scenario-Based Question Extraction (2017–2019)")
    print("=" * 70)
    print(f"  PDF directory:    {PDF_DIR}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"  Years:            {YEARS}")
    print()
    print("  NOTE: This script is ONLY applicable to years 2017–2019.")
    print("        These exams use a scenario-based format where questions")
    print("        may reference shared clinical scenarios.")
    print("        For years 2020–2025, use 'extract_ssm_standalone.py'.")
    print()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_passed = True

    for year in YEARS:
        print(f"--- {year} ---")

        # Extract
        questions = process_year(year)
        if not questions:
            all_passed = False
            continue

        # Validate
        passed = validate_extraction(questions, year)
        if not passed:
            all_passed = False

        # Save
        output_path = os.path.join(OUTPUT_DIR, f"{year}_answers.xlsx")
        save_to_xlsx(questions, output_path, year)

        print(f"  Extracted: {len(questions)} questions")
        print(f"  Output:    {output_path}")
        print(f"  Status:    {'PASS' if passed else 'FAIL'}")
        print()

    # Summary
    print("=" * 70)
    print(f"RESULT: {'ALL YEARS PASSED' if all_passed else 'SOME YEARS FAILED'}")
    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
