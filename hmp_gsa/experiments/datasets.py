from __future__ import annotations

from pathlib import Path


def load_transactions(path: str | Path) -> tuple[tuple[str, ...], ...]:
    """Load a whitespace-separated transaction database without synthetic data."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)

    transactions = []
    with source.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            items = tuple(dict.fromkeys(line.split()))
            if items:
                transactions.append(items)
            elif line.strip():
                raise ValueError(f"Empty transaction at {source}:{line_number}")

    if not transactions:
        raise ValueError(f"Dataset contains no transactions: {source}")
    return tuple(transactions)


def resolve_dataset_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path
