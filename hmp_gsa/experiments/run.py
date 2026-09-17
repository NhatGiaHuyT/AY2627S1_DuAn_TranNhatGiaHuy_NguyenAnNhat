import argparse
import json

from .runner import run


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        default="configs/baseline.json",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=None,
    )

    args = parser.parse_args()

    with open(
        args.config,
        "r",
        encoding="utf-8",
    ) as file:
        config = json.load(file)

    results = run(
        config,
        max_workers=args.workers,
    )

    print(
        f"\nCompleted {len(results)} experiments."
    )


if __name__ == "__main__":
    main()