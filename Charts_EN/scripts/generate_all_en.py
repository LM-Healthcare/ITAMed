"""
Master script: generates ALL English charts in one run.
Output: Charts_EN/Output/
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("GENERATING ALL SSM CHARTS (ENGLISH)")
print("=" * 50)

print("\n[1/4] Aggregate charts...")
from chart_aggregate_en import plot_aggregate_pie, plot_aggregate_bar, plot_average_per_year_bar
plot_aggregate_pie()
plot_aggregate_bar()
plot_average_per_year_bar()

print("\n[2/4] Per-year charts...")
from chart_per_year_en import plot_year_pie, plot_year_bar
from chart_utils_en import get_all_distributions, YEARS
distributions = get_all_distributions()
for year in YEARS:
    if year in distributions:
        print(f"  {year}:")
        plot_year_pie(year, distributions[year])
        plot_year_bar(year, distributions[year])

print("\n[3/4] Advanced charts...")
from chart_advanced_en import (
    plot_heatmap, plot_stacked_bar, plot_trend_lines,
    plot_radar_comparison, plot_variability, plot_multi_specialty,
    plot_percentage_evolution
)
plot_heatmap()
plot_stacked_bar()
plot_trend_lines()
plot_radar_comparison()
plot_variability()
plot_multi_specialty()
plot_percentage_evolution()

print("\n[4/4] Combined chart...")
from chart_combined_en import plot_combined
plot_combined()

print("\n" + "=" * 50)
print("ALL ENGLISH CHARTS GENERATED SUCCESSFULLY!")
print(f"Output directory: Charts_EN\\Output\\")
print("=" * 50)
