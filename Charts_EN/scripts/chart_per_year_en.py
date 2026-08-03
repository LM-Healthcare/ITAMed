"""
Per-year English charts: pie + bar for each year (2017-2025).
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
from chart_utils_en import (
    get_all_distributions, CATEGORIES, PALETTE, YEARS,
    short_label, save_figure
)


def plot_year_pie(year, distribution):
    """Pie chart for a single year."""
    sorted_cats = sorted(CATEGORIES, key=lambda c: distribution.get(c, 0), reverse=True)
    counts = [distribution.get(c, 0) for c in sorted_cats]
    labels = [short_label(c) for c in sorted_cats]
    
    non_zero = [(l, c, PALETTE[i % len(PALETTE)]) for i, (l, c) in enumerate(zip(labels, counts)) if c > 0]
    labels_nz = [x[0] for x in non_zero]
    counts_nz = [x[1] for x in non_zero]
    colors_nz = [x[2] for x in non_zero]
    
    total = sum(counts_nz)
    threshold = total * 0.02
    main_labels, main_counts, main_colors = [], [], []
    other_count = 0
    
    for label, count, color in zip(labels_nz, counts_nz, colors_nz):
        if count >= threshold:
            main_labels.append(f"{label} ({count})")
            main_counts.append(count)
            main_colors.append(color)
        else:
            other_count += count
    
    if other_count > 0:
        main_labels.append(f"Other ({other_count})")
        main_counts.append(other_count)
        main_colors.append('#cccccc')
    
    fig, ax = plt.subplots(figsize=(11, 9))
    wedges, texts, autotexts = ax.pie(
        main_counts, labels=None, autopct='%1.1f%%',
        colors=main_colors, startangle=90, pctdistance=0.85,
    )
    for autotext in autotexts:
        autotext.set_fontsize(8)
    
    ax.legend(wedges, main_labels, title="Specializations",
              loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)
    ax.set_title(f"SSM Question Distribution {year}\n(140 questions)", fontsize=14, fontweight='bold')
    save_figure(fig, f"{year}_pie_chart.png")


def plot_year_bar(year, distribution):
    """Horizontal bar chart for a single year."""
    sorted_cats = sorted(CATEGORIES, key=lambda c: distribution.get(c, 0), reverse=True)
    counts = [distribution.get(c, 0) for c in sorted_cats]
    labels = [short_label(c) for c in sorted_cats]
    
    non_zero_idx = [i for i, c in enumerate(counts) if c > 0]
    labels = [labels[i] for i in non_zero_idx]
    counts = [counts[i] for i in non_zero_idx]
    colors = [PALETTE[i % len(PALETTE)] for i in non_zero_idx]
    
    fig, ax = plt.subplots(figsize=(11, max(8, len(labels) * 0.4)))
    bars = ax.barh(range(len(labels)), counts, color=colors, edgecolor='white', linewidth=0.5)
    
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Number of questions")
    ax.set_title(f"SSM Question Distribution {year}", fontsize=14, fontweight='bold')
    
    for bar, count in zip(bars, counts):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                str(count), va='center', fontsize=9)
    
    ax.set_xlim(0, max(counts) * 1.2 if counts else 1)
    plt.tight_layout()
    save_figure(fig, f"{year}_bar_chart.png")


if __name__ == "__main__":
    print("Generating per-year charts (EN)...")
    distributions = get_all_distributions()
    
    for year in YEARS:
        if year in distributions:
            print(f"\n  {year}:")
            plot_year_pie(year, distributions[year])
            plot_year_bar(year, distributions[year])
    
    print("\nDone!")
