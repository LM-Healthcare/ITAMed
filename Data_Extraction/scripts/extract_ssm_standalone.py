"""
==============================================================================
ITAMed — Standalone Question Extraction Script
==============================================================================

Purpose:
    Extracts multiple-choice questions from the Italian National Medical
    Specialization Exam (Concorso SSM) PDF documents in standalone format
    (years 2020–2025).

Input:
    Official PDF answer documents located in the 'pdf_sources/' directory.
    Expected filename format: '{year}_answers.pdf'
    Each PDF contains 140 questions with 5 answer options (A–E).

Output:
    One XLSX file per year in 'Data_Extraction/output/' with columns:
        - Codice Domanda (question code)
        - Domanda (question text)
        - Risposta A through E (answer options A–E)

Format Notes:
    - Years 2020–2024 use plain text format (A: ... B: ... C: ... D: ... E: ...)
    - Year 2025 uses checkbox format (☒ A: ... ☐ B: ... etc.)
    - The correct answer is ALWAYS option A (as per official released format)
    - This script handles ALL format variations automatically

Applicable Years:
    2020, 2021, 2022, 2023, 2024, 2025

Dependencies:
    - pdfplumber (PDF text extraction)
    - openpyxl (XLSX output generation)

Usage:
    python extract_ssm_standalone.py

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

EXTRACTION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(EXTRACTION_DIR, "pdf_sources")
OUTPUT_DIR = os.path.join(EXTRACTION_DIR, "output")

# Years to process (standalone format only)
YEARS = [2020, 2021, 2022, 2023, 2024, 2025]

# Expected number of questions per exam
EXPECTED_QUESTIONS = 140

# ==============================================================================
# Core Extraction Logic
# ==============================================================================

# Regex pattern to identify question headers across all format variants.
# Handles variable spacing across all format variants.
QUESTION_HEADER_PATTERN = re.compile(
    r'Domanda\s*(\d+)\s*:\s*\(codice\s*domanda\s*:\s*(ssm\w+)\)'
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


def extract_options(block: str) -> tuple:
    """
    Extract answer options A–E from a question text block.

    Uses a multi-pass strategy to handle different PDF format variants:
      1. Newline-based parsing (standard format: 2020–2022, 2024)
      2. Newline with checkbox markers (2025 format)
      3. Inline option detection with preprocessing (edge cases)

    Args:
        block: Raw text between two question headers.

    Returns:
        Tuple of (options_dict, first_option_position) where options_dict
        maps letters A–E to their answer text, or (None, 0) on failure.
    """
    # --- Pass 1: Standard newline-based format ---
    # Options appear at the beginning of a line, optionally with checkbox markers
    opt_newline = re.compile(
        r'(?:^|\n)\s*(?:[☒☐]\s*)?([A-E]):\s*(.*?)'
        r'(?=(?:\n)\s*(?:[☒☐]\s*)?[A-E]:\s|(?:\n)\s*CC:|$)',
        re.DOTALL
    )
    matches = list(opt_newline.finditer(block))
    letters = sorted([m.group(1) for m in matches])
    if letters == ['A', 'B', 'C', 'D', 'E']:
        options = {m.group(1): m.group(2).strip() for m in matches}
        return options, matches[0].start()

    # --- Pass 2: Split-based parsing (fallback for non-standard spacing) ---
    # Options start on their own line but text may lack word spacing
    opt_line_start = re.compile(r'(?:^|\n)([A-E]):', re.MULTILINE)
    splits = list(opt_line_start.finditer(block))
    if len(splits) >= 5:
        letters2 = [s.group(1) for s in splits[:5]]
        if sorted(letters2) == ['A', 'B', 'C', 'D', 'E']:
            options = {}
            first_pos = splits[0].start()
            for j in range(5):
                letter = splits[j].group(1)
                start = splits[j].end()
                end = splits[j + 1].start() if j + 1 < len(splits) else len(block)
                text = block[start:end].strip()
                # Remove commentary block (CC:) if present
                cc_match = re.search(r'\nCC:', text)
                if cc_match:
                    text = text[:cc_match.start()].strip()
                options[letter] = re.sub(r'\s+', ' ', text).strip()
            return options, first_pos

    # --- Pass 3: Inline option detection (edge cases) ---
    # Some options appear inline without a preceding newline (e.g., "...testo B:...")
    # Insert newline before inline [B-E]: that follow lowercase/punctuation
    processed = re.sub(r'([a-zà-ú\)\.0-9])([B-E]:)', r'\1\n\2', block)
    splits3 = list(opt_line_start.finditer(processed))
    if len(splits3) >= 5:
        letters3 = [s.group(1) for s in splits3[:5]]
        if sorted(letters3) == ['A', 'B', 'C', 'D', 'E']:
            options = {}
            for j in range(5):
                letter = splits3[j].group(1)
                start = splits3[j].end()
                end = splits3[j + 1].start() if j + 1 < len(splits3) else len(processed)
                text = processed[start:end].strip()
                cc_match = re.search(r'\nCC:', text)
                if cc_match:
                    text = text[:cc_match.start()].strip()
                options[letter] = re.sub(r'\s+', ' ', text).strip()
            first_pos = block.find('A:')
            return options, max(first_pos, 0)

    return None, 0


def extract_question_text(block: str, options_start: int) -> str:
    """
    Extract the question text (clinical vignette + stem) from the block.

    The question text is everything before the first answer option.
    Commentary and metadata are stripped.

    Args:
        block: Full text block for this question.
        options_start: Character position where answer options begin.

    Returns:
        Cleaned question text string.
    """
    raw = block[:options_start].strip() if options_start > 0 else block.strip()
    # Normalize whitespace (collapse multiple spaces/newlines into single space)
    cleaned = re.sub(r'\s+', ' ', raw).strip()
    # Remove trailing colon if present
    if cleaned.endswith(':'):
        cleaned = cleaned[:-1].strip()
    return cleaned


def process_year(year: int) -> list:
    """
    Process a single year's PDF and extract all 140 questions.

    Args:
        year: The exam year (2020–2025).

    Returns:
        List of question dictionaries with keys:
        'number', 'code', 'question', 'A', 'B', 'C', 'D', 'E'
    """
    pdf_path = os.path.join(PDF_DIR, f"{year}_answers.pdf")

    if not os.path.exists(pdf_path):
        print(f"  ERROR: PDF not found: {pdf_path}")
        return []

    # Step 1: Extract raw text
    full_text = extract_text_from_pdf(pdf_path)

    # Step 2: Locate all question headers
    headers = list(QUESTION_HEADER_PATTERN.finditer(full_text))

    if len(headers) != EXPECTED_QUESTIONS:
        print(f"  WARNING: Found {len(headers)} question headers "
              f"(expected {EXPECTED_QUESTIONS})")

    # Step 3: Parse each question
    questions = []
    for i, header in enumerate(headers):
        q_num = int(header.group(1))
        q_code = header.group(2)

        # Define the text block for this question
        block_start = header.end()
        block_end = headers[i + 1].start() if i + 1 < len(headers) else len(full_text)
        block = full_text[block_start:block_end].strip()

        # Extract answer options
        options, opts_start = extract_options(block)

        if options is None:
            print(f"  ERROR: Failed to extract options for Q{q_num} ({q_code})")
            options = {'A': '', 'B': '', 'C': '', 'D': '', 'E': ''}
            opts_start = len(block)

        # Extract question text
        question_text = extract_question_text(block, opts_start)

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

    # Sort by question number (should already be in order)
    questions.sort(key=lambda x: x['number'])
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
    Main entry point. Processes all standalone-format PDFs (2020–2025),
    extracts questions, validates results, and saves to XLSX.
    """
    print("=" * 70)
    print("ITAMed — Standalone Question Extraction (2020–2025)")
    print("=" * 70)
    print(f"  PDF directory:    {PDF_DIR}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"  Years:            {YEARS}")
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
