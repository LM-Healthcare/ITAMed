"""
Shared utilities for loading classification data and common chart settings.
"""

import os
import json
from collections import Counter, defaultdict

import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import numpy as np

# --- Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DATASET_JSON_DIR = os.path.join(REPO_ROOT, "Dataset", "IT", "json")
CHARTS_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "Output")

# Create output dir
os.makedirs(CHARTS_OUTPUT_DIR, exist_ok=True)

# --- Style ---
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['font.size'] = 10
matplotlib.rcParams['axes.titlesize'] = 13
matplotlib.rcParams['axes.labelsize'] = 11
matplotlib.rcParams['figure.dpi'] = 150

# Professional color palette
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
    "Cardiologia e Cardiochirurgia",
    "Chirurgia Generale",
    "Gastroenterologia",
    "Neurologia e Neurochirurgia",
    "Pneumologia e Chirurgia Toracica",
    "Ortopedia e Traumatologia",
    "Endocrinologia",
    "Ginecologia e Ostetricia",
    "Pediatria",
    "Urologia",
    "Nefrologia",
    "Ematologia",
    "Oncologia",
    "Malattie Infettive",
    "Immunologia e Reumatologia",
    "Dermatologia e Venereologia",
    "Psichiatria",
    "Oftalmologia",
    "Otorinolaringoiatria",
    "Anestesia e Rianimazione",
    "Igiene, Epidemiologia e Statistica",
    "Medicina del Lavoro",
    "Medicina Legale",
    "Diagnostica per Immagini e Medicina Nucleare",
    "Genetica Medica",
    "Farmacologia e Tossicologia",
    "Nutrizione Clinica",
    "Medicina Interna",
]

# Short labels for charts
CATEGORY_SHORT = {
    "Cardiologia e Cardiochirurgia": "Cardiologia",
    "Chirurgia Generale": "Chir. Generale",
    "Gastroenterologia": "Gastroenterologia",
    "Neurologia e Neurochirurgia": "Neurologia",
    "Pneumologia e Chirurgia Toracica": "Pneumologia",
    "Ortopedia e Traumatologia": "Ortopedia",
    "Endocrinologia": "Endocrinologia",
    "Ginecologia e Ostetricia": "Ginecologia",
    "Pediatria": "Pediatria",
    "Urologia": "Urologia",
    "Nefrologia": "Nefrologia",
    "Ematologia": "Ematologia",
    "Oncologia": "Oncologia",
    "Malattie Infettive": "Mal. Infettive",
    "Immunologia e Reumatologia": "Immunologia",
    "Dermatologia e Venereologia": "Dermatologia",
    "Psichiatria": "Psichiatria",
    "Oftalmologia": "Oftalmologia",
    "Otorinolaringoiatria": "ORL",
    "Anestesia e Rianimazione": "Anestesia",
    "Igiene, Epidemiologia e Statistica": "Igiene/Epid.",
    "Medicina del Lavoro": "Med. Lavoro",
    "Medicina Legale": "Med. Legale",
    "Diagnostica per Immagini e Medicina Nucleare": "Diagnostica Imm.",
    "Genetica Medica": "Genetica",
    "Farmacologia e Tossicologia": "Farmacologia",
    "Nutrizione Clinica": "Nutrizione",
    "Medicina Interna": "Med. Interna",
}

YEARS = list(range(2017, 2026))


def load_all_classifications():
    """Load all classification data from dataset JSON files.
    
    Returns dict: {year: {q_num: category_str}}
    """
    all_data = {}
    for year in YEARS:
        json_path = os.path.join(DATASET_JSON_DIR, f"ITAMed_{year}.json")
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
    """Get distributions for all years. Returns {year: Counter}"""
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
    """Get short label for a category."""
    return CATEGORY_SHORT.get(cat, cat)


def save_figure(fig, filename):
    """Save figure to output directory."""
    path = os.path.join(CHARTS_OUTPUT_DIR, filename)
    fig.savefig(path, bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")
