"""
Advanced/professional English charts:
1. Heatmap: categories x years
2. Stacked bar chart
3. Trend lines: top categories over time
4. Radar/spider chart: year comparison
5. Category variability (std dev across years)
6. Multi-specialty question analysis
7. Percentage evolution top 6
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from collections import Counter
from chart_utils_en import (
    get_all_distributions, load_all_classifications,
    CATEGORIES, PALETTE, YEARS, YEAR_COLORS,
    short_label, save_figure
)


def plot_heatmap():
    """Heatmap of categories x years."""
    distributions = get_all_distributions()
    years_available = sorted(distributions.keys())
    
    matrix = np.zeros((len(CATEGORIES), len(years_available)))
    for j, year in enumerate(years_available):
        for i, cat in enumerate(CATEGORIES):
            matrix[i, j] = distributions[year].get(cat, 0)
    
    totals = matrix.sum(axis=1)
    sort_idx = np.argsort(-totals)
    matrix = matrix[sort_idx]
    sorted_labels = [short_label(CATEGORIES[i]) for i in sort_idx]
    
    fig, ax = plt.subplots(figsize=(12, 12))
    im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto')
    
    ax.set_xticks(range(len(years_available)))
    ax.set_xticklabels(years_available, fontsize=10)
    ax.set_yticks(range(len(sorted_labels)))
    ax.set_yticklabels(sorted_labels, fontsize=9)
    
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = int(matrix[i, j])
            color = 'white' if val > matrix.max() * 0.6 else 'black'
            ax.text(j, i, str(val), ha='center', va='center', fontsize=8, color=color)
    
    ax.set_title("Heatmap: Questions by Specialization and Year", fontsize=14, fontweight='bold')
    fig.colorbar(im, ax=ax, label="Number of questions", shrink=0.8)
    plt.tight_layout()
    save_figure(fig, "heatmap_categories_years.png")


def plot_stacked_bar():
    """Stacked bar chart: each year stacked by category proportions."""
    distributions = get_all_distributions()
    years_available = sorted(distributions.keys())
    
    total = Counter()
    for d in distributions.values():
        total.update(d)
    top_cats = [cat for cat, _ in total.most_common(12)]
    
    fig, ax = plt.subplots(figsize=(14, 8))
    bottom = np.zeros(len(years_available))
    
    for i, cat in enumerate(top_cats):
        values = [distributions[y].get(cat, 0) for y in years_available]
        ax.bar(range(len(years_available)), values, bottom=bottom,
               label=short_label(cat), color=PALETTE[i], edgecolor='white', linewidth=0.3)
        bottom += np.array(values)
    
    other_values = []
    for y in years_available:
        other = sum(v for k, v in distributions[y].items() if k not in top_cats)
        other_values.append(other)
    ax.bar(range(len(years_available)), other_values, bottom=bottom,
           label="Other", color='#cccccc', edgecolor='white', linewidth=0.3)
    
    ax.set_xticks(range(len(years_available)))
    ax.set_xticklabels(years_available, fontsize=11)
    ax.set_ylabel("Number of questions")
    ax.set_title("SSM Question Composition by Year (Top 12 Specializations)", fontsize=14, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)
    ax.set_ylim(0, 155)
    plt.tight_layout()
    save_figure(fig, "stacked_bar_years.png")


def plot_trend_lines():
    """Line chart showing trends for top categories over the years."""
    distributions = get_all_distributions()
    years_available = sorted(distributions.keys())
    
    total = Counter()
    for d in distributions.values():
        total.update(d)
    top_cats = [cat for cat, _ in total.most_common(8)]
    
    fig, ax = plt.subplots(figsize=(13, 7))
    
    for i, cat in enumerate(top_cats):
        values = [distributions[y].get(cat, 0) for y in years_available]
        ax.plot(years_available, values, marker='o', linewidth=2, markersize=6,
                label=short_label(cat), color=PALETTE[i])
    
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of questions")
    ax.set_title("Question Trends by Specialization (Top 8)", fontsize=14, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)
    ax.set_xticks(years_available)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)
    plt.tight_layout()
    save_figure(fig, "trend_lines_top8.png")


def plot_radar_comparison():
    """Radar/spider chart comparing 2017, 2021, 2025."""
    distributions = get_all_distributions()
    compare_years = [2017, 2021, 2025]
    
    total = Counter()
    for d in distributions.values():
        total.update(d)
    top_cats = [cat for cat, _ in total.most_common(12)]
    
    n_cats = len(top_cats)
    angles = np.linspace(0, 2 * np.pi, n_cats, endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    for year in compare_years:
        if year not in distributions:
            continue
        values = [distributions[year].get(cat, 0) for cat in top_cats]
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=2, markersize=4,
                label=str(year), color=YEAR_COLORS[year])
        ax.fill(angles, values, alpha=0.1, color=YEAR_COLORS[year])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([short_label(c) for c in top_cats], fontsize=8)
    ax.set_title("Distribution Comparison: 2017 vs 2021 vs 2025", fontsize=13, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.tight_layout()
    save_figure(fig, "radar_comparison.png")


def plot_variability():
    """Bar chart showing category variability across years."""
    distributions = get_all_distributions()
    years_available = sorted(distributions.keys())
    
    stats = {}
    for cat in CATEGORIES:
        values = [distributions[y].get(cat, 0) for y in years_available]
        stats[cat] = {
            'mean': np.mean(values),
            'std': np.std(values),
            'cv': np.std(values) / np.mean(values) if np.mean(values) > 0 else 0,
        }
    
    sorted_cats = sorted(CATEGORIES, key=lambda c: stats[c]['cv'], reverse=True)
    sorted_cats = [c for c in sorted_cats if stats[c]['mean'] >= 1]
    
    labels = [short_label(c) for c in sorted_cats]
    means = [stats[c]['mean'] for c in sorted_cats]
    stds = [stats[c]['std'] for c in sorted_cats]
    
    fig, ax = plt.subplots(figsize=(12, 10))
    y_pos = range(len(labels))
    bars = ax.barh(y_pos, means, xerr=stds, color=PALETTE[:len(labels)],
                   edgecolor='white', linewidth=0.5, capsize=3, error_kw={'linewidth': 1})
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Questions (mean ± standard deviation)")
    ax.set_title("Specialization Variability Over Time (2017-2025)\nSorted by coefficient of variation",
                 fontsize=13, fontweight='bold')
    
    for i, cat in enumerate(sorted_cats):
        cv = stats[cat]['cv']
        ax.text(means[i] + stds[i] + 0.5, i, f"CV={cv:.2f}", va='center', fontsize=8, color='gray')
    
    plt.tight_layout()
    save_figure(fig, "variability_categories.png")


def plot_multi_specialty():
    """Analysis of multi-specialty questions."""
    all_data = load_all_classifications()
    
    yearly_multi = {}
    yearly_single = {}
    multi_combos = Counter()
    
    for year, data in all_data.items():
        multi = 0
        single = 0
        for cat_str in data.values():
            cats = [c.strip() for c in cat_str.split(";") if c.strip()]
            if len(cats) > 1:
                multi += 1
                combo = " + ".join(sorted([short_label(c) for c in cats]))
                multi_combos[combo] += 1
            else:
                single += 1
        yearly_multi[year] = multi
        yearly_single[year] = single
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    years_available = sorted(yearly_multi.keys())
    multi_vals = [yearly_multi[y] for y in years_available]
    single_vals = [yearly_single[y] for y in years_available]
    
    x = np.arange(len(years_available))
    width = 0.35
    
    ax1.bar(x - width/2, single_vals, width, label='Single-specialty', color='#2196F3')
    ax1.bar(x + width/2, multi_vals, width, label='Multi-specialty', color='#FF5722')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Number of questions')
    ax1.set_title('Single vs Multi-specialty Questions', fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(years_available)
    ax1.legend()
    ax1.set_ylim(0, 150)
    
    top_combos = multi_combos.most_common(10)
    if top_combos:
        combo_labels = [c[0] for c in top_combos]
        combo_counts = [c[1] for c in top_combos]
        ax2.barh(range(len(combo_labels)), combo_counts, color=PALETTE[:len(combo_labels)])
        ax2.set_yticks(range(len(combo_labels)))
        ax2.set_yticklabels(combo_labels, fontsize=8)
        ax2.invert_yaxis()
        ax2.set_xlabel('Frequency')
        ax2.set_title('Most Frequent Multi-specialty Combinations', fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    save_figure(fig, "multi_specialty_analysis.png")


def plot_percentage_evolution():
    """Percentage evolution of top 6 categories."""
    distributions = get_all_distributions()
    years_available = sorted(distributions.keys())
    
    total = Counter()
    for d in distributions.values():
        total.update(d)
    top_cats = [cat for cat, _ in total.most_common(6)]
    
    fig, ax = plt.subplots(figsize=(13, 7))
    
    for i, cat in enumerate(top_cats):
        percentages = [(distributions[y].get(cat, 0) / 140) * 100 for y in years_available]
        ax.plot(years_available, percentages, marker='s', linewidth=2.5, markersize=7,
                label=short_label(cat), color=PALETTE[i])
        ax.annotate(f"{percentages[-1]:.1f}%", (years_available[-1], percentages[-1]),
                    textcoords="offset points", xytext=(10, 0), fontsize=8)
    
    ax.set_xlabel("Year")
    ax.set_ylabel("Percentage (%)")
    ax.set_title("Percentage Evolution of Top 6 Specializations", fontsize=14, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=10)
    ax.set_xticks(years_available)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)
    plt.tight_layout()
    save_figure(fig, "percentage_evolution_top6.png")


if __name__ == "__main__":
    print("Generating advanced charts (EN)...")
    plot_heatmap()
    plot_stacked_bar()
    plot_trend_lines()
    plot_radar_comparison()
    plot_variability()
    plot_multi_specialty()
    plot_percentage_evolution()
    print("\nAll advanced charts generated!")
