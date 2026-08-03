# Distribution Charts

## Overview

This directory contains all visualizations of the ITAMed dataset's question distribution across medical specialties, years, and multi-specialty classification patterns.

All charts are generated from the final, expert-validated English dataset (`Dataset/EN/json/`).

---

## Charts

### Aggregate Distribution

| Chart | Description |
|:------|:------------|
| `aggregate_bar_chart.png` | Horizontal bar chart — total questions by specialty (all years) |
| `aggregate_pie_chart.png` | Pie chart — proportional distribution across 28 specialties |
| `average_per_year_bar.png` | Horizontal bar chart — average questions per year by specialty |
| `combined_distribution_chart.png` | **Combined figure**: (a) aggregate distribution + (b) single vs multi-specialty by year |

### Per-Year Charts

For each year (2017–2025):
- `{year}_bar_chart.png` — Horizontal bar chart of that year's specialty distribution
- `{year}_pie_chart.png` — Pie chart of that year's specialty distribution

### Advanced Analysis

| Chart | Description |
|:------|:------------|
| `heatmap_categories_years.png` | **Heatmap**: questions by specialty × year (28 × 9 matrix) |
| `stacked_bar_years.png` | Stacked bar chart — yearly composition by top 12 specialties |
| `trend_lines_top8.png` | Line chart — question count trends for top 8 specialties |
| `radar_comparison.png` | Radar/spider chart — distribution comparison: 2017 vs 2021 vs 2025 |
| `variability_categories.png` | Horizontal bar chart — mean ± SD with coefficient of variation |
| `multi_specialty_analysis.png` | Dual panel: single vs multi-specialty counts + top combinations |
| `percentage_evolution_top6.png` | Line chart — percentage evolution of top 6 specialties |

---

## Scripts

| Script | Description |
|:-------|:------------|
| `chart_utils_en.py` | Shared utilities: data loading, paths, palette, category labels |
| `chart_aggregate_en.py` | Aggregate distribution charts |
| `chart_per_year_en.py` | Per-year bar and pie charts |
| `chart_advanced_en.py` | Heatmap, trends, radar, variability, multi-specialty |
| `chart_combined_en.py` | Combined distribution + multi-specialty chart |
| `generate_all_en.py` | Master script — generates all charts in one run |

### Regenerating All Charts

```bash
python Charts_EN/scripts/generate_all_en.py
```

Output is saved to `Charts_EN/Output/`.

### Requirements

```
matplotlib
seaborn
numpy
```
