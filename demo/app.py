"""
ITAMed Explorer — Interactive Demo for the ITAMed Dataset
HuggingFace Spaces (Gradio)

Allows users to browse, filter, and download subsets of the ITAMed dataset.
"""

import json
import os
import gradio as gr
import pandas as pd
from pathlib import Path

# ==============================================================================
# Data Loading
# ==============================================================================

# Try loading from HuggingFace datasets first, fall back to local JSON
try:
    from datasets import load_dataset
    _ds_it = load_dataset("Filo-White/ITAMed", "it", split="train")
    _ds_en = load_dataset("Filo-White/ITAMed", "en", split="train")
    DF_IT = _ds_it.to_pandas()
    DF_EN = _ds_en.to_pandas()
except Exception:
    # Fallback: load from local JSON files
    DATA_DIR = Path(__file__).parent / "data"
    with open(DATA_DIR / "ITAMed_IT.json", "r", encoding="utf-8") as f:
        DF_IT = pd.DataFrame(json.load(f))
    with open(DATA_DIR / "ITAMed_EN.json", "r", encoding="utf-8") as f:
        DF_EN = pd.DataFrame(json.load(f))

YEARS = sorted(DF_IT["year"].unique().tolist())

CATEGORIES_IT = sorted(set(
    cat.strip()
    for cats in DF_IT["category"].dropna()
    for cat in cats.split(";")
))

CATEGORIES_EN = sorted(set(
    cat.strip()
    for cats in DF_EN["category"].dropna()
    for cat in cats.split(";")
))

IMAGE_CATEGORIES = sorted(set(
    DF_IT.loc[DF_IT["image_category"].notna() & (DF_IT["image_category"] != ""), "image_category"]
))

# ==============================================================================
# Filter Logic
# ==============================================================================

def filter_dataset(
    language: str,
    years: list,
    categories: list,
    image_filter: str,
    image_categories: list,
    search_text: str,
):
    """Apply filters and return a DataFrame subset."""
    df = DF_EN.copy() if language == "English" else DF_IT.copy()

    # Year filter
    if years:
        df = df[df["year"].isin([int(y) for y in years])]

    # Category filter
    if categories:
        mask = df["category"].apply(
            lambda c: any(cat.strip() in categories for cat in str(c).split(";"))
            if pd.notna(c) else False
        )
        df = df[mask]

    # Image filter
    if image_filter == "With image only":
        df = df[df["has_image"] == True]
    elif image_filter == "Without image only":
        df = df[df["has_image"] == False]

    # Image category filter
    if image_categories:
        df = df[df["image_category"].isin(image_categories)]

    # Text search
    if search_text and search_text.strip():
        query = search_text.strip().lower()
        df = df[df["question"].str.lower().str.contains(query, na=False)]

    return df


def apply_filters(language, years, categories, image_filter, image_categories, search_text):
    """Main filter function connected to the UI."""
    df = filter_dataset(language, years, categories, image_filter, image_categories, search_text)

    # Select display columns
    if language == "English":
        display_cols = ["year", "question_number", "question_code", "question",
                        "answer_a", "correct_answer", "category", "has_image", "image_category"]
    else:
        display_cols = ["year", "question_number", "question_code", "question",
                        "answer_a", "correct_answer", "category", "has_image", "image_category"]

    display_df = df[display_cols].reset_index(drop=True)
    summary = f"**{len(display_df)}** questions found"

    return summary, display_df


def get_question_detail(language, years, categories, image_filter, image_categories, search_text, evt: gr.SelectData):
    """Show full details when a row is clicked."""
    df = filter_dataset(language, years, categories, image_filter, image_categories, search_text)
    df = df.reset_index(drop=True)

    if evt.index[0] >= len(df):
        return "No question selected."

    row = df.iloc[evt.index[0]]

    detail = f"""### Question {row['question_number']} ({row['year']})
**Code:** `{row['question_code']}`
**Category:** {row['category']}
**Image:** {'Yes — ' + str(row['image_category']) if row['has_image'] else 'No'}

---

**{row['question']}**

- **A)** {row['answer_a']} ✅
- **B)** {row['answer_b']}
- **C)** {row['answer_c']}
- **D)** {row['answer_d']}
- **E)** {row['answer_e']}
"""
    return detail


def export_filtered(language, years, categories, image_filter, image_categories, search_text, fmt):
    """Export filtered results to file."""
    df = filter_dataset(language, years, categories, image_filter, image_categories, search_text)

    tmp_dir = Path("/tmp/itamed_exports")
    tmp_dir.mkdir(exist_ok=True)

    if fmt == "JSON":
        path = tmp_dir / "ITAMed_filtered.json"
        df.to_json(path, orient="records", force_ascii=False, indent=2)
    elif fmt == "CSV":
        path = tmp_dir / "ITAMed_filtered.csv"
        df.to_csv(path, index=False, encoding="utf-8")
    else:
        path = tmp_dir / "ITAMed_filtered.xlsx"
        df.to_excel(path, index=False, engine="openpyxl")

    return str(path)


def update_categories(language):
    """Update category dropdown based on language selection."""
    if language == "English":
        return gr.update(choices=CATEGORIES_EN, value=[])
    else:
        return gr.update(choices=CATEGORIES_IT, value=[])


# ==============================================================================
# Statistics Tab
# ==============================================================================

