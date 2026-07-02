"""
==============================================================================
ITAMed — Apply Translation Review to Official EN Dataset
==============================================================================

Purpose:
    After the expert medical review of the English translation, this script:

    1. Extracts all corrections from the reviewed XLSX file into a structured
       JSON log (translation_corrections.json)
    2. Applies those corrections to all official EN dataset files
       (per-year and complete, both XLSX and JSON)
    3. Generates a tracked-changes XLSX where modified cells are highlighted
       with the original text preserved in cell comments — analogous to
       Word's track-changes feature

Input:
    - Dataset_Translation/ITAMed_complete_EN_translation_TO_CHECK.xlsx
      (reviewed by the medical expert, with corrections in columns J–P)

Output:
    - Dataset_Translation/translation_corrections.json  (structured log)
    - Dataset/EN/xlsx/ITAMed_{year}_EN.xlsx             (updated)
    - Dataset/EN/xlsx/ITAMed_complete_EN.xlsx            (updated)
    - Dataset/EN/json/ITAMed_{year}_EN.json             (updated)
    - Dataset/EN/json/ITAMed_complete_EN.json            (updated)
    - Dataset/EN/ITAMed_complete_EN_tracked.xlsx         (tracked-changes)

Usage:
    python apply_translation_review.py

Author: ITAMed Dataset Team
=============================================================================="""

import os
import sys
import json
import shutil
from datetime import datetime

import openpyxl
from openpyxl.styles import PatternFill, Font
from openpyxl.comments import Comment

# ==============================================================================
# Configuration
# ==============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TRANSLATION_DIR = os.path.dirname(SCRIPT_DIR)
REPO_ROOT = os.path.dirname(TRANSLATION_DIR)

REVIEW_FILE = os.path.join(TRANSLATION_DIR, "ITAMed_complete_EN_translation_TO_CHECK.xlsx")
EN_XLSX_DIR = os.path.join(REPO_ROOT, "Dataset", "EN", "xlsx")
EN_JSON_DIR = os.path.join(REPO_ROOT, "Dataset", "EN", "json")
EN_DIR = os.path.join(REPO_ROOT, "Dataset", "EN")
BACKUP_DIR = os.path.join(EN_DIR, "backup_pre_translation_review")

YEARS = list(range(2017, 2026))

# Tracked-changes styling
HIGHLIGHT_FILL = PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")
STRIKETHROUGH_FONT = Font(strikethrough=True, color="999999")


# ==============================================================================
# Load Review Data
# ==============================================================================


def load_review_data() -> dict:
    """
    Load modifications from the review file.

    Returns:
        Dict keyed by question_code, each containing:
        {
            "question": revised_text or None,
            "A": revised_text or None,
            ...
            "E": revised_text or None,
            "comment": str or None
        }
    """
    wb = openpyxl.load_workbook(REVIEW_FILE)
    ws = wb.active

    modifications = {}
    total_checked = 0

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        q_code = row[2].value  # Column C
        if not q_code:
            continue

        q_checked = row[9].value    # Column J
        a_checked = row[10].value   # Column K
        b_checked = row[11].value   # Column L
        c_checked = row[12].value   # Column M
        d_checked = row[13].value   # Column N
        e_checked = row[14].value   # Column O
        comment = row[15].value     # Column P

        has_modification = any([q_checked, a_checked, b_checked,
                                c_checked, d_checked, e_checked])

        if has_modification:
            modifications[str(q_code)] = {
                "question": q_checked,
                "A": a_checked,
                "B": b_checked,
                "C": c_checked,
                "D": d_checked,
                "E": e_checked,
                "comment": comment,
            }
            total_checked += 1

    return modifications


# ==============================================================================
# Backup
# ==============================================================================


def create_backup():
    """Backup all current EN files before applying changes."""
    if os.path.exists(BACKUP_DIR):
        print(f"  Backup already exists at {BACKUP_DIR}")
        print(f"  Skipping backup (delete manually to re-backup)")
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Backup XLSX
    xlsx_backup = os.path.join(BACKUP_DIR, "xlsx")
    os.makedirs(xlsx_backup, exist_ok=True)
    for f in os.listdir(EN_XLSX_DIR):
        if f.endswith(".xlsx"):
            shutil.copy2(os.path.join(EN_XLSX_DIR, f), xlsx_backup)

    # Backup JSON
    json_backup = os.path.join(BACKUP_DIR, "json")
    os.makedirs(json_backup, exist_ok=True)
    for f in os.listdir(EN_JSON_DIR):
        if f.endswith(".json"):
            shutil.copy2(os.path.join(EN_JSON_DIR, f), json_backup)

    print(f"  Backup created at {BACKUP_DIR}")


