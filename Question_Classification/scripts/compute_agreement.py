"""
==============================================================================
ITAMed — Inter-Rater Agreement Analysis
==============================================================================

Purpose:
    Computes inter-rater agreement between two independent LLM-based
    annotators (Claude Opus 4.8 and GPT-5.5) for medical specialty
    classification of SSM exam questions.

    Produces:
      1. Contingency table (Claude × GPT categories)
      2. Cohen's Kappa (overall and per-category)
      3. Full discordance report for expert adjudication

    For multi-label questions (up to 2 categories), agreement is evaluated
    on the PRIMARY category (first listed). A secondary analysis reports
    exact-match agreement on the full category string.

Input:
    - Claude classifications: Question_Classification/results/claude/{year}_classifications_claude.json
    - GPT classifications: Question_Classification/results/gpt/{year}_classifications_gpt.json

Output:
    All outputs are saved to Question_Classification/results/agreement/:
      - contingency_table.xlsx     — Full N×N contingency matrix
      - agreement_report.txt       — Summary statistics and Kappa values
      - discordances.xlsx          — Questions with disagreeing classifications
      - discordances.json          — Same data in JSON for programmatic use

Requirements:
    - scikit-learn>=1.0 (Cohen's Kappa, confusion matrix)
    - openpyxl (XLSX read/write)
    - pandas>=2.0 (data manipulation)

Usage:
    python inter_rater_agreement.py

Author: ITAMed Dataset Team
==============================================================================
"""

import os
import json
from collections import Counter

import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix

# ==============================================================================
# Configuration
# ==============================================================================

QC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(QC_DIR)
CLAUDE_DIR = os.path.join(QC_DIR, "results", "claude")
GPT_DIR = os.path.join(QC_DIR, "results", "gpt")
OUTPUT_DIR = os.path.join(QC_DIR, "results", "agreement")
IT_JSON_DIR = os.path.join(REPO_ROOT, "Dataset", "IT", "json")

YEARS = list(range(2017, 2026))

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


# ==============================================================================
# Data Loading
# ==============================================================================


def get_primary_category(cat_str: str) -> str:
    """Extract the primary (first) category from a multi-label string."""
    if not cat_str or cat_str == "NON CLASSIFICATA":
        return "NON CLASSIFICATA"
    return cat_str.split(";")[0].strip()


def load_claude_classifications() -> pd.DataFrame:
    """
    Load Claude classifications from raw output JSON files.

    Reads from results/claude/{year}_classifications_claude.json — the
    immutable raw output produced by classify_claude.py.

    Returns:
        DataFrame with columns: year, question_number, question_code,
        question, claude_category (full), claude_primary (first category).
    """
    # Load question metadata (codes, text) from dataset for context
    it_path = os.path.join(IT_JSON_DIR, "ITAMed_complete.json")
    with open(it_path, "r", encoding="utf-8") as f:
        it_data = json.load(f)
    meta = {(item["year"], item["question_number"]): item for item in it_data}

    records = []
    for year in YEARS:
        json_path = os.path.join(CLAUDE_DIR, f"{year}_classifications_claude.json")
        if not os.path.exists(json_path):
            print(f"  WARNING: Claude file not found: {json_path}")
            continue

        with open(json_path, "r", encoding="utf-8") as f:
            classifications = json.load(f)

        for q_num_str, category in classifications.items():
            q_num = int(q_num_str)
            item_meta = meta.get((year, q_num), {})
            records.append({
                "year": year,
                "question_number": q_num,
                "question_code": item_meta.get("question_code", ""),
                "question": item_meta.get("question", ""),
                "answer_a": item_meta.get("answer_a", ""),
                "answer_b": item_meta.get("answer_b", ""),
                "answer_c": item_meta.get("answer_c", ""),
                "answer_d": item_meta.get("answer_d", ""),
                "answer_e": item_meta.get("answer_e", ""),
                "claude_category": category,
            })

    df = pd.DataFrame(records)
    df["claude_primary"] = df["claude_category"].apply(get_primary_category)
    return df


def load_gpt_classifications() -> pd.DataFrame:
    """
    Load GPT-5.5 classifications from JSON result files.

    Returns:
        DataFrame with columns: year, question_number, gpt_category (full),
        gpt_primary (first category).
    """
    records = []
    for year in YEARS:
        json_path = os.path.join(GPT_DIR, f"{year}_classifications_gpt.json")
        if not os.path.exists(json_path):
            print(f"  WARNING: GPT file not found: {json_path}")
            continue

        with open(json_path, "r", encoding="utf-8") as f:
            classifications = json.load(f)

        for q_num_str, category in classifications.items():
            records.append({
                "year": year,
                "question_number": int(q_num_str),
                "gpt_category": category,
            })

    df = pd.DataFrame(records)
    df["gpt_primary"] = df["gpt_category"].apply(get_primary_category)
    return df


