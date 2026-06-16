"""
ITAMed Explorer — Interactive Dataset Browser
HuggingFace Spaces Demo

Browse, filter, and download subsets of the ITAMed dataset:
1,260 bilingual (IT/EN) medical exam questions from the Italian SSM (2017-2025).
"""

import json
import os
import tempfile

import gradio as gr
import pandas as pd
from pathlib import Path

# ==============================================================================
# Data Loading
# ==============================================================================

DATA_DIR = Path(__file__).parent / "data"

with open(DATA_DIR / "ITAMed_IT.json", "r", encoding="utf-8") as f:
    DF_IT = pd.DataFrame(json.load(f))
with open(DATA_DIR / "ITAMed_EN.json", "r", encoding="utf-8") as f:
    DF_EN = pd.DataFrame(json.load(f))

YEARS = sorted(DF_IT["year"].unique().tolist())

CATEGORIES_IT = sorted(set(
    cat.strip()
    for cats in DF_IT["category"].dropna()
    for cat in str(cats).split(";")
    if cat.strip()
))

CATEGORIES_EN = sorted(set(
    cat.strip()
    for cats in DF_EN["category"].dropna()
    for cat in str(cats).split(";")
    if cat.strip()
))

IMAGE_CATEGORIES = sorted(
    DF_IT.loc[
        DF_IT["image_category"].notna() & (DF_IT["image_category"] != ""),
        "image_category"
    ].unique().tolist()
)

# ==============================================================================
# Filter Logic
# ==============================================================================


def filter_dataset(language, years, categories, image_filter, image_categories, search_text):
    """Apply all filters and return a DataFrame subset."""
    df = DF_EN.copy() if language == "English" else DF_IT.copy()

    if years:
        df = df[df["year"].isin([int(y) for y in years])]

    if categories:
        mask = df["category"].apply(
            lambda c: any(cat.strip() in categories for cat in str(c).split(";"))
            if pd.notna(c) else False
        )
        df = df[mask]

    if image_filter == "With image only":
        df = df[df["has_image"] == True]
    elif image_filter == "Without image only":
        df = df[df["has_image"] == False]

    if image_categories:
        df = df[df["image_category"].isin(image_categories)]

    if search_text and search_text.strip():
        query = search_text.strip().lower()
        df = df[df["question"].str.lower().str.contains(query, na=False)]

    return df


def apply_filters(language, years, categories, image_filter, image_categories, search_text):
    """Main filter function — returns summary and table."""
    df = filter_dataset(language, years, categories, image_filter, image_categories, search_text)

    display_cols = [
        "year", "question_number", "question_code", "question",
        "answer_a", "answer_b", "answer_c", "answer_d", "answer_e",
        "correct_answer", "category", "has_image", "image_category"
    ]
    display_df = df[display_cols].reset_index(drop=True)

    # Truncate question text for table display
    display_df["question"] = display_df["question"].str[:100] + "..."

    summary = f"**{len(display_df)}** questions match your filters"
    return summary, display_df


def get_question_detail(language, years, categories, image_filter, image_categories, search_text, evt: gr.SelectData):
    """Show full question details when a row is clicked."""
    df = filter_dataset(language, years, categories, image_filter, image_categories, search_text)
    df = df.reset_index(drop=True)

    if evt.index[0] >= len(df):
        return "Select a row to view details."

    row = df.iloc[evt.index[0]]

    img_info = f"Yes — *{row['image_category']}*" if row["has_image"] else "No"

    detail = f"""## Question {row['question_number']} ({row['year']})

| | |
|:--|:--|
| **Code** | `{row['question_code']}` |
| **Category** | {row['category']} |
| **Image** | {img_info} |

---

### {row['question']}

| Option | Answer |
|:------:|:-------|
| **A** ✅ | {row['answer_a']} |
| **B** | {row['answer_b']} |
| **C** | {row['answer_c']} |
| **D** | {row['answer_d']} |
| **E** | {row['answer_e']} |
"""
    return detail


def export_filtered(language, years, categories, image_filter, image_categories, search_text, fmt):
    """Export filtered results to a downloadable file."""
    df = filter_dataset(language, years, categories, image_filter, image_categories, search_text)

    tmp_dir = Path(tempfile.gettempdir()) / "itamed_exports"
    tmp_dir.mkdir(exist_ok=True)

    if fmt == "JSON":
        path = tmp_dir / "ITAMed_filtered.json"
        df.to_json(path, orient="records", force_ascii=False, indent=2)
    else:
        path = tmp_dir / "ITAMed_filtered.xlsx"
        df.to_excel(path, index=False, engine="openpyxl")

    return gr.DownloadButton(value=str(path), visible=True)


def update_categories(language):
    """Update category choices when language changes."""
    choices = CATEGORIES_EN if language == "English" else CATEGORIES_IT
    return gr.update(choices=choices, value=[])


# ==============================================================================
# Statistics
# ==============================================================================


