"""
==============================================================================
ITAMed — Apply Final Category Assignments to All Dataset Files
==============================================================================

Purpose:
    Builds the complete final category mapping for ALL 1,260 questions by
    combining three sources:

      1. 880 LLM-concordant questions (Claude = GPT) → use agreed category
      2. 254 reviewer-concordant questions (R1 = R2) → use agreed category
      3. 126 resolved discordances → use consensus resolution

    Then applies the final categories to ALL official dataset files:
      - IT JSON + XLSX (per-year + complete)
      - EN JSON + XLSX (per-year + complete)

Input:
    - LLM classifications: Dataset/IT/xlsx/ (Claude) + results/gpt/ (GPT)
    - Reviewer files: expert_review/*_completed.xlsx
    - Resolution file: results/expert_review/reviewer_discordances_RESOLUTION.xlsx

Output:
    Updated category field in all IT and EN dataset files (JSON + XLSX).

Requirements:
    - openpyxl>=3.1

Usage:
    python scripts/apply_expert_review.py

Author: ITAMed Dataset Team
==============================================================================
"""

import os
import sys
import json

import openpyxl

# ==============================================================================
# Configuration
# ==============================================================================

QC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(QC_DIR)

IT_JSON_DIR = os.path.join(REPO, "Dataset", "IT", "json")
IT_XLSX_DIR = os.path.join(REPO, "Dataset", "IT", "xlsx")
EN_JSON_DIR = os.path.join(REPO, "Dataset", "EN", "json")
EN_XLSX_DIR = os.path.join(REPO, "Dataset", "EN", "xlsx")
GPT_DIR = os.path.join(QC_DIR, "results", "gpt")
REVIEW_DIR = os.path.join(QC_DIR, "expert_review")
RESOLUTION_FILE = os.path.join(
    QC_DIR, "results", "expert_review",
    "reviewer_discordances_RESOLUTION.xlsx",
)

REV1_FILE = os.path.join(REVIEW_DIR, "discordances_to_review_REW1_EM_B_completed.xlsx")
REV2_FILE = os.path.join(REVIEW_DIR, "discordances_to_review_REW_2_ED_B_completed.xlsx")

YEARS = list(range(2017, 2026))

# IT → EN category translation
CAT_IT_TO_EN = {
    "Anestesia e Rianimazione": "Anesthesia and Intensive Care",
    "Cardiologia e Cardiochirurgia": "Cardiology and Cardiac Surgery",
    "Chirurgia Generale": "General Surgery",
    "Dermatologia e Venereologia": "Dermatology and Venereology",
    "Diagnostica per Immagini e Medicina Nucleare": "Diagnostic Imaging and Nuclear Medicine",
    "Ematologia": "Hematology",
    "Endocrinologia": "Endocrinology",
    "Farmacologia e Tossicologia": "Pharmacology and Toxicology",
    "Gastroenterologia": "Gastroenterology",
    "Genetica Medica": "Medical Genetics",
    "Ginecologia e Ostetricia": "Gynecology and Obstetrics",
    "Igiene, Epidemiologia e Statistica": "Hygiene, Epidemiology and Statistics",
    "Immunologia e Reumatologia": "Immunology and Rheumatology",
    "Malattie Infettive": "Infectious Diseases",
    "Medicina Interna": "Internal Medicine",
    "Medicina Legale": "Forensic Medicine",
    "Medicina del Lavoro": "Occupational Medicine",
    "Nefrologia": "Nephrology",
    "Neurologia e Neurochirurgia": "Neurology and Neurosurgery",
    "Nutrizione Clinica": "Clinical Nutrition",
    "Oftalmologia": "Ophthalmology",
    "Oncologia": "Oncology",
    "Ortopedia e Traumatologia": "Orthopedics and Traumatology",
    "Otorinolaringoiatria": "Otorhinolaryngology",
    "Pediatria": "Pediatrics",
    "Pneumologia e Chirurgia Toracica": "Pulmonology and Thoracic Surgery",
    "Psichiatria": "Psychiatry",
    "Urologia": "Urology",
}


