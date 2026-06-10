"""
Aggregate English charts across all years (2017-2025).
"""

import sys
sys.path.insert(0, r"c:\Users\filow\OneDrive\Desktop\Repository\ITAMed\Charts_EN")

import matplotlib.pyplot as plt
import numpy as np
from chart_utils_en import (
    get_aggregate_distribution, get_all_distributions,
    CATEGORIES, PALETTE, YEARS,
    short_label, save_figure
)


def plot_aggregate_pie():
    """Pie chart of total question distribution across all years."""
    total = get_aggregate_distribution()
    
    sorted_cats = sorted(CATEGORIES, key=lambda c: total.get(c, 0), reverse=True)
    counts = [total.get(c, 0) for c in sorted_cats]
    labels = [short_label(c) for c in sorted_cats]
    
    total_sum = sum(counts)
    threshold = total_sum * 0.02
    main_labels, main_counts, main_colors = [], [], []
    other_count = 0
    
    for i, (label, count) in enumerate(zip(labels, counts)):
        if count >= threshold:
            main_labels.append(f"{label} ({count})")
            main_counts.append(count)
            main_colors.append(PALETTE[i % len(PALETTE)])
        else:
            other_count += count
    
    if other_count > 0:
        main_labels.append(f"Other ({other_count})")
        main_counts.append(other_count)
        main_colors.append('#cccccc')
    
    fig, ax = plt.subplots(figsize=(12, 10))
    wedges, texts, autotexts = ax.pie(
        main_counts, labels=None, autopct='%1.1f%%',
        colors=main_colors, startangle=90, pctdistance=0.85,
    )
    for autotext in autotexts:
        autotext.set_fontsize(8)
    
    ax.legend(wedges, main_labels, title="Specializations",
              loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)
    ax.set_title(f"Aggregate SSM Question Distribution (2017-2025)\nTotal: {total_sum} questions",
                 fontsize=14, fontweight='bold')
    save_figure(fig, "aggregate_pie_chart.png")


def plot_aggregate_bar():
    """Horizontal bar chart of total distribution."""
    total = get_aggregate_distribution()
    
    sorted_cats = sorted(CATEGORIES, key=lambda c: total.get(c, 0), reverse=True)
    counts = [total.get(c, 0) for c in sorted_cats]
    labels = [short_label(c) for c in sorted_cats]
    
    fig, ax = plt.subplots(figsize=(12, 10))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(labels))]
    bars = ax.barh(range(len(labels)), counts, color=colors, edgecolor='white', linewidth=0.5)
    
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Number of questions")
    ax.set_title("Aggregate SSM Question Distribution (2017-2025)", fontsize=14, fontweight='bold')
    
    for bar, count in zip(bars, counts):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                str(count), va='center', fontsize=9)
    
    ax.set_xlim(0, max(counts) * 1.15)
    plt.tight_layout()
    save_figure(fig, "aggregate_bar_chart.png")


def plot_average_per_year_bar():
    """Bar chart showing average questions per year per category."""
    distributions = get_all_distributions()
    n_years = len(distributions)
    
    avg_counts = {}
    for cat in CATEGORIES:
        total = sum(d.get(cat, 0) for d in distributions.values())
        avg_counts[cat] = total / n_years
    
    sorted_cats = sorted(CATEGORIES, key=lambda c: avg_counts[c], reverse=True)
    avgs = [avg_counts[c] for c in sorted_cats]
    labels = [short_label(c) for c in sorted_cats]
    
    fig, ax = plt.subplots(figsize=(12, 10))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(labels))]
    bars = ax.barh(range(len(labels)), avgs, color=colors, edgecolor='white', linewidth=0.5)
    
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Average questions per year")
    ax.set_title("Average Questions per Year by Specialization (2017-2025)", fontsize=14, fontweight='bold')
    
    for bar, avg in zip(bars, avgs):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f"{avg:.1f}", va='center', fontsize=9)
    
    ax.set_xlim(0, max(avgs) * 1.15)
    plt.tight_layout()
    save_figure(fig, "average_per_year_bar.png")


if __name__ == "__main__":
    print("Generating aggregate charts (EN)...")
    plot_aggregate_pie()
    plot_aggregate_bar()
    plot_average_per_year_bar()
    print("Done!")
