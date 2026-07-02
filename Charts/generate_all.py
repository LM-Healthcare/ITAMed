"""
Master script: generates ALL charts in one run.
Output: Charts/Output/
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("GENERATING ALL SSM CHARTS")
print("=" * 50)

print("\n[1/3] Aggregate charts...")
from chart_aggregate import plot_aggregate_pie, plot_aggregate_bar, plot_average_per_year_bar
plot_aggregate_pie()
plot_aggregate_bar()
plot_average_per_year_bar()

print("\n[2/3] Per-year charts...")
from chart_per_year import plot_year_pie, plot_year_bar
from chart_utils import get_all_distributions, YEARS
distributions = get_all_distributions()
for year in YEARS:
    if year in distributions:
        print(f"  {year}:")
        plot_year_pie(year, distributions[year])
        plot_year_bar(year, distributions[year])

print("\n[3/3] Advanced charts...")
from chart_advanced import (
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

print("\n" + "=" * 50)
print("ALL CHARTS GENERATED SUCCESSFULLY!")
print(f"Output directory: Charts\\Output\\")
print("=" * 50)
