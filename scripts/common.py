import csv
import os
import re
import sys

DEFAULT_PBF = "data/ocp1.osm.pbf"
OUTPUT_DIR = "output"

NUMBER = re.compile(r"^\s*(\d+(?:[.,]\d+)?)\s*(m|meter|metre|meters|metres)?\s*$", re.IGNORECASE)


def get_path():
    return sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PBF


def write_csv(filename, header, rows):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    return path


def parse_number(text):
    if text is None:
        return ""
    match = NUMBER.match(text)
    if not match:
        return ""
    return float(match.group(1).replace(",", "."))