# ==============================================================================
# Apply to XLSX
# ==============================================================================

# Column mapping for EN dataset XLSX files
# Headers: Year(1) | Q.Number(2) | Q.Code(3) | Question(4) | A(5) | B(6) | C(7) | D(8) | E(9) | ...
COL_QUESTION = 4
COL_A = 5
COL_B = 6
COL_C = 7
COL_D = 8
COL_E = 9


def apply_to_xlsx(xlsx_path: str, modifications: dict) -> int:
    """
    Apply modifications to an EN dataset XLSX file.

    Returns number of cells updated.
    """
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active
    cells_updated = 0

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        q_code = str(row[2].value)  # Column C (index 2)
        if q_code not in modifications:
            continue

        mod = modifications[q_code]

        if mod["question"]:
            row[COL_QUESTION - 1].value = mod["question"]
            cells_updated += 1
        if mod["A"]:
            row[COL_A - 1].value = mod["A"]
            cells_updated += 1
        if mod["B"]:
            row[COL_B - 1].value = mod["B"]
            cells_updated += 1
        if mod["C"]:
            row[COL_C - 1].value = mod["C"]
            cells_updated += 1
        if mod["D"]:
            row[COL_D - 1].value = mod["D"]
            cells_updated += 1
        if mod["E"]:
            row[COL_E - 1].value = mod["E"]
            cells_updated += 1

    wb.save(xlsx_path)
    return cells_updated


def apply_to_all_xlsx(modifications: dict) -> int:
    """Apply modifications to all per-year and complete XLSX files."""
    total_cells = 0

    for year in YEARS:
        path = os.path.join(EN_XLSX_DIR, f"ITAMed_{year}_EN.xlsx")
        if not os.path.exists(path):
            print(f"    WARNING: {path} not found")
            continue
        cells = apply_to_xlsx(path, modifications)
        if cells > 0:
            print(f"    {year}: {cells} cells updated")
        total_cells += cells

    # Complete file
    complete_path = os.path.join(EN_XLSX_DIR, "ITAMed_complete_EN.xlsx")
    if os.path.exists(complete_path):
        cells = apply_to_xlsx(complete_path, modifications)
        print(f"    complete: {cells} cells updated")
        total_cells += cells

    return total_cells


# ==============================================================================
# Apply to JSON
# ==============================================================================

# JSON key mapping
JSON_KEY_MAP = {
    "question": "question",
    "A": "answer_a",
    "B": "answer_b",
    "C": "answer_c",
    "D": "answer_d",
    "E": "answer_e",
}


