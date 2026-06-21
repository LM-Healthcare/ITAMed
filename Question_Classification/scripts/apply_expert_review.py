"""
==============================================================================
ITAMed — Apply Expert Review to Dataset
==============================================================================

Purpose:
    Reads the expert-reviewed discordance file and updates the official
    ITAMed dataset files with the adjudicated category decisions.

    This script is the final step in the dual-annotator classification
    pipeline. After two LLMs independently classify questions and medical
    experts resolve disagreements, this script propagates the final
    categories back into the official dataset.

Input:
    - Expert review file:
      Question_Classification/expert_review/discordances_to_review.xlsx
      (column 'CATEGORIA FINALE (compilare)' must be filled for all rows)

    - Original dataset files:
      Official/IT/ITAMed_{year}_Checked.xlsx
      Official/IT/ITAMed_complete.json
      Official/IT/ITAMed_complete.xlsx

Output:
    Updated versions of:
      - Official/IT/ITAMed_{year}_Checked.xlsx (per-year files)
      - Official/IT/ITAMed_complete.json (consolidated JSON)
      - Official/IT/ITAMed_complete.xlsx (consolidated XLSX)

    A backup of original files is created in:
      Official/IT/backup_pre_review/

Requirements:
    - openpyxl>=3.1
    - pandas>=2.0

Usage:
    python apply_expert_review.py

Author: ITAMed Dataset Team
==============================================================================
"""

import os
import sys
import json
import shutil
from datetime import datetime

import openpyxl
import pandas as pd

# ==============================================================================
# Configuration
# ==============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OFFICIAL_DIR = os.path.join(BASE_DIR, "Official", "IT")
REVIEW_FILE = os.path.join(
    BASE_DIR, "Question_Classification", "expert_review", "discordances_to_review.xlsx"
)
BACKUP_DIR = os.path.join(OFFICIAL_DIR, "backup_pre_review")

YEARS = list(range(2017, 2026))


# ==============================================================================
# Core Logic
# ==============================================================================


def load_expert_decisions() -> dict:
    """
    Load expert-reviewed categories from the discordance review file.

    Returns:
        Dictionary mapping (year, question_number) -> final_category.

    Raises:
        SystemExit if the review file has unfilled rows.
    """
    if not os.path.exists(REVIEW_FILE):
        print(f"ERROR: Review file not found: {REVIEW_FILE}")
        sys.exit(1)

    wb = openpyxl.load_workbook(REVIEW_FILE)
    ws = wb.active

    decisions = {}
    missing = []

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        year = row[0].value          # Anno
        q_num = row[1].value         # N. Domanda
        final_cat = row[11].value    # CATEGORIA FINALE (col L, 0-indexed = 11)

        if not final_cat or str(final_cat).strip() == "":
            missing.append(f"  Year {year}, Question {q_num}")
        else:
            decisions[(int(year), int(q_num))] = str(final_cat).strip()

    if missing:
        print("ERROR: The following discordances have NOT been reviewed:")
        for m in missing[:20]:
            print(m)
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more")
        print(f"\nTotal unfilled: {len(missing)} / {len(missing) + len(decisions)}")
        print("Please complete the review file before running this script.")
        sys.exit(1)

    return decisions


def backup_originals():
    """Create a timestamped backup of all original dataset files."""
    os.makedirs(BACKUP_DIR, exist_ok=True)

    files_to_backup = []
    for year in YEARS:
        f = os.path.join(OFFICIAL_DIR, f"ITAMed_{year}_Checked.xlsx")
        if os.path.exists(f):
            files_to_backup.append(f)

    for f in ["ITAMed_complete.json", "ITAMed_complete.xlsx"]:
        path = os.path.join(OFFICIAL_DIR, f)
        if os.path.exists(path):
            files_to_backup.append(path)

    for src in files_to_backup:
        dst = os.path.join(BACKUP_DIR, os.path.basename(src))
        shutil.copy2(src, dst)

    print(f"  Backup created: {BACKUP_DIR} ({len(files_to_backup)} files)")