def translate_category(it_cat: str) -> str:
    """Translate an Italian category string (possibly multi-label) to English."""
    parts = [p.strip() for p in it_cat.split(";") if p.strip()]
    en_parts = []
    for p in parts:
        en = CAT_IT_TO_EN.get(p)
        if not en:
            print(f"  WARNING: Unknown IT category '{p}', keeping as-is")
            en = p
        en_parts.append(en)
    return "; ".join(en_parts)


# ==============================================================================
# Data Loading
# ==============================================================================


def get_primary(cat_str):
    if not cat_str:
        return ""
    return cat_str.split(";")[0].strip()


def normalize_cat(cat_str):
    if not cat_str:
        return ""
    return "; ".join(p.strip() for p in cat_str.split(";") if p.strip())


def load_claude_categories() -> dict:
    """Load Claude categories from IT dataset (currently assigned)."""
    path = os.path.join(IT_JSON_DIR, "ITAMed_complete.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {item["question_code"]: normalize_cat(item.get("category", ""))
            for item in data}


def load_gpt_categories() -> dict:
    """Load GPT categories from classification results."""
    # Need to map (year, q_num) -> question_code first
    it_path = os.path.join(IT_JSON_DIR, "ITAMed_complete.json")
    with open(it_path, "r", encoding="utf-8") as f:
        it_data = json.load(f)
    key_to_code = {(item["year"], item["question_number"]): item["question_code"]
                   for item in it_data}

    gpt_cats = {}
    for year in YEARS:
        gpt_path = os.path.join(GPT_DIR, f"{year}_classifications_gpt.json")
        if not os.path.exists(gpt_path):
            continue
        with open(gpt_path, "r", encoding="utf-8") as f:
            classifications = json.load(f)
        for q_num_str, category in classifications.items():
            code = key_to_code.get((year, int(q_num_str)))
            if code:
                gpt_cats[code] = normalize_cat(category)
    return gpt_cats


def load_reviewer_category(path: str) -> dict:
    """Load final category from a completed reviewer file."""
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb.active
    cats = {}
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        code = row[2].value
        if not code:
            continue
        cat1 = str(row[7].value).strip() if row[7].value else ""
        cat2 = str(row[8].value).strip() if row[8].value else ""
        final = f"{cat1}; {cat2}" if cat2 else cat1
        cats[str(code)] = normalize_cat(final)
    wb.close()
    return cats


def load_resolution() -> dict:
    """Load resolved categories from the resolution file (col K)."""
    wb = openpyxl.load_workbook(RESOLUTION_FILE, read_only=True)
    ws = wb.active
    cats = {}
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        code = row[2].value
        resolution = row[10].value  # Column K
        if code and resolution:
            cats[str(code)] = normalize_cat(str(resolution).strip())
    wb.close()
    return cats


# ==============================================================================
# Build Final Category Mapping
# ==============================================================================


def build_final_categories() -> dict:
    """
    Build the complete final category mapping for all 1,260 questions.

    Priority:
      1. Resolution file (126 consensus-resolved discordances)
      2. Reviewer concordance (254 questions where R1 = R2)
      3. LLM concordance (880 questions where Claude = GPT)

    Returns:
        Dict mapping question_code -> final_it_category
    """
    claude_cats = load_claude_categories()
    gpt_cats = load_gpt_categories()
    rev1_cats = load_reviewer_category(REV1_FILE)
    rev2_cats = load_reviewer_category(REV2_FILE)
    resolution_cats = load_resolution()

    final = {}
    stats = {
        "llm_concordant": 0,
        "reviewer_concordant": 0,
        "resolved": 0,
        "unresolved": 0,
    }

    all_codes = set(claude_cats.keys())
    reviewed_codes = set(rev1_cats.keys())  # The 380 discordant questions

    for code in all_codes:
        claude = claude_cats.get(code, "")
        gpt = gpt_cats.get(code, "")

        if code in resolution_cats:
            # Priority 1: Consensus resolution
            final[code] = resolution_cats[code]
            stats["resolved"] += 1

        elif code in reviewed_codes:
            # This is a reviewed question
            r1 = rev1_cats.get(code, "")
            r2 = rev2_cats.get(code, "")
            if r1 == r2:
                # Priority 2: Reviewers agree
                final[code] = r1
                stats["reviewer_concordant"] += 1
            else:
                # Should have been in resolution file — fallback to R1
                print(f"  WARNING: {code} has reviewer disagreement but no resolution!")
                final[code] = r1
                stats["unresolved"] += 1

        else:
            # Not reviewed = LLMs agreed (exact match on full string)
            # Use Claude category (= GPT category)
            final[code] = claude
            stats["llm_concordant"] += 1

    return final, stats


