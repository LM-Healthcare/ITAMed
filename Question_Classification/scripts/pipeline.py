"""
==============================================================================
ITAMed — Classification Pipeline (End-to-End)
==============================================================================

Purpose:
    Reproducible end-to-end pipeline that reconstructs the final classified
    dataset from immutable intermediate artifacts. Each stage reads only
    from its declared inputs and produces deterministic outputs.

Pipeline stages:
    1. Load raw extracted dataset (no categories)
    2. Load immutable LLM classification outputs (Claude + GPT)
    3. Compute inter-annotator agreement (Claude vs GPT)
    4. Load independent expert reviewer decisions (R1 + R2)
    5. Compute inter-reviewer agreement
    6. Load consensus resolution for remaining discordances
    7. Build final category mapping (priority: resolution > reviewer > LLM)
    8. Apply categories to all dataset files (IT + EN, JSON + XLSX)
    9. Validate final dataset integrity

Immutable inputs (not modified by this pipeline):
    - Dataset/IT/json/ITAMed_{year}.json         (extracted text, no categories)
    - results/claude/{year}_classifications_claude.json  (raw Claude output)
    - results/gpt/{year}_classifications_gpt.json        (raw GPT output)
    - expert_review/discordances_to_review_REW1_EM_B_completed.xlsx (R1)
    - expert_review/discordances_to_review_REW_2_ED_B_completed.xlsx (R2)
    - results/expert_review/reviewer_discordances_RESOLUTION.xlsx (consensus)

Outputs:
    - results/agreement/         (LLM agreement analysis)
    - results/expert_review/     (reviewer agreement analysis)
    - Dataset/IT/ and Dataset/EN/ (final classified dataset)

Validation checks (pipeline halts on failure):
    - Total question count = 1,260
    - No duplicate or missing question_code values
    - Every LLM output covers all 1,260 questions
    - All categories belong to the 28-category taxonomy
    - No question has more than 2 categories
    - Every discordant question has two independent reviewer decisions
    - Every residual disagreement has a consensus resolution
    - IT↔EN category mapping is consistent
    - All referenced image files exist

Usage:
    python scripts/pipeline.py [--verify-only]

    --verify-only   Skip steps 3–8, only run validation on existing files.

Author: ITAMed Dataset Team
==============================================================================
"""

import os
import sys
import json
import argparse

import openpyxl

# ==============================================================================
# Configuration
# ==============================================================================

QC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(QC_DIR)

CLAUDE_DIR = os.path.join(QC_DIR, "results", "claude")
GPT_DIR = os.path.join(QC_DIR, "results", "gpt")
AGREEMENT_DIR = os.path.join(QC_DIR, "results", "agreement")
EXPERT_REVIEW_DIR = os.path.join(QC_DIR, "expert_review")
EXPERT_RESULTS_DIR = os.path.join(QC_DIR, "results", "expert_review")
RESOLUTION_FILE = os.path.join(EXPERT_RESULTS_DIR, "reviewer_discordances_RESOLUTION.xlsx")
REV1_FILE = os.path.join(EXPERT_REVIEW_DIR, "discordances_to_review_REW1_EM_B_completed.xlsx")
REV2_FILE = os.path.join(EXPERT_REVIEW_DIR, "discordances_to_review_REW_2_ED_B_completed.xlsx")

IT_JSON_DIR = os.path.join(REPO, "Dataset", "IT", "json")
IT_XLSX_DIR = os.path.join(REPO, "Dataset", "IT", "xlsx")
EN_JSON_DIR = os.path.join(REPO, "Dataset", "EN", "json")
EN_XLSX_DIR = os.path.join(REPO, "Dataset", "EN", "xlsx")
IMAGES_DIR = os.path.join(REPO, "Dataset", "images")

YEARS = list(range(2017, 2026))
EXPECTED_TOTAL = 1260
EXPECTED_PER_YEAR = 140

VALID_CATEGORIES = {
    "Anestesia e Rianimazione",
    "Cardiologia e Cardiochirurgia",
    "Chirurgia Generale",
    "Dermatologia e Venereologia",
    "Diagnostica per Immagini e Medicina Nucleare",
    "Ematologia",
    "Endocrinologia",
    "Farmacologia e Tossicologia",
    "Gastroenterologia",
    "Genetica Medica",
    "Ginecologia e Ostetricia",
    "Igiene, Epidemiologia e Statistica",
    "Immunologia e Reumatologia",
    "Malattie Infettive",
    "Medicina Interna",
    "Medicina Legale",
    "Medicina del Lavoro",
    "Nefrologia",
    "Neurologia e Neurochirurgia",
    "Nutrizione Clinica",
    "Oftalmologia",
    "Oncologia",
    "Ortopedia e Traumatologia",
    "Otorinolaringoiatria",
    "Pediatria",
    "Pneumologia e Chirurgia Toracica",
    "Psichiatria",
    "Urologia",
}

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


