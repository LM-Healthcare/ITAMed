"""
==============================================================================
ITAMed — Expert Reviewer Inter-Rater Agreement Analysis
==============================================================================

Purpose:
    Computes inter-rater agreement between two independent medical reviewers
    (Reviewer 1: Emiliano, Reviewer 2: Edoardo) who adjudicated the 380
    LLM-discordant questions.

    Produces:
      1. Overall agreement statistics (raw agreement, Cohen's κ)
      2. Per-category agreement (one-vs-all κ)
      3. Agreement by year
      4. Reviewer alignment with LLM annotators (Claude vs GPT)
      5. Confusion matrix between reviewers
      6. Discordance list for final resolution
      7. Professional markdown report for paper

Input:
    - Reviewer 1: expert_review/discordances_to_review_REW1_EM_B_completed.xlsx
    - Reviewer 2: expert_review/discordances_to_review_REW_2_ED_B_completed.xlsx

Output:
    - results/expert_review/expert_agreement_report.md
    - results/expert_review/reviewer_discordances.xlsx
    - results/expert_review/reviewer_discordances.json
    - results/expert_review/reviewer_confusion_matrix.xlsx

Requirements:
    - scikit-learn>=1.0
    - openpyxl
    - pandas>=2.0

Usage:
    python scripts/compute_reviewer_agreement.py

Author: ITAMed Dataset Team
==============================================================================
"""
import os
import json
from collections import Counter, defaultdict

import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from sklearn.metrics import cohen_kappa_score, confusion_matrix

# ==============================================================================
# Configuration
# ==============================================================================

QC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(QC_DIR)
REVIEW_DIR = os.path.join(QC_DIR, "expert_review")
OUTPUT_DIR = os.path.join(QC_DIR, "results", "expert_review")

REV1_FILE = os.path.join(REVIEW_DIR, "discordances_to_review_REW1_EM_B_completed.xlsx")
REV2_FILE = os.path.join(REVIEW_DIR, "discordances_to_review_REW_2_ED_B_completed.xlsx")

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


def get_primary(cat_str: str) -> str:
    """Extract primary category (first before semicolon)."""
    if not cat_str or pd.isna(cat_str):
        return ""
    return cat_str.split(";")[0].strip()


def normalize_category(cat_str: str) -> str:
    """Normalize a category string: trim whitespace, sort multi-labels."""
    if not cat_str or pd.isna(cat_str):
        return ""
    parts = [p.strip() for p in cat_str.split(";") if p.strip()]
    return "; ".join(parts)


def load_reviewer(path: str, label: str) -> pd.DataFrame:
    """
    Load a completed reviewer file.

    Columns:
        0: Anno, 1: N.Domanda, 2: Codice, 3: Domanda, 4: Risposta Corretta,
        5: Categoria Claude, 6: Categoria GPT,
        7: CATEGORIA FINALE 1, 8: CATEGORIA FINALE 2,
        9: CATEGORIA FINALE (formula — we compute manually)

    Returns DataFrame with columns:
        year, question_number, question_code, question, correct_answer,
        claude_cat, gpt_cat, rev_cat1, rev_cat2, rev_final
    """
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb.active
    records = []

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        code = row[2].value
        if not code:
            continue

        cat1 = str(row[7].value).strip() if row[7].value else ""
        cat2 = str(row[8].value).strip() if row[8].value else ""

        # Compute final (replicate the Excel formula)
        if cat2:
            final = f"{cat1}; {cat2}"
        else:
            final = cat1

        records.append({
            "year": row[0].value,
            "question_number": row[1].value,
            "question_code": str(code),
            "question": row[3].value,
            "correct_answer": row[4].value,
            "claude_cat": normalize_category(str(row[5].value) if row[5].value else ""),
            "gpt_cat": normalize_category(str(row[6].value) if row[6].value else ""),
            f"{label}_cat1": cat1,
            f"{label}_cat2": cat2,
            f"{label}_final": normalize_category(final),
            f"{label}_primary": get_primary(final),
        })

    wb.close()
    print(f"  Loaded {len(records)} questions from {label}")
    return pd.DataFrame(records)


# ==============================================================================
# Agreement Analysis
# ==============================================================================