# ==============================================================================
# Apply Categories
# ==============================================================================


def apply_to_json(json_dir, suffix, final_it, final_en):
    """Apply categories to JSON files (per-year + complete)."""
    cats = final_en if "_EN" in suffix else final_it
    updated = 0

    for year in YEARS:
        path = os.path.join(json_dir, f"ITAMed_{year}{suffix}.json")
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        changed = False
        for item in data:
            code = item["question_code"]
            if code in cats and item.get("category") != cats[code]:
                item["category"] = cats[code]
                changed = True
                updated += 1
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    # Complete
    path = os.path.join(json_dir, f"ITAMed_complete{suffix}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            code = item["question_code"]
            if code in cats and item.get("category") != cats[code]:
                item["category"] = cats[code]
                updated += 1
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return updated


def apply_to_xlsx(xlsx_dir, suffix, final_it, final_en):
    """Apply categories to XLSX files (per-year + complete)."""
    cats = final_en if "_EN" in suffix else final_it
    updated = 0
    CAT_COL = 11  # Column K (1-indexed), 0-indexed = 10

    for name in [f"ITAMed_{y}{suffix}.xlsx" for y in YEARS] + [f"ITAMed_complete{suffix}.xlsx"]:
        path = os.path.join(xlsx_dir, name)
        if not os.path.exists(path):
            continue
        wb = openpyxl.load_workbook(path)
        ws = wb.active
        changed = False
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            code = str(row[2].value) if row[2].value else ""
            if code in cats and row[10].value != cats[code]:
                row[10].value = cats[code]
                changed = True
                updated += 1
        if changed:
            wb.save(path)

    return updated


# ==============================================================================
# Main
# ==============================================================================


def main():
    print("=" * 70)
    print("ITAMed — Apply Final Category Assignments")
    print("=" * 70)

    # Build final mapping
    print("\n[1] Building final category mapping...")
    final_it, stats = build_final_categories()
    print(f"  LLM concordant:      {stats['llm_concordant']}")
    print(f"  Reviewer concordant: {stats['reviewer_concordant']}")
    print(f"  Consensus resolved:  {stats['resolved']}")
    if stats['unresolved'] > 0:
        print(f"  WARNING unresolved:  {stats['unresolved']}")
    print(f"  Total:               {len(final_it)}")

    # Translate to English
    print("\n[2] Translating categories to English...")
    final_en = {code: translate_category(cat) for code, cat in final_it.items()}
    print(f"  Translated {len(final_en)} categories")

    # Apply to IT files
    print("\n[3] Applying to IT dataset files...")
    n_it_json = apply_to_json(IT_JSON_DIR, "", final_it, final_en)
    n_it_xlsx = apply_to_xlsx(IT_XLSX_DIR, "", final_it, final_en)
    print(f"  IT JSON updates: {n_it_json}")
    print(f"  IT XLSX updates: {n_it_xlsx}")

    # Apply to EN files
    print("\n[4] Applying to EN dataset files...")
    n_en_json = apply_to_json(EN_JSON_DIR, "_EN", final_it, final_en)
    n_en_xlsx = apply_to_xlsx(EN_XLSX_DIR, "_EN", final_it, final_en)
    print(f"  EN JSON updates: {n_en_json}")
    print(f"  EN XLSX updates: {n_en_xlsx}")

    # Summary
    total = n_it_json + n_it_xlsx + n_en_json + n_en_xlsx
    print("\n" + "=" * 70)
    print("DONE — Final categories applied to all dataset files")
    print(f"  Total field updates: {total}")
    print("=" * 70)


if __name__ == "__main__":
    main()
