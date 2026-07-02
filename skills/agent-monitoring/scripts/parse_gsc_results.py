#!/usr/bin/env python3
"""Parse GSC tool output files (JSON wrapped in [{type, text}]) into CSV."""
from __future__ import annotations
import json
import csv
import sys
from pathlib import Path


def parse_gsc_file(input_path: Path, output_path: Path) -> int:
    raw = input_path.read_text(encoding="utf-8")
    outer = json.loads(raw)
    if isinstance(outer, list) and outer and "text" in outer[0]:
        payload = json.loads(outer[0]["text"])
    else:
        payload = outer

    rows = payload.get("rows", [])
    if not rows:
        print(f"WARN: no rows in {input_path}")
        return 0

    fieldnames = list(rows[0].keys())
    with output_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return len(rows)


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: parse_gsc_results.py <input.txt> <output.csv>")
        sys.exit(1)
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    n = parse_gsc_file(input_path, output_path)
    print(f"OK: {n} rows -> {output_path}")


if __name__ == "__main__":
    main()
