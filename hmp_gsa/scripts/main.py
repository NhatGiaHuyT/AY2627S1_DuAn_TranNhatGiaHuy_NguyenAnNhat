import os

from prior_scan import process_dataset

if __name__ == "__main__":

    datasets_to_run = {
        "Accidents": "../datasets/accident.txt",
    }

    for name, path in datasets_to_run.items():
        if os.path.exists(path):
            process_dataset(name, path)