# ==============================================================================
# Utility
# ==============================================================================


def normalize_cat(cat_str):
    """Normalize a category string."""
    if not cat_str:
        return ""
    return "; ".join(p.strip() for p in str(cat_str).split(";") if p.strip())


def get_primary(cat_str):
    """Extract primary category."""
    if not cat_str:
        return ""
    return cat_str.split(";")[0].strip()


def fail(msg):
    """Print error and exit."""
    print(f"\n  ✗ FATAL: {msg}")
    sys.exit(1)


# ==============================================================================
# Stage 1: Load raw dataset metadata
# ==============================================================================


def load_dataset_metadata():
    """Load question metadata (codes, years, question_numbers) from IT JSON."""
    all_items = []
    for year in YEARS:
        path = os.path.join(IT_JSON_DIR, f"ITAMed_{year}.json")
        if not os.path.exists(path):
            fail(f"Missing dataset file: {path}")
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)
        all_items.extend(items)
    return all_items


# ==============================================================================
# Stage 2: Load raw LLM outputs
# ==============================================================================


def load_raw_llm_output(model_dir, suffix):
    """Load raw LLM classification output files."""
    output = {}
    for year in YEARS:
        path = os.path.join(model_dir, f"{year}_classifications_{suffix}.json")
        if not os.path.exists(path):
            fail(f"Missing {suffix} output: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for q_num_str, category in data.items():
            output[(year, int(q_num_str))] = normalize_cat(category)
    return output


# ==============================================================================
# Stage 4: Load reviewer decisions
# ==============================================================================


def load_reviewer(path):
    """Load a completed reviewer file. Returns dict: question_code -> category."""
    if not os.path.exists(path):
        fail(f"Missing reviewer file: {path}")
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


# ==============================================================================
# Stage 6: Load consensus resolution
# ==============================================================================


def load_resolution():
    """Load resolved categories from resolution file (column K)."""
    if not os.path.exists(RESOLUTION_FILE):
        fail(f"Missing resolution file: {RESOLUTION_FILE}")
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
# Stage 7: Build final category mapping
# ==============================================================================


def build_final_mapping(metadata, claude_raw, gpt_raw, rev1, rev2, resolution):
    """
    Build the definitive category for every question.

    Priority:
      1. Consensus resolution (126 questions)
      2. Reviewer concordance, i.e. R1 = R2 (254 questions)
      3. LLM concordance, i.e. Claude = GPT exact match (880 questions)
    """
    code_map = {(item["year"], item["question_number"]): item["question_code"]
                for item in metadata}
    reviewed_codes = set(rev1.keys())

    final = {}
    stats = {"llm_concordant": 0, "reviewer_concordant": 0,
             "resolved": 0, "unresolved": 0}

    for (year, q_num), code in code_map.items():
        claude_cat = claude_raw.get((year, q_num), "")
        gpt_cat = gpt_raw.get((year, q_num), "")

        if code in resolution:
            final[code] = resolution[code]
            stats["resolved"] += 1
        elif code in reviewed_codes:
            r1 = rev1.get(code, "")
            r2 = rev2.get(code, "")
            if r1 == r2:
                final[code] = r1
                stats["reviewer_concordant"] += 1
            else:
                fail(f"Question {code} has reviewer disagreement but no "
                     f"consensus resolution entry")
        else:
            # LLM concordant — verify they actually agree
            if claude_cat != gpt_cat:
                fail(f"Question {code} not in review set but Claude≠GPT: "
                     f"'{claude_cat}' vs '{gpt_cat}'")
            final[code] = claude_cat
            stats["llm_concordant"] += 1

    return final, stats


# ==============================================================================
# Stage 9: Validation
# ==============================================================================


def validate(metadata, claude_raw, gpt_raw, rev1, rev2, resolution, final_it):
    """Run all validation checks. Halts on first failure."""
    print("\n[Validation]")
    errors = 0

    # 1. Total question count
    if len(metadata) != EXPECTED_TOTAL:
        fail(f"Question count = {len(metadata)}, expected {EXPECTED_TOTAL}")
    print(f"  ✓ Question count: {len(metadata)}")

    # 2. No duplicate/missing question_codes
    codes = [item["question_code"] for item in metadata]
    if len(codes) != len(set(codes)):
        dupes = [c for c in codes if codes.count(c) > 1]
        fail(f"Duplicate question_codes: {set(dupes)}")
    if any(not c for c in codes):
        fail("Empty question_code found")
    print(f"  ✓ No duplicate/missing question_codes")

    # 3. LLM outputs cover all questions
    code_map = {(item["year"], item["question_number"]): item["question_code"]
                for item in metadata}
    missing_claude = [k for k in code_map if k not in claude_raw]
    missing_gpt = [k for k in code_map if k not in gpt_raw]
    if missing_claude:
        fail(f"Claude output missing {len(missing_claude)} questions: {missing_claude[:5]}")
    if missing_gpt:
        fail(f"GPT output missing {len(missing_gpt)} questions: {missing_gpt[:5]}")
    print(f"  ✓ Both LLM outputs cover all {EXPECTED_TOTAL} questions")

    # 4. All categories in taxonomy
    invalid = []
    for code, cat_str in final_it.items():
        parts = [p.strip() for p in cat_str.split(";") if p.strip()]
        for p in parts:
            if p not in VALID_CATEGORIES:
                invalid.append((code, p))
    if invalid:
        fail(f"Invalid categories ({len(invalid)}): {invalid[:5]}")
    print(f"  ✓ All final categories belong to 28-category taxonomy")

    # 5. No question has > 2 categories
    over_two = [(code, cat) for code, cat in final_it.items()
                if len([p for p in cat.split(";") if p.strip()]) > 2]
    if over_two:
        fail(f"Questions with >2 categories: {over_two[:5]}")
    print(f"  ✓ No question exceeds 2 categories")

    # 6. Every discordant question has two reviewer decisions
    reviewed_codes = set(rev1.keys()) | set(rev2.keys())
    rev1_only = set(rev1.keys()) - set(rev2.keys())
    rev2_only = set(rev2.keys()) - set(rev1.keys())
    if rev1_only or rev2_only:
        fail(f"Reviewer coverage mismatch: {len(rev1_only)} in R1 only, "
             f"{len(rev2_only)} in R2 only")
    print(f"  ✓ All {len(rev1)} reviewed questions have two reviewer decisions")

    # 7. Every residual disagreement has a consensus resolution
    residual = [code for code in rev1 if rev1[code] != rev2[code]]
    missing_resolution = [code for code in residual if code not in resolution]
    if missing_resolution:
        fail(f"Missing consensus resolution for {len(missing_resolution)} "
             f"disagreements: {missing_resolution[:5]}")
    print(f"  ✓ All {len(residual)} residual disagreements have consensus resolution")

    # 8. IT↔EN mapping consistent
    for year in YEARS:
        en_path = os.path.join(EN_JSON_DIR, f"ITAMed_{year}_EN.json")
        if not os.path.exists(en_path):
            continue
        with open(en_path, "r", encoding="utf-8") as f:
            en_data = json.load(f)
        for item in en_data:
            code = item["question_code"]
            it_cat = final_it.get(code, "")
            expected_en = "; ".join(
                CAT_IT_TO_EN.get(p.strip(), p.strip())
                for p in it_cat.split(";") if p.strip()
            )
            actual_en = item.get("category", "")
            if expected_en != actual_en:
                fail(f"IT↔EN mismatch for {code}: "
                     f"expected '{expected_en}', got '{actual_en}'")
    print(f"  ✓ IT↔EN category mapping consistent across all files")

    # 9. Referenced image files exist
    dataset_dir = os.path.join(REPO, "Dataset")
    missing_images = []
    for item in metadata:
        if item.get("has_image") and item.get("image_path"):
            img_path = os.path.join(dataset_dir, item["image_path"])
            if not os.path.exists(img_path):
                missing_images.append(item["question_code"])
    if missing_images:
        fail(f"Missing image files for {len(missing_images)} questions: "
             f"{missing_images[:5]}")
    n_images = sum(1 for item in metadata if item.get("has_image"))
    print(f"  ✓ All {n_images} referenced image files exist")

    # 10. Per-year counts
    for year in YEARS:
        year_count = sum(1 for item in metadata if item["year"] == year)
        if year_count != EXPECTED_PER_YEAR:
            fail(f"Year {year}: {year_count} questions (expected {EXPECTED_PER_YEAR})")
    print(f"  ✓ Each year has exactly {EXPECTED_PER_YEAR} questions")

    # 11. No empty categories in final mapping
    empty = [code for code, cat in final_it.items() if not cat.strip()]
    if empty:
        fail(f"{len(empty)} questions have empty final category: {empty[:5]}")
    print(f"  ✓ No empty categories in final mapping")

    # 12. question_type field present and valid for all questions
    valid_types = {"case-based", "knowledge-based"}
    missing_type = [item["question_code"] for item in metadata
                    if item.get("question_type") not in valid_types]
    if missing_type:
        fail(f"{len(missing_type)} questions have invalid/missing question_type: "
             f"{missing_type[:5]}")
    print(f"  ✓ All questions have valid question_type annotation")

    print(f"\n  All validation checks passed.")


# ==============================================================================
# Main
# ==============================================================================


def main():
    parser = argparse.ArgumentParser(description="ITAMed Classification Pipeline")
    parser.add_argument("--verify-only", action="store_true",
                        help="Only run validation on existing files")
    args = parser.parse_args()

    print("=" * 70)
    print("ITAMed — Classification Pipeline")
    print("=" * 70)

    # Stage 1: Load dataset metadata
    print("\n[1] Loading dataset metadata...")
    metadata = load_dataset_metadata()
    print(f"    {len(metadata)} questions loaded")
    code_map = {(item["year"], item["question_number"]): item["question_code"]
                for item in metadata}

    # Stage 2: Load raw LLM outputs
    print("\n[2] Loading raw LLM classification outputs...")
    claude_raw = load_raw_llm_output(CLAUDE_DIR, "claude")
    gpt_raw = load_raw_llm_output(GPT_DIR, "gpt")
    print(f"    Claude: {len(claude_raw)} classifications")
    print(f"    GPT:    {len(gpt_raw)} classifications")

    # Stage 3: LLM agreement (can be recomputed via compute_agreement.py)
    llm_agree = sum(1 for k in claude_raw if claude_raw[k] == gpt_raw.get(k))
    llm_discord = len(claude_raw) - llm_agree
    print(f"\n[3] LLM inter-annotator agreement:")
    print(f"    Exact-match concordant: {llm_agree}/{EXPECTED_TOTAL} "
          f"({llm_agree/EXPECTED_TOTAL:.1%})")
    print(f"    Discordant:             {llm_discord}/{EXPECTED_TOTAL}")

    # Stage 4: Load reviewer decisions
    print("\n[4] Loading expert reviewer decisions...")
    rev1 = load_reviewer(REV1_FILE)
    rev2 = load_reviewer(REV2_FILE)
    print(f"    Reviewer 1: {len(rev1)} decisions")
    print(f"    Reviewer 2: {len(rev2)} decisions")

    # Stage 5: Reviewer agreement
    rev_agree = sum(1 for code in rev1 if rev1[code] == rev2.get(code))
    rev_discord = len(rev1) - rev_agree
    print(f"\n[5] Expert inter-reviewer agreement:")
    print(f"    Concordant: {rev_agree}/{len(rev1)} "
          f"({rev_agree/len(rev1):.1%})")
    print(f"    Discordant: {rev_discord}/{len(rev1)}")

    # Stage 6: Load consensus resolution
    print("\n[6] Loading consensus resolution...")
    resolution = load_resolution()
    print(f"    Resolved: {len(resolution)} questions")

    # Stage 7: Build final mapping
    print("\n[7] Building final category mapping...")
    final_it, stats = build_final_mapping(
        metadata, claude_raw, gpt_raw, rev1, rev2, resolution
    )
    print(f"    LLM concordant:      {stats['llm_concordant']}")
    print(f"    Reviewer concordant: {stats['reviewer_concordant']}")
    print(f"    Consensus resolved:  {stats['resolved']}")
    print(f"    Total:               {len(final_it)}")

    if not args.verify_only:
        # Stage 8: Apply to dataset (delegated to apply_expert_review.py)
        print("\n[8] Applying final categories to dataset files...")
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from apply_expert_review import (
            translate_category, apply_to_json, apply_to_xlsx
        )
        final_en = {code: translate_category(cat) for code, cat in final_it.items()}

        n_it_json = apply_to_json(IT_JSON_DIR, "", final_it, final_en)
        n_it_xlsx = apply_to_xlsx(IT_XLSX_DIR, "", final_it, final_en)
        n_en_json = apply_to_json(EN_JSON_DIR, "_EN", final_it, final_en)
        n_en_xlsx = apply_to_xlsx(EN_XLSX_DIR, "_EN", final_it, final_en)
        print(f"    IT: {n_it_json} JSON + {n_it_xlsx} XLSX updates")
        print(f"    EN: {n_en_json} JSON + {n_en_xlsx} XLSX updates")

    # Stage 9: Validate
    validate(metadata, claude_raw, gpt_raw, rev1, rev2, resolution, final_it)

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
