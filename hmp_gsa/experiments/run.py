import argparse
import json
from .runner import run

parser = argparse.ArgumentParser()
parser.add_argument("--config", default="configs/baseline.json")
args = parser.parse_args()

with open(args.config, encoding="utf-8") as f:
    config = json.load(f)

print("Experiment output:", run(config))