def compute_stats():
    """Generate dataset statistics as markdown."""
    total = len(DF_IT)
    with_img = DF_IT["has_image"].sum()

    # Category distribution
    cat_counts = {}
    for cats in DF_EN["category"].dropna():
        for cat in cats.split(";"):
            cat = cat.strip()
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

    cat_sorted = sorted(cat_counts.items(), key=lambda x: -x[1])

    # Year distribution
    year_counts = DF_IT.groupby("year").size()

    # Image per year
    img_per_year = DF_IT[DF_IT["has_image"]].groupby("year").size()

    stats_md = f"""## Dataset Overview

| Metric | Value |
|:-------|------:|
| Total questions | {total:,} |
| Years | {YEARS[0]}–{YEARS[-1]} |
| Questions per year | 140 |
| With images | {with_img} ({with_img/total*100:.1f}%) |
| Medical specialties | {len(cat_counts)} |
| Image categories | {len(IMAGE_CATEGORIES)} |

## Top 10 Medical Specialties

| # | Category | Count | % |
|:-:|:---------|------:|--:|
"""
    for i, (cat, count) in enumerate(cat_sorted[:10], 1):
        stats_md += f"| {i} | {cat} | {count} | {count/total*100:.1f}% |\n"

    stats_md += f"""
## Questions with Images per Year

| Year | Total | With Image |
|:----:|------:|-----------:|
"""
    for year in YEARS:
        img_count = img_per_year.get(year, 0)
        stats_md += f"| {year} | {year_counts[year]} | {img_count} |\n"

    return stats_md


# ==============================================================================
# Gradio Interface
# ==============================================================================

THEME = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate",
)

with gr.Blocks(theme=THEME, title="ITAMed Explorer") as demo:
    gr.Markdown(
        """
        # 🏥 ITAMed Explorer
        **Interactive browser for the Italian Medical Specialization Exam Dataset (2017–2025)**

        Browse, filter, and download subsets of 1,260 bilingual medical exam questions.

        <a href="https://github.com/Filo-White/ITAMed">GitHub</a> •
        <a href="https://huggingface.co/datasets/Filo-White/ITAMed">Dataset</a> •
        <a href="#">Paper</a>
        """
    )

    with gr.Tabs():
        # --- Tab 1: Explorer ---
        with gr.TabItem("Explorer"):
            with gr.Row():
                with gr.Column(scale=1):
                    language = gr.Radio(
                        choices=["Italian", "English"],
                        value="English",
                        label="Language",
                    )
                    years = gr.CheckboxGroup(
                        choices=[str(y) for y in YEARS],
                        value=[],
                        label="Years (leave empty for all)",
                    )
                    categories = gr.Dropdown(
                        choices=CATEGORIES_EN,
                        multiselect=True,
                        label="Medical Specialties",
                    )
                    image_filter = gr.Radio(
                        choices=["All", "With image only", "Without image only"],
                        value="All",
                        label="Image Filter",
                    )
                    image_cats = gr.Dropdown(
                        choices=IMAGE_CATEGORIES,
                        multiselect=True,
                        label="Image Categories",
                    )
                    search_box = gr.Textbox(
                        label="Search in question text",
                        placeholder="e.g. myocardial infarction",
                    )
                    filter_btn = gr.Button("🔍 Apply Filters", variant="primary")

                    gr.Markdown("### Export")
                    export_fmt = gr.Radio(
                        choices=["JSON", "CSV", "XLSX"],
                        value="JSON",
                        label="Format",
                    )
                    export_btn = gr.Button("📥 Download Filtered Subset")
                    export_file = gr.File(label="Download")

                with gr.Column(scale=3):
                    result_summary = gr.Markdown("Click **Apply Filters** to browse the dataset.")
                    result_table = gr.Dataframe(
                        headers=["year", "question_number", "question_code", "question",
                                 "answer_a", "correct_answer", "category", "has_image", "image_category"],
                        interactive=False,
                        wrap=True,
                    )
                    question_detail = gr.Markdown("*Click a row to see full question details.*")

            # Event bindings
            language.change(update_categories, inputs=[language], outputs=[categories])

            filter_inputs = [language, years, categories, image_filter, image_cats, search_box]

            filter_btn.click(
                apply_filters,
                inputs=filter_inputs,
                outputs=[result_summary, result_table],
            )

            result_table.select(
                get_question_detail,
                inputs=filter_inputs,
                outputs=[question_detail],
            )

            export_btn.click(
                export_filtered,
                inputs=filter_inputs + [export_fmt],
                outputs=[export_file],
            )

        # --- Tab 2: Statistics ---
        with gr.TabItem("Statistics"):
            stats_md = gr.Markdown(compute_stats())

        # --- Tab 3: About ---
        with gr.TabItem("About"):
            gr.Markdown(
                """
                ## About ITAMed

                **ITAMed** is a comprehensive bilingual dataset of 1,260 multiple-choice questions
                from the Italian National Medical Specialization Entrance Exam (SSM), covering
                all 9 editions from 2017 to 2025.

                ### Construction Pipeline

                1. **PDF Extraction** — Automated text extraction from official exam PDFs
                2. **Specialty Classification** — LLM-based classification into 28 medical categories
                3. **Image Annotation** — Manual identification and categorization of image-bearing questions
                4. **Translation** — LLM-based medical translation (Italian → English)
                5. **Quality Control** — Manual review and validation

                ### Links

                - 📄 **Paper**: [Scientific Data — submitted]
                - 💻 **GitHub**: [Filo-White/ITAMed](https://github.com/Filo-White/ITAMed)
                - 📊 **Related benchmark**: [LLM-EVAL-Education](https://github.com/Filo-White/LLM-EVAL-Education)

                ### Citation

                ```bibtex
                @article{itamed2025,
                  title   = {ITAMed: A Comprehensive Bilingual Dataset of Italian Medical
                             Specialization Exam Questions (2017--2025)},
                  author  = {[Authors]},
                  journal = {Scientific Data},
                  year    = {2025},
                  doi     = {[to be assigned]}
                }
                ```
                """
            )


if __name__ == "__main__":
    demo.launch()