def compute_agreement(df: pd.DataFrame) -> dict:
    """Compute all agreement metrics between the two reviewers."""

    r1_primary = df["rev1_primary"].tolist()
    r2_primary = df["rev2_primary"].tolist()
    r1_final = df["rev1_final"].tolist()
    r2_final = df["rev2_final"].tolist()

    n = len(df)

    # ----- Primary category agreement -----
    primary_agree = sum(1 for a, b in zip(r1_primary, r2_primary) if a == b)
    primary_rate = primary_agree / n if n else 0.0

    # ----- Exact-match agreement (full multi-label string) -----
    exact_agree = sum(1 for a, b in zip(r1_final, r2_final) if a == b)
    exact_rate = exact_agree / n if n else 0.0

    # ----- Set-based agreement (order-independent multi-label) -----
    def to_set(s):
        return frozenset(p.strip() for p in s.split(";") if p.strip())
    set_agree = sum(1 for a, b in zip(r1_final, r2_final) if to_set(a) == to_set(b))
    set_rate = set_agree / n if n else 0.0

    # ----- Cohen's Kappa (primary category) -----
    kappa_primary = cohen_kappa_score(r1_primary, r2_primary) if n > 1 else 0.0

    # ----- Per-category Kappa (one-vs-all) -----
    all_cats = sorted(set(r1_primary) | set(r2_primary))
    per_cat_kappa = {}
    for cat in all_cats:
        if not cat:
            continue
        r1_bin = [1 if c == cat else 0 for c in r1_primary]
        r2_bin = [1 if c == cat else 0 for c in r2_primary]
        if len(set(r1_bin)) < 2 and len(set(r2_bin)) < 2:
            per_cat_kappa[cat] = float("nan")
        else:
            try:
                per_cat_kappa[cat] = cohen_kappa_score(r1_bin, r2_bin)
            except Exception:
                per_cat_kappa[cat] = float("nan")

    # ----- Agreement by year -----
    by_year = {}
    for year in sorted(df["year"].unique()):
        mask = df["year"] == year
        yr_n = mask.sum()
        yr_primary_agree = sum(
            1 for a, b in zip(
                df.loc[mask, "rev1_primary"], df.loc[mask, "rev2_primary"]
            ) if a == b
        )
        yr_exact_agree = sum(
            1 for a, b in zip(
                df.loc[mask, "rev1_final"], df.loc[mask, "rev2_final"]
            ) if a == b
        )
        by_year[year] = {
            "n": yr_n,
            "primary_agree": yr_primary_agree,
            "primary_rate": yr_primary_agree / yr_n if yr_n else 0.0,
            "exact_agree": yr_exact_agree,
            "exact_rate": yr_exact_agree / yr_n if yr_n else 0.0,
        }

    # ----- LLM alignment analysis -----
    # For each reviewer, how often did they agree with Claude, GPT, or choose a third option?
    def llm_alignment(rev_primary_col, rev_final_col):
        chose_claude = 0
        chose_gpt = 0
        chose_third = 0
        chose_both = 0  # when Claude == GPT primary (shouldn't happen in discordances)
        for _, row in df.iterrows():
            rev_p = row[rev_primary_col]
            claude_p = get_primary(row["claude_cat"])
            gpt_p = get_primary(row["gpt_cat"])
            if rev_p == claude_p and rev_p == gpt_p:
                chose_both += 1
            elif rev_p == claude_p:
                chose_claude += 1
            elif rev_p == gpt_p:
                chose_gpt += 1
            else:
                chose_third += 1
        return {
            "chose_claude": chose_claude,
            "chose_gpt": chose_gpt,
            "chose_third": chose_third,
            "chose_both_agree": chose_both,
        }

    rev1_align = llm_alignment("rev1_primary", "rev1_final")
    rev2_align = llm_alignment("rev2_primary", "rev2_final")

    # ----- Discordance categorization -----
    # Among reviewer discordances, categorize:
    disc_mask = df["rev1_primary"] != df["rev2_primary"]
    n_disc = disc_mask.sum()

    # When reviewers disagree, who aligns with which LLM?
    disc_types = Counter()
    for _, row in df[disc_mask].iterrows():
        r1 = row["rev1_primary"]
        r2 = row["rev2_primary"]
        cp = get_primary(row["claude_cat"])
        gp = get_primary(row["gpt_cat"])
        if r1 == cp and r2 == gp:
            disc_types["R1=Claude, R2=GPT"] += 1
        elif r1 == gp and r2 == cp:
            disc_types["R1=GPT, R2=Claude"] += 1
        elif r1 == cp:
            disc_types["R1=Claude, R2=third"] += 1
        elif r1 == gp:
            disc_types["R1=GPT, R2=third"] += 1
        elif r2 == cp:
            disc_types["R2=Claude, R1=third"] += 1
        elif r2 == gp:
            disc_types["R2=GPT, R1=third"] += 1
        else:
            disc_types["Both=third (different)"] += 1

    return {
        "n": n,
        "primary_agree": primary_agree,
        "primary_rate": primary_rate,
        "exact_agree": exact_agree,
        "exact_rate": exact_rate,
        "set_agree": set_agree,
        "set_rate": set_rate,
        "kappa_primary": kappa_primary,
        "per_cat_kappa": per_cat_kappa,
        "by_year": by_year,
        "rev1_align": rev1_align,
        "rev2_align": rev2_align,
        "n_discordances": n_disc,
        "disc_types": dict(disc_types),
    }


