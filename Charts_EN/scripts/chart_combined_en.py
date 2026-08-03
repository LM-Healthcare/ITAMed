"""
Combined chart:
  Top: Horizontal bar chart — aggregate question distribution by category
  Bottom: Grouped bar chart — single vs multi-specialty questions by year
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from collections import Counter
from chart_utils_en import (
    load_all_classifications, get_all_distributions,
    get_aggregate_distribution, CATEGORIES, PALETTE, YEARS,
    short_label, save_figure
)


def plot_combined():
    """Combined figure: distribution bar + multi/single specialty by year."""
    all_data = load_all_classifications()
    aggregate = get_aggregate_distribution()

    # --- Data prep: aggregate distribution (sorted descending) ---
    sorted_cats = sorted(CATEGORIES, key=lambda c: aggregate.get(c, 0), reverse=True)
    sorted_cats = [c for c in sorted_cats if aggregate.get(c, 0) > 0]
    cat_counts = [aggregate[c] for c in sorted_cats]
    cat_labels = [short_label(c) for c in sorted_cats]
    n_cats = len(sorted_cats)

    # --- Data prep: multi vs single by year ---
    years_available = sorted(all_data.keys())
    single_vals = []
    multi_vals = []
    multi_pct = []
    for year in years_available:
        multi = 0
        single = 0
        for cat_str in all_data[year].values():
            cats = [c.strip() for c in cat_str.split(";") if c.strip()]
            if len(cats) > 1:
                multi += 1
            else:
                single += 1
        single_vals.append(single)
        multi_vals.append(multi)
        total = single + multi
        multi_pct.append(multi / total * 100 if total else 0)

    # --- Create figure with GridSpec ---
    fig = plt.figure(figsize=(16, 14))
    gs = gridspec.GridSpec(2, 1, height_ratios=[2.2, 1], hspace=0.30)

    # ===== TOP: Horizontal bar chart =====
    ax1 = fig.add_subplot(gs[0])

    # Use a gradient colormap for visual appeal
    cmap = plt.cm.YlOrRd
    norm_vals = np.array(cat_counts) / max(cat_counts) if max(cat_counts) > 0 else np.zeros(n_cats)
    bar_colors = [cmap(0.25 + 0.65 * v) for v in norm_vals]

    y_pos = np.arange(n_cats)
    bars = ax1.barh(y_pos, cat_counts, color=bar_colors, edgecolor='white', linewidth=0.5, height=0.75)

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(cat_labels, fontsize=10)
    ax1.invert_yaxis()
    ax1.set_xlabel("Number of Questions (across all years)", fontsize=11)
    ax1.set_title("(a) Aggregate Question Distribution by Medical Specialty",
                  fontsize=14, fontweight='bold', pad=12)

    # Add count labels
    max_val = max(cat_counts)
    for i, (bar, val) in enumerate(zip(bars, cat_counts)):
        pct = val / sum(cat_counts) * 100
        if val > max_val * 0.15:
            ax1.text(val - 1, i, f"{val}", ha='right', va='center',
                     fontsize=9, fontweight='bold', color='white')
            ax1.text(val + 1, i, f"({pct:.1f}%)", ha='left', va='center',
                     fontsize=8, color='#444444')
        else:
            ax1.text(val + 1, i, f"{val} ({pct:.1f}%)", ha='left', va='center',
                     fontsize=8, color='#444444')

    ax1.set_xlim(0, max_val * 1.18)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # ===== BOTTOM: Grouped bar — single vs multi by year =====
    ax2 = fig.add_subplot(gs[1])

    x = np.arange(len(years_available))
    width = 0.35

    bars_s = ax2.bar(x - width/2, single_vals, width,
                     label='Single-specialty', color='#2196F3',
                     edgecolor='white', linewidth=0.5)
    bars_m = ax2.bar(x + width/2, multi_vals, width,
                     label='Multi-specialty', color='#FF5722',
                     edgecolor='white', linewidth=0.5)

    ax2.set_xlabel('Year', fontsize=11)
    ax2.set_ylabel('Number of Questions', fontsize=11)
    ax2.set_title('(b) Single-Specialty vs Multi-Specialty Questions by Year',
                  fontsize=14, fontweight='bold', pad=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(years_available, fontsize=11)
    ax2.legend(fontsize=11, loc='upper right')
    ax2.set_ylim(0, 155)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    # Add value labels on bars
    for bar in bars_s:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, h + 1, str(int(h)),
                 ha='center', va='bottom', fontsize=9, color='#1565C0')
    for bar in bars_m:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, h + 1, str(int(h)),
                 ha='center', va='bottom', fontsize=9, color='#BF360C')

    # Add secondary y-axis for multi-specialty percentage
    ax2b = ax2.twinx()
    ax2b.plot(x, multi_pct, color='#FF5722', marker='D', linewidth=2,
              markersize=6, linestyle='--', alpha=0.7, label='Multi-specialty %')
    ax2b.set_ylabel('Multi-specialty (%)', fontsize=10, color='#BF360C')
    ax2b.set_ylim(0, 100)
    ax2b.tick_params(axis='y', labelcolor='#BF360C')
    ax2b.spines['top'].set_visible(False)

    # Annotate percentages
    for xi, pct in zip(x, multi_pct):
        ax2b.annotate(f"{pct:.0f}%", (xi, pct), textcoords="offset points",
                      xytext=(0, 10), ha='center', fontsize=8, color='#BF360C',
                      fontweight='bold')

    save_figure(fig, "combined_distribution_chart.png")
    print("  Combined chart generated successfully!")


if __name__ == "__main__":
    print("Generating combined distribution chart...")
    plot_combined()
