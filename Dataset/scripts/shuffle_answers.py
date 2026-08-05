"""
==============================================================================
ITAMed — Answer Shuffling Utility
==============================================================================

Purpose:
    Produces a version of the dataset with randomized answer option order.

    In the official release, the correct answer is always in position A
    (this reflects the original PDF format). For evaluation and benchmarking
    purposes, this script generates a shuffled version where the correct
    answer appears in a random position for each question.

    The shuffled output preserves a mapping from each question to its new
    correct answer position, enabling deterministic re-shuffling with a
    fixed random seed.

Input:
    - Dataset/IT/json/ITAMed_complete.json   (or per-year files)
    - Dataset/EN/json/ITAMed_complete_EN.json

Output:
    - Dataset/IT/json/ITAMed_complete_shuffled.json
    - Dataset/EN/json/ITAMed_complete_EN_shuffled.json
    (or per-year equivalents if --per-year is specified)

    Each shuffled question includes:
      - All original fields
      - answer_a through answer_e: reordered answers
      - correct_answer: updated to reflect new position (A–E)
      - shuffle_mapping: dict mapping original position → new position

Usage:
    python Dataset/scripts/shuffle_answers.py [--seed 42] [--per-year]

    --seed N       Random seed for reproducibility (default: 42)
    --per-year     Also generate per-year shuffled files

Author: ITAMed Dataset Team
==============================================================================
"""

import os
import sys
import json
import random
import argparse
from copy import deepcopy

# ==============================================================================
# Configuration
# ==============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.dirname(SCRIPT_DIR)
REPO_DIR = os.path.dirname(DATASET_DIR)

IT_JSON_DIR = os.path.join(DATASET_DIR, "IT", "json")
EN_JSON_DIR = os.path.join(DATASET_DIR, "EN", "json")

YEARS = list(range(2017, 2026))
POSITIONS = ["A", "B", "C", "D", "E"]
ANSWER_KEYS = ["answer_a", "answer_b", "answer_c", "answer_d", "answer_e"]


# ==============================================================================
# Shuffling Logic
# ==============================================================================


def shuffle_question(item: dict, rng: random.Random) -> dict:
    """
    Shuffle the answer options of a single question.

    Args:
        item: Original question dict.
        rng: Random number generator instance.

    Returns:
        New question dict with shuffled answers and updated correct_answer.
    """
    shuffled = deepcopy(item)

    # Extract original answers in order
    original_answers = [item[key] for key in ANSWER_KEYS]

    # Create position indices and shuffle
    indices = list(range(5))
    rng.shuffle(indices)

    # Apply shuffled order
    for new_pos, orig_idx in enumerate(indices):
        shuffled[ANSWER_KEYS[new_pos]] = original_answers[orig_idx]

    # Find where the correct answer (originally at position 0 = A) ended up
    new_correct_pos = indices.index(0)
    shuffled["correct_answer"] = POSITIONS[new_correct_pos]

    # Record the mapping: original position -> new position
    # indices[new_pos] = orig_idx, so we invert to get orig -> new
    mapping = {POSITIONS[orig_idx]: POSITIONS[new_pos]
               for new_pos, orig_idx in enumerate(indices)}
    shuffled["shuffle_mapping"] = mapping

    return shuffled


def shuffle_dataset(data: list, seed: int) -> list:
    """
    Shuffle all questions in a dataset.

    Each question gets its own deterministic shuffle based on seed + question index.
    """
    rng = random.Random(seed)
    return [shuffle_question(item, rng) for item in data]


# ==============================================================================
# File Processing
# ==============================================================================


def process_file(input_path: str, output_path: str, seed: int) -> int:
    """Process a single JSON file: shuffle answers and save."""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    shuffled = shuffle_dataset(data, seed)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(shuffled, f, ensure_ascii=False, indent=2)

    return len(shuffled)


# ==============================================================================
# Main
# ==============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="ITAMed Answer Shuffling Utility"
    )
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--per-year", action="store_true",
                        help="Also generate per-year shuffled files")
    args = parser.parse_args()

    print("=" * 70)
    print("ITAMed — Answer Shuffling Utility")
    print(f"  Seed: {args.seed}")
    print("=" * 70)

    total = 0

    # Process IT complete
    it_complete = os.path.join(IT_JSON_DIR, "ITAMed_complete.json")
    it_complete_out = os.path.join(IT_JSON_DIR, "ITAMed_complete_shuffled.json")
    if os.path.exists(it_complete):
        n = process_file(it_complete, it_complete_out, args.seed)
        print(f"\n  IT complete: {n} questions shuffled → {os.path.basename(it_complete_out)}")
        total += n

    # Process EN complete
    en_complete = os.path.join(EN_JSON_DIR, "ITAMed_complete_EN.json")
    en_complete_out = os.path.join(EN_JSON_DIR, "ITAMed_complete_EN_shuffled.json")
    if os.path.exists(en_complete):
        n = process_file(en_complete, en_complete_out, args.seed)
        print(f"  EN complete: {n} questions shuffled → {os.path.basename(en_complete_out)}")
        total += n

    # Process per-year files if requested
    if args.per_year:
        print("\n  Per-year files:")
        for year in YEARS:
            # IT
            it_year = os.path.join(IT_JSON_DIR, f"ITAMed_{year}.json")
            it_year_out = os.path.join(IT_JSON_DIR, f"ITAMed_{year}_shuffled.json")
            if os.path.exists(it_year):
                n = process_file(it_year, it_year_out, args.seed)
                print(f"    IT {year}: {n} questions")
                total += n

            # EN
            en_year = os.path.join(EN_JSON_DIR, f"ITAMed_{year}_EN.json")
            en_year_out = os.path.join(EN_JSON_DIR, f"ITAMed_{year}_EN_shuffled.json")
            if os.path.exists(en_year):
                n = process_file(en_year, en_year_out, args.seed)
                print(f"    EN {year}: {n} questions")
                total += n

    # Verify shuffle quality
    print(f"\n  Verifying shuffle distribution...")
    with open(it_complete_out, "r", encoding="utf-8") as f:
        shuffled_data = json.load(f)
    from collections import Counter
    pos_counts = Counter(item["correct_answer"] for item in shuffled_data)
    print(f"  Correct answer distribution after shuffle:")
    for pos in POSITIONS:
        count = pos_counts.get(pos, 0)
        pct = count / len(shuffled_data) * 100
        print(f"    {pos}: {count} ({pct:.1f}%)")

    print(f"\n{'='*70}")
    print(f"DONE — {total} questions shuffled (seed={args.seed})")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