# ==============================================================================
# Report Generation (Markdown)
# ==============================================================================


def generate_markdown_report(stats: dict, df: pd.DataFrame) -> str:
    """Generate a professional markdown report suitable for paper supplementary."""
    lines = []
    lines.append("# Expert Reviewer Agreement — Inter-Rater Analysis")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("Two independent medical specialists (Reviewer 1 and Reviewer 2) "
                 "adjudicated 380 questions for which the two LLM annotators "
                 "(Claude Opus 4.8 and GPT-5.5) produced discordant specialty "
                 "classifications. Each reviewer worked independently without "
                 "access to the other's decisions.")
    lines.append("")
    if stats['n'] < 380:
        lines.append(f"> **Note:** {380 - stats['n']} question(s) were excluded from "
                     f"analysis due to missing reviewer annotations. "
                     f"Analysis is based on {stats['n']} questions.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ------ Section 1: Overall Statistics ------
    lines.append("## 1. Overall Agreement Statistics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|:-------|------:|")
    lines.append(f"| Questions reviewed | {stats['n']} |")
    lines.append(f"| Primary-category agreement | "
                 f"{stats['primary_agree']}/{stats['n']} "
                 f"({stats['primary_rate']:.1%}) |")
    lines.append(f"| Exact-match agreement (full string) | "
                 f"{stats['exact_agree']}/{stats['n']} "
                 f"({stats['exact_rate']:.1%}) |")
    lines.append(f"| Set-based agreement (order-independent) | "
                 f"{stats['set_agree']}/{stats['n']} "
                 f"({stats['set_rate']:.1%}) |")
    lines.append(f"| **Cohen's κ (primary category)** | "
                 f"**κ = {stats['kappa_primary']:.4f}** |")
    lines.append(f"| Remaining discordances | "
                 f"{stats['n_discordances']} |")
    lines.append("")

    # Interpretation
    kappa = stats["kappa_primary"]
    if kappa >= 0.81:
        interp = "Almost perfect"
    elif kappa >= 0.61:
        interp = "Substantial"
    elif kappa >= 0.41:
        interp = "Moderate"
    elif kappa >= 0.21:
        interp = "Fair"
    elif kappa >= 0.0:
        interp = "Slight"
    else:
        interp = "Poor"

    lines.append("### Interpretation (Landis & Koch, 1977)")
    lines.append("")
    lines.append("| κ Range | Interpretation |")
    lines.append("|:--------|:---------------|")
    lines.append("| < 0.00 | Poor |")
    lines.append("| 0.00–0.20 | Slight |")
    lines.append("| 0.21–0.40 | Fair |")
    lines.append("| 0.41–0.60 | Moderate |")
    lines.append("| 0.61–0.80 | Substantial |")
    lines.append("| **0.81–1.00** | **Almost perfect** |")
    lines.append("")
    lines.append(f"The inter-reviewer **κ = {kappa:.4f}** indicates "
                 f"**{interp.lower()} agreement** between the two medical "
                 f"specialists.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ------ Section 2: Per-Category Kappa ------
    lines.append("## 2. Per-Category Agreement (one-vs-all κ)")
    lines.append("")
    lines.append("| Category | κ | Interpretation |")
    lines.append("|:---------|--:|:---------------|")

    sorted_cats = sorted(
        stats["per_cat_kappa"].items(),
        key=lambda x: -x[1] if not pd.isna(x[1]) else -2,
    )
    for cat, k in sorted_cats:
        if pd.isna(k):
            k_str = "N/A"
            interp_str = "—"
        else:
            k_str = f"{k:.4f}"
            if k >= 0.81:
                interp_str = "Almost perfect"
            elif k >= 0.61:
                interp_str = "Substantial"
            elif k >= 0.41:
                interp_str = "Moderate"
            elif k >= 0.21:
                interp_str = "Fair"
            elif k >= 0.0:
                interp_str = "Slight"
            else:
                interp_str = "Poor"
        lines.append(f"| {cat} | {k_str} | {interp_str} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # ------ Section 3: Agreement by Year ------
    lines.append("## 3. Agreement by Year")
    lines.append("")
    lines.append("| Year | N | Primary Agreement | % | Exact Agreement | % |")
    lines.append("|:-----|--:|------------------:|--:|----------------:|--:|")
    for year, ys in sorted(stats["by_year"].items()):
        lines.append(
            f"| {year} | {ys['n']} | "
            f"{ys['primary_agree']}/{ys['n']} | {ys['primary_rate']:.1%} | "
            f"{ys['exact_agree']}/{ys['n']} | {ys['exact_rate']:.1%} |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")

    # ------ Section 4: Reviewer–LLM Alignment ------
    lines.append("## 4. Reviewer–LLM Alignment")
    lines.append("")
    lines.append("For each question, we checked whether the reviewer's primary "
                 "category matched Claude's, GPT's, or neither (third option).")
    lines.append("")
    lines.append("| Metric | Reviewer 1 | Reviewer 2 |")
    lines.append("|:-------|:---------:|:---------:|")
    r1 = stats["rev1_align"]
    r2 = stats["rev2_align"]
    n = stats["n"]
    lines.append(f"| Agreed with Claude (only) | {r1['chose_claude']} ({r1['chose_claude']/n:.1%}) "
                 f"| {r2['chose_claude']} ({r2['chose_claude']/n:.1%}) |")
    lines.append(f"| Agreed with GPT (only) | {r1['chose_gpt']} ({r1['chose_gpt']/n:.1%}) "
                 f"| {r2['chose_gpt']} ({r2['chose_gpt']/n:.1%}) |")
    lines.append(f"| Chose third option | {r1['chose_third']} ({r1['chose_third']/n:.1%}) "
                 f"| {r2['chose_third']} ({r2['chose_third']/n:.1%}) |")
    if r1['chose_both_agree'] > 0 or r2['chose_both_agree'] > 0:
        lines.append(f"| Matched LLM consensus* | {r1['chose_both_agree']} ({r1['chose_both_agree']/n:.1%}) "
                     f"| {r2['chose_both_agree']} ({r2['chose_both_agree']/n:.1%}) |")
        lines.append("")
        lines.append("\\* *Questions where both LLMs had the same primary category "
                     "(discordance was only in secondary categories). The reviewer "
                     "confirmed that shared primary.*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ------ Section 5: Discordance Categorization ------
    lines.append("## 5. Reviewer Discordance Categorization")
    lines.append("")
    lines.append(f"Of the {stats['n']} reviewed questions, **{stats['n_discordances']}** "
                 f"({stats['n_discordances']/n:.1%}) have a primary-category disagreement "
                 f"between the two reviewers and require final resolution.")
    lines.append("")
    if stats["disc_types"]:
        lines.append("| Discordance pattern | Count |")
        lines.append("|:--------------------|------:|")
        for pattern, count in sorted(stats["disc_types"].items(), key=lambda x: -x[1]):
            lines.append(f"| {pattern} | {count} |")
        lines.append("")
    lines.append("---")
    lines.append("")

    # ------ Section 6: Summary ------
    total_disc_to_resolve = stats['n'] - stats['exact_agree']
    concordant_total = 880 + stats['exact_agree']
    lines.append("## 6. Summary — Full Classification Pipeline")
    lines.append("")
    lines.append("| Stage | Questions | Agreement | κ |")
    lines.append("|:------|:---------:|:---------:|:-:|")
    lines.append("| LLM annotation (Claude vs GPT) | 1,260 | 880/1,260 (69.8%) | 0.8950 |")
    lines.append(f"| Expert adjudication (R1 vs R2) | {stats['n']} | "
                 f"{stats['exact_agree']}/{stats['n']} exact ({stats['exact_rate']:.1%}) | "
                 f"{stats['kappa_primary']:.4f} |")
    lines.append(f"| **Fully resolved** | **{concordant_total}/1,260** | "
                 f"**{concordant_total/1260:.1%}** | — |")
    lines.append(f"| Remaining for resolution (any disagreement) | "
                 f"{total_disc_to_resolve} | — | — |")
    lines.append("")
    lines.append(f"Of the {total_disc_to_resolve} discordances to resolve:")
    lines.append(f"- **{stats['n_discordances']}** differ on the primary category")
    lines.append(f"- **{total_disc_to_resolve - stats['n_discordances']}** agree on primary "
                 f"but differ on the secondary category")
    lines.append("")

    return "\n".join(lines)


# ==============================================================================
# Output Files
# ==============================================================================


def save_discordances(df: pd.DataFrame, stats: dict):
    """Save ALL reviewer discordances (primary + secondary) to XLSX and JSON."""
    # Include ALL questions where full category doesn't match (not just primary)
    disc = df[df["rev1_final"] != df["rev2_final"]].copy()
    disc = disc.sort_values(["year", "question_number"]).reset_index(drop=True)

    # Select columns for output
    out_cols = [
        "year", "question_number", "question_code", "question", "correct_answer",
        "claude_cat", "gpt_cat",
        "rev1_final", "rev2_final",
        "rev1_primary", "rev2_primary",
    ]
    disc_out = disc[out_cols].copy()
    disc_out.columns = [
        "Year", "Q.Number", "Q.Code", "Question", "Correct Answer",
        "Claude Category", "GPT Category",
        "Reviewer 1 Final", "Reviewer 2 Final",
        "Reviewer 1 Primary", "Reviewer 2 Primary",
    ]

    # XLSX
    xlsx_path = os.path.join(OUTPUT_DIR, "reviewer_discordances.xlsx")
    disc_out.to_excel(xlsx_path, index=False)
    print(f"  Saved: {xlsx_path}")

    # JSON
    json_path = os.path.join(OUTPUT_DIR, "reviewer_discordances.json")
    records = disc_out.to_dict(orient="records")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {json_path}")

    return disc


def save_confusion_matrix(df: pd.DataFrame):
    """Save confusion matrix between the two reviewers."""
    r1 = df["rev1_primary"].tolist()
    r2 = df["rev2_primary"].tolist()

    all_cats = sorted(set(r1) | set(r2))
    cm = confusion_matrix(r1, r2, labels=all_cats)
    cm_df = pd.DataFrame(cm, index=all_cats, columns=all_cats)

    xlsx_path = os.path.join(OUTPUT_DIR, "reviewer_confusion_matrix.xlsx")
    cm_df.to_excel(xlsx_path)
    print(f"  Saved: {xlsx_path}")


# ==============================================================================
# Main
# ==============================================================================


def main():
    print("=" * 70)
    print("ITAMed — Expert Reviewer Agreement Analysis")
    print("=" * 70)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load reviewer data
    print("\nLoading reviewer files...")
    rev1_df = load_reviewer(REV1_FILE, "rev1")
    rev2_df = load_reviewer(REV2_FILE, "rev2")

    # Merge on question code
    merge_cols = ["year", "question_number", "question_code", "question",
                  "correct_answer", "claude_cat", "gpt_cat"]
    rev1_specific = ["rev1_cat1", "rev1_cat2", "rev1_final", "rev1_primary"]
    rev2_specific = ["rev2_cat1", "rev2_cat2", "rev2_final", "rev2_primary"]

    merged = pd.merge(
        rev1_df[merge_cols + rev1_specific],
        rev2_df[["question_code"] + rev2_specific],
        on="question_code",
        how="inner",
    )
    print(f"\nMerged: {len(merged)} questions with both reviews")

    # Check for missing categories
    missing_r1 = merged["rev1_primary"].eq("").sum()
    missing_r2 = merged["rev2_primary"].eq("").sum()
    if missing_r1 > 0 or missing_r2 > 0:
        print(f"\n  WARNING: Missing categories — R1: {missing_r1}, R2: {missing_r2}")
        missing_codes = merged[(merged["rev1_primary"] == "") | (merged["rev2_primary"] == "")]["question_code"].tolist()
        print(f"  Codes: {missing_codes}")
        print(f"  Excluding these from agreement computation.")
        merged = merged[(merged["rev1_primary"] != "") & (merged["rev2_primary"] != "")]
        print(f"  Remaining: {len(merged)} questions")

    # Compute agreement
    print("\nComputing agreement statistics...")
    stats = compute_agreement(merged)

    print(f"  Primary agreement:   {stats['primary_agree']}/{stats['n']} ({stats['primary_rate']:.1%})")
    print(f"  Exact match:         {stats['exact_agree']}/{stats['n']} ({stats['exact_rate']:.1%})")
    print(f"  Cohen's κ (primary): {stats['kappa_primary']:.4f}")
    print(f"  Discordances:        {stats['n_discordances']}")

    # Save outputs
    print("\nSaving outputs...")
    save_discordances(merged, stats)
    save_confusion_matrix(merged)

    # Generate markdown report
    print("\nGenerating markdown report...")
    report = generate_markdown_report(stats, merged)
    report_path = os.path.join(OUTPUT_DIR, "expert_agreement_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  Saved: {report_path}")

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