# ==============================================================================
# Agreement Analysis
# ==============================================================================


def compute_contingency_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a contingency table (Claude rows × GPT columns) for primary
    categories.

    Args:
        df: Merged DataFrame with 'claude_primary' and 'gpt_primary' columns.

    Returns:
        Contingency table as a pandas DataFrame.
    """
    # Collect all unique categories that appear in either annotator
    all_cats = sorted(
        set(df["claude_primary"].unique()) | set(df["gpt_primary"].unique())
    )

    ct = pd.crosstab(
        df["claude_primary"],
        df["gpt_primary"],
        margins=True,
        margins_name="Total",
    )

    # Reindex to ensure all categories appear even if count is 0
    all_cats_with_total = [c for c in all_cats if c != "Total"] + ["Total"]
    ct = ct.reindex(index=all_cats_with_total, columns=all_cats_with_total, fill_value=0)

    return ct


def compute_kappa(df: pd.DataFrame) -> dict:
    """
    Compute Cohen's Kappa and related agreement statistics.

    Args:
        df: Merged DataFrame with 'claude_primary' and 'gpt_primary' columns.

    Returns:
        Dictionary with overall kappa, per-category kappa, and agreement rates.
    """
    claude = df["claude_primary"].tolist()
    gpt = df["gpt_primary"].tolist()

    # Overall Cohen's Kappa
    kappa = cohen_kappa_score(claude, gpt)

    # Raw agreement
    agree = sum(1 for c, g in zip(claude, gpt) if c == g)
    raw_agreement = agree / len(claude) if claude else 0.0

    # Exact-match agreement (full category string, not just primary)
    exact_agree = sum(
        1 for _, row in df.iterrows()
        if row["claude_category"] == row["gpt_category"]
    )
    exact_agreement = exact_agree / len(df) if len(df) > 0 else 0.0

    # Per-category Kappa (one-vs-all binary kappa for each category)
    per_cat_kappa = {}
    for cat in sorted(set(claude) | set(gpt)):
        claude_bin = [1 if c == cat else 0 for c in claude]
        gpt_bin = [1 if g == cat else 0 for g in gpt]
        # Skip if one annotator never used this category
        if len(set(claude_bin)) < 2 and len(set(gpt_bin)) < 2:
            per_cat_kappa[cat] = float("nan")
        else:
            try:
                per_cat_kappa[cat] = cohen_kappa_score(claude_bin, gpt_bin)
            except Exception:
                per_cat_kappa[cat] = float("nan")

    return {
        "overall_kappa": kappa,
        "raw_agreement": raw_agreement,
        "exact_agreement": exact_agreement,
        "n_total": len(claude),
        "n_agree_primary": agree,
        "n_agree_exact": exact_agree,
        "per_category_kappa": per_cat_kappa,
    }


def extract_discordances(df: pd.DataFrame) -> tuple:
    """
    Extract discordant questions at two levels:
      1. Primary-category disagreements (Claude vs GPT primary ≠)
      2. Exact-match disagreements (full category string ≠)

    The exact-match set (larger) is what was sent for expert adjudication,
    as it includes questions where models agree on primary but disagree on
    secondary categories.

    Args:
        df: Merged DataFrame with both annotations.

    Returns:
        Tuple of (primary_discordances_df, exact_match_discordances_df).
    """
    cols = [
        "year", "question_number", "question_code", "question",
        "answer_a", "answer_b", "answer_c", "answer_d", "answer_e",
        "claude_category", "gpt_category",
        "claude_primary", "gpt_primary",
    ]
    available_cols = [c for c in cols if c in df.columns]

    # Primary disagreements
    primary_disc = df[df["claude_primary"] != df["gpt_primary"]].copy()
    primary_disc = primary_disc.sort_values(["year", "question_number"]).reset_index(drop=True)

    # Exact-match disagreements (full string, sent for expert review)
    exact_disc = df[df["claude_category"] != df["gpt_category"]].copy()
    exact_disc = exact_disc.sort_values(["year", "question_number"]).reset_index(drop=True)

    return primary_disc[available_cols], exact_disc[available_cols]


# ==============================================================================
# Report Generation
# ==============================================================================


def generate_report(stats: dict, ct: pd.DataFrame, disc: pd.DataFrame) -> str:
    """Generate a human-readable agreement report."""
    lines = [
        "=" * 70,
        "ITAMed — Inter-Rater Agreement Report",
        "Annotators: Claude Opus 4.8 vs GPT-5.5",
        "=" * 70,
        "",
        "OVERALL STATISTICS",
        "-" * 40,
        f"  Total questions:             {stats['n_total']}",
        f"  Primary-category agreement:  {stats['n_agree_primary']} / {stats['n_total']}"
        f"  ({stats['raw_agreement']:.1%})",
        f"  Exact-match agreement:       {stats['n_agree_exact']} / {stats['n_total']}"
        f"  ({stats['exact_agreement']:.1%})",
        f"  Cohen's Kappa (primary):     {stats['overall_kappa']:.4f}",
        "",
        "  Interpretation (Landis & Koch, 1977):",
        "    < 0.00  Poor",
        "    0.00–0.20  Slight",
        "    0.21–0.40  Fair",
        "    0.41–0.60  Moderate",
        "    0.61–0.80  Substantial",
        "    0.81–1.00  Almost perfect",
        "",
        f"  Primary discordances:        {stats['n_total'] - stats['n_agree_primary']}",
        f"  Exact-match discordances:    {stats['n_total'] - stats['n_agree_exact']}",
        "",
        "",
        "PER-CATEGORY KAPPA (one-vs-all)",
        "-" * 40,
    ]

    for cat, k in sorted(
        stats["per_category_kappa"].items(), key=lambda x: -x[1] if not pd.isna(x[1]) else -2
    ):
        k_str = f"{k:.4f}" if not pd.isna(k) else "N/A"
        lines.append(f"  {cat:<50s}  κ = {k_str}")

    lines += [
        "",
        "",
        "DISCORDANCE SUMMARY BY YEAR",
        "-" * 40,
    ]

    if not disc.empty:
        for year in sorted(disc["year"].unique()):
            year_disc = disc[disc["year"] == year]
            lines.append(f"  {year}: {len(year_disc)} discordances")
    else:
        lines.append("  No discordances found.")

    lines += [
        "",
        "=" * 70,
        "Files saved in: Question_Classification/results/agreement/",
        "  - contingency_table.xlsx",
        "  - discordances.xlsx",
        "  - discordances.json",
        "  - agreement_report.txt",
        "=" * 70,
    ]

    return "\n".join(lines)


# ==============================================================================
# Main Execution
# ==============================================================================


def main():
    """
    Main entry point. Loads both annotator classifications, computes
    inter-rater agreement statistics, and exports results.
    """
    print("=" * 70)
    print("ITAMed — Inter-Rater Agreement Analysis")
    print("=" * 70)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- Load data ---
    print("\nLoading Claude classifications...")
    claude_df = load_claude_classifications()
    print(f"  Loaded {len(claude_df)} Claude annotations")

    print("Loading GPT-5.5 classifications...")
    gpt_df = load_gpt_classifications()
    print(f"  Loaded {len(gpt_df)} GPT annotations")

    if gpt_df.empty:
        print("\nERROR: No GPT classifications found.")
        print("  Run classify_gpt.py first.")
        return

    # --- Merge ---
    merged = pd.merge(
        claude_df,
        gpt_df,
        on=["year", "question_number"],
        how="inner",
    )
    print(f"\nMerged: {len(merged)} questions with both annotations")

    if len(merged) == 0:
        print("ERROR: No matching questions between Claude and GPT results.")
        return

    if len(merged) < len(claude_df):
        print(f"  WARNING: {len(claude_df) - len(merged)} Claude questions "
              f"have no GPT match")

    # --- Contingency table ---
    print("\nComputing contingency table...")
    ct = compute_contingency_table(merged)
    ct_path = os.path.join(OUTPUT_DIR, "contingency_table.xlsx")
    ct.to_excel(ct_path)
    print(f"  Saved: {ct_path}")

    # --- Cohen's Kappa ---
    print("Computing Cohen's Kappa...")
    stats = compute_kappa(merged)
    print(f"  Overall Kappa:            {stats['overall_kappa']:.4f}")
    print(f"  Primary agreement rate:   {stats['raw_agreement']:.1%}")
    print(f"  Exact-match rate:         {stats['exact_agreement']:.1%}")

    # --- Discordances ---
    print("\nExtracting discordances...")
    primary_disc, exact_disc = extract_discordances(merged)
    print(f"  Primary-category discordances: {len(primary_disc)}")
    print(f"  Exact-match discordances:      {len(exact_disc)} (sent for expert review)")

    # Save exact-match discordances (the set sent for expert adjudication)
    disc_xlsx_path = os.path.join(OUTPUT_DIR, "discordances.xlsx")
    exact_disc.to_excel(disc_xlsx_path, index=False)
    print(f"  Saved: {disc_xlsx_path}")

    disc_json_path = os.path.join(OUTPUT_DIR, "discordances.json")
    disc_records = exact_disc.to_dict(orient="records")
    with open(disc_json_path, "w", encoding="utf-8") as f:
        json.dump(disc_records, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {disc_json_path}")

    # --- Report ---
    report = generate_report(stats, ct, exact_disc)
    report_path = os.path.join(OUTPUT_DIR, "agreement_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n  Report: {report_path}")

    # Print report to console
    print("\n")
    print(report)


if __name__ == "__main__":
    main()