def compute_stats():
    """Generate dataset statistics as Markdown."""
    total = len(DF_IT)
    with_img = int(DF_IT["has_image"].sum())

    cat_counts = {}
    for cats in DF_EN["category"].dropna():
        for cat in str(cats).split(";"):
            cat = cat.strip()
            if cat:
                cat_counts[cat] = cat_counts.get(cat, 0) + 1

    cat_sorted = sorted(cat_counts.items(), key=lambda x: -x[1])
    img_per_year = DF_IT[DF_IT["has_image"]].groupby("year").size()

    stats_md = f"""## Dataset Overview

| Metric | Value |
|:-------|------:|
| Total questions | **{total:,}** |
| Years covered | {YEARS[0]}–{YEARS[-1]} (9 years) |
| Questions per year | 140 |
| Questions with images | {with_img} ({with_img/total*100:.1f}%) |
| Medical specialties | {len(cat_counts)} |
| Image categories | {len(IMAGE_CATEGORIES)} |
| Languages | Italian + English |

---

## Top 10 Medical Specialties (English)

| # | Category | Count | % |
|:-:|:---------|------:|--:|
"""
    for i, (cat, count) in enumerate(cat_sorted[:10], 1):
        stats_md += f"| {i} | {cat} | {count} | {count/total*100:.1f}% |\n"

    stats_md += f"""
---

## Image Questions per Year

| Year | Questions | With Image | % |
|:----:|----------:|-----------:|--:|
"""
    for year in YEARS:
        img_count = img_per_year.get(year, 0)
        stats_md += f"| {year} | 140 | {img_count} | {img_count/140*100:.1f}% |\n"

    return stats_md


# ==============================================================================
# Gradio Interface
# ==============================================================================

THEME = gr.themes.Soft(primary_hue="blue", secondary_hue="slate")

with gr.Blocks(theme=THEME, title="ITAMed Explorer") as demo:
    gr.Markdown(
        """
        <h1 align="center">ITAMed Explorer</h1>
        <p align="center">
            <strong>Interactive browser for the Italian Medical Specialization Exam Dataset (2017–2025)</strong><br/>
            1,260 bilingual medical exam questions · 28 specialties · 76 image questions
        </p>
        <p align="center">
            <a href="https://github.com/LM-Healthcare/ITAMed">GitHub</a> ·
            <a href="https://huggingface.co/datasets/Filo-White/ITAMed">Dataset</a> ·
            Paper (in progress)
        </p>
        """
    )

    with gr.Tabs():
        # ===== Tab 1: Explorer =====
        with gr.TabItem("Explorer"):
            with gr.Row():
                with gr.Column(scale=1, min_width=280):
                    gr.Markdown("### Filters")
                    language = gr.Radio(
                        choices=["Italian", "English"],
                        value="English",
                        label="Language",
                    )
                    years = gr.CheckboxGroup(
                        choices=[str(y) for y in YEARS],
                        value=[],
                        label="Years (leave empty = all)",
                    )
                    categories = gr.Dropdown(
                        choices=CATEGORIES_EN,
                        multiselect=True,
                        label="Medical Specialties",
                        max_choices=5,
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
                        placeholder="e.g. myocardial infarction, ECG...",
                    )
                    filter_btn = gr.Button("Apply Filters", variant="primary", size="lg")

                    gr.Markdown("---")
                    gr.Markdown("### Export Subset")
                    export_fmt = gr.Radio(
                        choices=["JSON", "XLSX"],
                        value="JSON",
                        label="Format",
                    )
                    export_btn = gr.Button("Prepare Download", variant="secondary")
                    export_file = gr.DownloadButton("Save File", visible=False)

                with gr.Column(scale=3):
                    result_summary = gr.Markdown(
                        "Configure filters on the left and click **Apply Filters** to browse."
                    )
                    result_table = gr.Dataframe(
                        interactive=False,
                        wrap=True,
                    )
                    question_detail = gr.Markdown(
                        "*Click any row in the table above to see the full question with all answer options.*"
                    )

            # Event bindings
            language.change(update_categories, inputs=[language], outputs=[categories])
            filter_inputs = [language, years, categories, image_filter, image_cats, search_box]

            filter_btn.click(apply_filters, inputs=filter_inputs, outputs=[result_summary, result_table])
            result_table.select(get_question_detail, inputs=filter_inputs, outputs=[question_detail])
            export_btn.click(export_filtered, inputs=filter_inputs + [export_fmt], outputs=[export_file])

        # ===== Tab 2: Statistics =====
        with gr.TabItem("Statistics"):
            gr.Markdown(compute_stats())

        # ===== Tab 3: About =====
        with gr.TabItem("About"):
            gr.Markdown(
                """
                ## About ITAMed

                **ITAMed** is a comprehensive bilingual dataset of 1,260 multiple-choice questions
                from the Italian National Medical Specialization Entrance Exam (SSM), covering
                all 9 editions from 2017 to 2025.

                The dataset was created as part of a collaboration between **Sapienza Università di Roma**
                (DIAG Department) and **Université Grenoble Alpes** (LIG Laboratory, SANGRIA Team).

                ### Construction Pipeline

                1. **PDF Extraction** — Automated parsing from official exam PDFs using `pdfplumber`
                2. **Specialty Classification** — LLM-based (Claude) classification into 28 categories
                3. **Image Annotation** — Manual identification and categorization (21 image types)
                4. **Translation** — LLM-based expert medical translation (Italian → English)
                5. **Quality Control** — Manual review and validation against source documents

                ### Key Features

                - **Bilingual** — Original Italian + expert English translation
                - **28 medical specialties** — Standardized taxonomy
                - **76 image questions** — With diagnostic image type metadata
                - **Fully structured** — Ready for LLM benchmarking, no preprocessing needed
                - **Multiple formats** — JSON, XLSX available

                ### How to Use

                ```python
                from datasets import load_dataset

                # Load the dataset
                dataset = load_dataset("Filo-White/ITAMed", "en")

                # Filter by specialty
                cardiology = dataset["train"].filter(
                    lambda x: "Cardiology" in x["category"]
                )
                ```

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

                ### Links

                - **GitHub**: [LM-Healthcare/ITAMed](https://github.com/LM-Healthcare/ITAMed)
                - **Related**: [LLM-EVAL-Education](https://github.com/LM-Healthcare/LLM-EVAL-Education)
                """
            )


if __name__ == "__main__":
    demo.launch()
