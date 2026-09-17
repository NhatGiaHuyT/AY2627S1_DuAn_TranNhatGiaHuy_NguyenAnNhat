import csv
import json
import os
from collections import Counter
from itertools import combinations


def _item_sort_key(value):
    text = str(value)

    if text.startswith("-"):
        return (
            1,
            -int(text),
            text,
        )

    if text.isdigit():
        return (
            0,
            int(text),
            text,
        )

    return (
        2,
        text,
    )


def scan_dataset(
    file_path: str,
):
    """
    Single-pass scan over a transactional dataset.

    This produces raw dataset statistics and the pairwise
    co-occurrence matrix.

    It does NOT decide how those statistics become a GSA
    Feature -> weight prior. That responsibility belongs
    to the concrete HMP adapter.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    total_transactions = 0
    total_items_count = 0

    item_frequency = Counter()
    pair_cooccurrence = Counter()

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            items = set(
                line.split()
            )

            sorted_items = sorted(
                items,
                key=_item_sort_key,
            )

            total_transactions += 1
            total_items_count += len(
                sorted_items
            )

            for item in sorted_items:
                item_frequency[item] += 1

            for item_i, item_j in combinations(
                sorted_items,
                2,
            ):
                pair_cooccurrence[
                    (item_i, item_j)
                ] += 1

    distinct_items = len(
        item_frequency
    )

    atl = (
        total_items_count
        / total_transactions
        if total_transactions
        else 0.0
    )

    density = (
        atl
        / distinct_items
        * 100
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


def save_results(
    results,
    output_dir: str,
) -> None:

    os.makedirs(
        output_dir,
        exist_ok=True,
    )

    statistics = {
        "size_D": results["size_D"],
        "distinct_I": results["distinct_I"],
        "atl": results["atl"],
        "density": results["density"],
        "observed_pairs": len(
            results["pair_cooccurrence"]
        ),
    }

    with open(
        os.path.join(
            output_dir,
            "statistics.json",
        ),
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            statistics,
            file,
            indent=4,
            sort_keys=True,
        )

    with open(
        os.path.join(
            output_dir,
            "item_frequency.csv",
        ),
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "item",
                "frequency",
            ]
        )

        for item, frequency in sorted(
            results["item_frequency"].items(),
            key=lambda pair: _item_sort_key(
                pair[0]
            ),
        ):
            writer.writerow(
                [
                    item,
                    frequency,
                ]
            )

    with open(
        os.path.join(
            output_dir,
            "cooccurrence.csv",
        ),
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "item_i",
                "item_j",
                "cooccurrence",
            ]
        )

        for (item_i, item_j), count in sorted(
            results["pair_cooccurrence"].items(),
            key=lambda pair: (
                _item_sort_key(
                    pair[0][0]
                ),
                _item_sort_key(
                    pair[0][1]
                ),
            ),
        ):
            writer.writerow(
                [
                    item_i,
                    item_j,
                    count,
                ]
            )


def process_dataset(
    name: str,
    file_path: str,
    output_root: str = "derived",
) -> str:

    results = scan_dataset(
        file_path
    )

    dataset_output_dir = os.path.join(
        output_root,
        str(name).lower(),
    )

    save_results(
        results,
        dataset_output_dir,
    )

    print(
        f"Saved results for {name} "
        f"→ {dataset_output_dir}"
    )

    return dataset_output_dir


if __name__ == "__main__":
    process_dataset(
        "Accidents",
        "accident.txt",
        output_root="derived",
    )