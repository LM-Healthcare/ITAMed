"""
Shared utilities for English charts - loading classification data and common settings.
"""

import os
import json
from collections import Counter

import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import numpy as np

# --- Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHARTS_DIR = os.path.dirname(SCRIPT_DIR)
REPO_ROOT = os.path.dirname(CHARTS_DIR)
DATASET_JSON_DIR = os.path.join(REPO_ROOT, "Dataset", "EN", "json")
CHARTS_OUTPUT_DIR = os.path.join(CHARTS_DIR, "Output")

os.makedirs(CHARTS_OUTPUT_DIR, exist_ok=True)

# --- Style ---
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['font.size'] = 10
matplotlib.rcParams['axes.titlesize'] = 13
matplotlib.rcParams['axes.labelsize'] = 11
matplotlib.rcParams['figure.dpi'] = 150

PALETTE = sns.color_palette("husl", 28)
YEAR_COLORS = {
    2017: '#1f77b4',
    2018: '#ff7f0e',
    2019: '#2ca02c',
    2020: '#d62728',
    2021: '#9467bd',
    2022: '#8c564b',
    2023: '#e377c2',
    2024: '#7f7f7f',
    2025: '#bcbd22',
}

CATEGORIES = [
    "Cardiology and Cardiac Surgery",
    "General Surgery",
    "Gastroenterology",
    "Neurology and Neurosurgery",
    "Pulmonology and Thoracic Surgery",
    "Orthopedics and Traumatology",
    "Endocrinology",
    "Gynecology and Obstetrics",
    "Pediatrics",
    "Urology",
    "Nephrology",
    "Hematology",
    "Oncology",
    "Infectious Diseases",
    "Immunology and Rheumatology",
    "Dermatology and Venereology",
    "Psychiatry",
    "Ophthalmology",
    "Otorhinolaryngology",
    "Anesthesia and Intensive Care",
    "Hygiene, Epidemiology and Statistics",
    "Occupational Medicine",
    "Forensic Medicine",
    "Diagnostic Imaging and Nuclear Medicine",
    "Medical Genetics",
    "Pharmacology and Toxicology",
    "Clinical Nutrition",
    "Internal Medicine",
]

CATEGORY_SHORT = {
    "Cardiology and Cardiac Surgery": "Cardiology",
    "General Surgery": "General Surgery",
    "Gastroenterology": "Gastroenterology",
    "Neurology and Neurosurgery": "Neurology",
    "Pulmonology and Thoracic Surgery": "Pulmonology",
    "Orthopedics and Traumatology": "Orthopedics",
    "Endocrinology": "Endocrinology",
    "Gynecology and Obstetrics": "Gynecology",
    "Pediatrics": "Pediatrics",
    "Urology": "Urology",
    "Nephrology": "Nephrology",
    "Hematology": "Hematology",
    "Oncology": "Oncology",
    "Infectious Diseases": "Infectious Dis.",
    "Immunology and Rheumatology": "Immunology",
    "Dermatology and Venereology": "Dermatology",
    "Psychiatry": "Psychiatry",
    "Ophthalmology": "Ophthalmology",
    "Otorhinolaryngology": "ENT",
    "Anesthesia and Intensive Care": "Anesthesia/ICU",
    "Hygiene, Epidemiology and Statistics": "Hygiene/Epid.",
    "Occupational Medicine": "Occup. Medicine",
    "Forensic Medicine": "Forensic Med.",
    "Diagnostic Imaging and Nuclear Medicine": "Diagnostic Img.",
    "Medical Genetics": "Genetics",
    "Pharmacology and Toxicology": "Pharmacology",
    "Clinical Nutrition": "Nutrition",
    "Internal Medicine": "Internal Med.",
}

YEARS = list(range(2017, 2026))


def load_all_classifications():
    """Load all English classification data from dataset JSON files.
    
    Returns dict: {year: {q_num: category_str}}
    """
    all_data = {}
    for year in YEARS:
        json_path = os.path.join(DATASET_JSON_DIR, f"ITAMed_{year}_EN.json")
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                items = json.load(f)
            year_data = {}
            for item in items:
                q_num = str(item["question_number"])
                year_data[q_num] = item.get("category", "")
            all_data[year] = year_data
    return all_data


def get_distribution(classifications_dict):
    """Get category counts from a single year's classifications."""
    counts = Counter()
    for cat_str in classifications_dict.values():
        for cat in cat_str.split("; "):
            cat = cat.strip()
            if cat:
                counts[cat] += 1
    return counts


def get_all_distributions():
    """Get distributions for all years."""
    all_data = load_all_classifications()
    distributions = {}
    for year, data in all_data.items():
        distributions[year] = get_distribution(data)
    return distributions


def get_aggregate_distribution():
    """Get total distribution across all years."""
    distributions = get_all_distributions()
    total = Counter()
    for year_dist in distributions.values():
        total.update(year_dist)
    return total


def short_label(cat):
    return CATEGORY_SHORT.get(cat, cat)


def save_figure(fig, filename):
    path = os.path.join(CHARTS_OUTPUT_DIR, filename)
    fig.savefig(path, bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")