def apply_to_json(json_path: str, modifications: dict) -> int:
    """Apply modifications to an EN dataset JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fields_updated = 0

    for item in data:
        q_code = item.get("question_code", "")
        if q_code not in modifications:
            continue

        mod = modifications[q_code]
        for review_key, json_key in JSON_KEY_MAP.items():
            if mod[review_key]:
                item[json_key] = mod[review_key]
                fields_updated += 1

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return fields_updated


def apply_to_all_json(modifications: dict) -> int:
    """Apply modifications to all per-year and complete JSON files."""
    total_fields = 0

    for year in YEARS:
        path = os.path.join(EN_JSON_DIR, f"ITAMed_{year}_EN.json")
        if not os.path.exists(path):
            continue
        fields = apply_to_json(path, modifications)
        if fields > 0:
            print(f"    {year}: {fields} fields updated")
        total_fields += fields

    complete_path = os.path.join(EN_JSON_DIR, "ITAMed_complete_EN.json")
    if os.path.exists(complete_path):
        fields = apply_to_json(complete_path, modifications)
        print(f"    complete: {fields} fields updated")
        total_fields += fields

    return total_fields


# ==============================================================================
# Tracked Changes XLSX
# ==============================================================================


def create_tracked_changes_xlsx(modifications: dict):
    """
    Create a tracked-changes version of the complete EN dataset.

    Modified cells are:
    - Highlighted in yellow
    - Contain the NEW (corrected) text as the cell value
    - Have a comment showing "Original: <old text>" + reviewer note

    This mimics Word's track-changes feature in Excel.
    """
    source_path = os.path.join(BACKUP_DIR, "xlsx", "ITAMed_complete_EN.xlsx")
    if not os.path.exists(source_path):
        # Fallback: use current file (before applying changes)
        source_path = os.path.join(EN_XLSX_DIR, "ITAMed_complete_EN.xlsx")

    output_path = os.path.join(EN_DIR, "ITAMed_complete_EN_tracked.xlsx")

    wb = openpyxl.load_workbook(source_path)
    ws = wb.active

    # Add a "Review Notes" column header
    notes_col = ws.max_column + 1
    ws.cell(row=1, column=notes_col, value="Review Notes")
    ws.cell(row=1, column=notes_col).font = Font(bold=True)

    changes_applied = 0

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        q_code = str(row[2].value)  # Column C
        if q_code not in modifications:
            continue

        mod = modifications[q_code]

        field_map = {
            "question": COL_QUESTION - 1,
            "A": COL_A - 1,
            "B": COL_B - 1,
            "C": COL_C - 1,
            "D": COL_D - 1,
            "E": COL_E - 1,
        }

        row_has_changes = False

        for field_key, col_idx in field_map.items():
            new_text = mod[field_key]
            if not new_text:
                continue

            cell = row[col_idx]
            original_text = str(cell.value) if cell.value else ""

            # Set new value
            cell.value = new_text

            # Highlight in yellow
            cell.fill = HIGHLIGHT_FILL

            # Add comment with original text (truncated if very long)
            orig_preview = original_text[:300]
            if len(original_text) > 300:
                orig_preview += "..."
            cell.comment = Comment(
                f"Original: {orig_preview}",
                "Medical Reviewer",
                width=400,
                height=150,
            )

            row_has_changes = True
            changes_applied += 1

        # Add review note in the extra column
        if row_has_changes and mod["comment"]:
            ws.cell(row=row[0].row, column=notes_col, value=mod["comment"])

    # Auto-width for notes column
    ws.column_dimensions[openpyxl.utils.get_column_letter(notes_col)].width = 50

    wb.save(output_path)
    print(f"  Tracked-changes file: {output_path}")
    print(f"  Highlighted cells: {changes_applied}")


# ==============================================================================
# Main
# ==============================================================================


def main():
    print("=" * 70)
    print("ITAMed — Apply Translation Review to EN Dataset")
    print("=" * 70)
    print()

    # Step 1: Load review data and extract corrections
    print("Step 1: Extracting corrections from reviewed XLSX...")
    if not os.path.exists(REVIEW_FILE):
        print(f"  ERROR: Review file not found: {REVIEW_FILE}")
        sys.exit(1)

    modifications = load_review_data()
    print(f"  Questions with modifications: {len(modifications)}")
    if not modifications:
        print("  No modifications found. Nothing to do.")
        return

    # Count per-field stats
    field_counts = {"question": 0, "A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
    for mod in modifications.values():
        for field in field_counts:
            if mod[field]:
                field_counts[field] += 1
    total_corrections = sum(field_counts.values())
    print(f"  Total corrections: {total_corrections}")
    print(f"  Breakdown: Q={field_counts['question']} A={field_counts['A']} "
          f"B={field_counts['B']} C={field_counts['C']} "
          f"D={field_counts['D']} E={field_counts['E']}")

    # Save corrections as JSON
    corrections_path = os.path.join(TRANSLATION_DIR, "translation_corrections.json")
    corrections_export = {}
    for q_code, mod in modifications.items():
        entry = {}
        if mod["question"]:
            entry["question"] = mod["question"]
        if mod["A"]:
            entry["answer_a"] = mod["A"]
        if mod["B"]:
            entry["answer_b"] = mod["B"]
        if mod["C"]:
            entry["answer_c"] = mod["C"]
        if mod["D"]:
            entry["answer_d"] = mod["D"]
        if mod["E"]:
            entry["answer_e"] = mod["E"]
        if mod["comment"]:
            entry["comment"] = mod["comment"]
        corrections_export[q_code] = entry

    with open(corrections_path, "w", encoding="utf-8") as f:
        json.dump(corrections_export, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {corrections_path}")
    print()

    # Step 2: Backup
    print("Step 2: Creating backup...")
    create_backup()
    print()

    # Step 3: Generate tracked-changes version BEFORE applying changes
    print("Step 3: Generating tracked-changes XLSX...")
    create_tracked_changes_xlsx(modifications)
    print()

    # Step 4: Apply to XLSX
    print("Step 4: Applying corrections to XLSX files...")
    xlsx_cells = apply_to_all_xlsx(modifications)
    print(f"  Total XLSX cells updated: {xlsx_cells}")
    print()

    # Step 5: Apply to JSON
    print("Step 5: Applying corrections to JSON files...")
    json_fields = apply_to_all_json(modifications)
    print(f"  Total JSON fields updated: {json_fields}")
    print()

    print("=" * 70)
    print("TRANSLATION REVIEW APPLIED SUCCESSFULLY")
    print()
    print("Output files:")
    print(f"  Corrections log:  {corrections_path}")
    print(f"  Clean version:    Dataset/EN/xlsx/ and Dataset/EN/json/")
    print(f"  Tracked changes:  Dataset/EN/ITAMed_complete_EN_tracked.xlsx")
    print(f"  Backup:           {BACKUP_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
