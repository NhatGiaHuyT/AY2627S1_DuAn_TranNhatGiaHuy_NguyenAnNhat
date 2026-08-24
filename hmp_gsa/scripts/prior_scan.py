import csv
import json
import os
from collections import Counter
from itertools import combinations

FILE_PATH = 'accident.txt'

def scan_dataset(file_path):
    """
    Single-pass scan over a transactional dataset.

    Returns:
        - number of transactions
        - distinct items
        - average transaction length
        - density
        - item frequencies
        - pairwise co-occurrence counts
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    total_transactions = 0
    total_items_count = 0

    item_frequency = Counter()
    pair_cooccurrence = Counter()

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            # Important: treat a transaction as a SET
            items = set(line.split())

            total_transactions += 1
            total_items_count += len(items)

            # Item support
            for item in items:
                item_frequency[item] += 1

            # Pairwise co-occurrence
            for i, j in combinations(sorted(items), 2):
                pair_cooccurrence[(i, j)] += 1

    distinct_items = len(item_frequency)

    atl = (
        total_items_count / total_transactions
        if total_transactions
        else 0.0
    )

    density = (
        atl / distinct_items * 100
        if distinct_items
        else 0.0
    )

    return {
        "size_D": total_transactions,
        "distinct_I": distinct_items,
        "atl": atl,
        "density": density,
        "item_frequency": item_frequency,
        "pair_cooccurrence": pair_cooccurrence,
    }

def save_results(results, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # -------------------------
    # Dataset statistics
    # -------------------------
    statistics = {
        "size_D": results["size_D"],
        "distinct_I": results["distinct_I"],
        "atl": results["atl"],
        "density": results["density"],
        "observed_pairs": len(results["pair_cooccurrence"]),
    }

    with open(
        os.path.join(output_dir, "statistics.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(statistics, f, indent=4)

    # -------------------------
    # Item frequencies
    # -------------------------
    with open(
        os.path.join(output_dir, "item_frequency.csv"),
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.writer(f)

        writer.writerow(["item", "frequency"])

        for item, frequency in results["item_frequency"].most_common():
            writer.writerow([item, frequency])

    # -------------------------
    # Pair co-occurrences
    # -------------------------
    with open(
        os.path.join(output_dir, "cooccurrence.csv"),
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.writer(f)

        writer.writerow([
            "item_i",
            "item_j",
            "cooccurrence",
        ])

        for (i, j), count in results["pair_cooccurrence"].items():
            writer.writerow([i, j, count])


def process_dataset(name, file_path, output_root="derived"):
    results = scan_dataset(file_path)

    dataset_output_dir = os.path.join(
        output_root,
        name.lower(),
    )

    save_results(
        results,
        dataset_output_dir,
    )

    print(f"Saved results for {name} → {dataset_output_dir}")