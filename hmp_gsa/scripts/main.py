import os
from pathlib import Path

try:
    from .prior_scan import process_dataset
except ImportError:  
    from hmp_gsa.scripts.prior_scan import process_dataset

if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[2]
    datasets_to_run = {
        "Accidents": repo_root / "datasets" / "accident.txt",
    }

    output_root = repo_root / "hmp_gsa" / "derived"
    for name, path in datasets_to_run.items():
        if path.exists():
            process_dataset(name, str(path), output_root=str(output_root))