def update_yearly_xlsx(decisions: dict) -> int:
    """
    Update per-year XLSX files with expert-adjudicated categories.

    Args:
        decisions: Dict mapping (year, q_num) -> final_category.

    Returns:
        Number of cells updated.
    """
    updated = 0

    for year in YEARS:
        xlsx_path = os.path.join(OFFICIAL_DIR, f"ITAMed_{year}_Checked.xlsx")
        if not os.path.exists(xlsx_path):
            continue

        wb = openpyxl.load_workbook(xlsx_path)
        ws = wb.active

        year_updates = 0
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            row_year = row[0].value
            q_num = row[1].value
            key = (int(row_year), int(q_num))

            if key in decisions:
                old_cat = row[10].value
                new_cat = decisions[key]
                row[10].value = new_cat
                year_updates += 1
                updated += 1

        if year_updates > 0:
            wb.save(xlsx_path)
            print(f"  {year}: updated {year_updates} categories")

    return updated


def update_complete_json(decisions: dict) -> int:
    """
    Update the consolidated JSON file with expert-adjudicated categories.

    Args:
        decisions: Dict mapping (year, q_num) -> final_category.

    Returns:
        Number of records updated.
    """
    json_path = os.path.join(OFFICIAL_DIR, "ITAMed_complete.json")
    if not os.path.exists(json_path):
        print("  WARNING: ITAMed_complete.json not found, skipping")
        return 0

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    for item in data:
        key = (int(item["year"]), int(item["question_number"]))
        if key in decisions:
            item["category"] = decisions[key]
            updated += 1

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  ITAMed_complete.json: updated {updated} records")
    return updated


def update_complete_xlsx(decisions: dict) -> int:
    """
    Update the consolidated XLSX file with expert-adjudicated categories.

    Args:
        decisions: Dict mapping (year, q_num) -> final_category.

    Returns:
        Number of cells updated.
    """
    xlsx_path = os.path.join(OFFICIAL_DIR, "ITAMed_complete.xlsx")
    if not os.path.exists(xlsx_path):
        print("  WARNING: ITAMed_complete.xlsx not found, skipping")
        return 0

    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active

    updated = 0
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        row_year = row[0].value
        q_num = row[1].value
        if row_year and q_num:
            key = (int(row_year), int(q_num))
            if key in decisions:
                row[10].value = decisions[key]
                updated += 1

    wb.save(xlsx_path)
    print(f"  ITAMed_complete.xlsx: updated {updated} records")
    return updated


# ==============================================================================
# Main Execution
# ==============================================================================


def main():
    """
    Main entry point. Loads expert decisions, backs up originals, and
    applies the reviewed categories to all official dataset files.
    """
    print("=" * 70)
    print("ITAMed — Apply Expert Review")
    print("=" * 70)
    print()

    # Load decisions
    print("Loading expert decisions...")
    decisions = load_expert_decisions()
    print(f"  Found {len(decisions)} adjudicated discordances")
    print()

    # Backup
    print("Creating backup of original files...")
    backup_originals()
    print()

    # Apply updates
    print("Updating per-year XLSX files...")
    n_yearly = update_yearly_xlsx(decisions)
    print()

    print("Updating consolidated JSON...")
    n_json = update_complete_json(decisions)
    print()

    print("Updating consolidated XLSX...")
    n_xlsx = update_complete_xlsx(decisions)
    print()

    # Summary
    print("=" * 70)
    print("REVIEW APPLIED SUCCESSFULLY")
    print(f"  Total discordances resolved: {len(decisions)}")
    print(f"  Yearly XLSX updates:         {n_yearly}")
    print(f"  Complete JSON updates:        {n_json}")
    print(f"  Complete XLSX updates:        {n_xlsx}")
    print(f"  Backup location:             {BACKUP_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
