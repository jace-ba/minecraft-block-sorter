#!/usr/bin/env python3
"""Build step for the Redstone Block Index.

Single source of truth: ``data/blocks.csv``.

This reads that CSV and injects it (as the ``const DATA = [...]`` JavaScript
array) into ``Redstone_Block_Index.html``. Edit the CSV, run this script, and
the app is updated. Nothing else needs to touch the block data by hand.

Usage:
    python scripts/build.py
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "blocks.csv"
HTML_PATH = ROOT / "Redstone_Block_Index.html"

# Column name -> type. Anything not listed is treated as a string.
# `piston` is a categorical string column: "Movable" | "Immovable" | "Breaks".
BOOL_COLS = {
    "breaks_water", "stable", "spawn_hostile",
    "spawn_friendly", "solid", "conductive", "falls", "flammable",
}
INT_COLS = {"height", "width"}

# Order the keys are emitted in (purely cosmetic, keeps diffs stable).
KEY_ORDER = [
    "name", "category", "piston", "breaks_water", "stable",
    "spawn_hostile", "spawn_friendly", "solid", "conductive", "height",
    "height_note", "width", "width_note", "falls", "flammable", "notes", "id",
]


def parse_bool(value, col, line):
    v = (value or "").strip().lower()
    if v in ("true", "1", "yes", "y"):
        return True
    if v in ("false", "0", "no", "n", ""):
        return False
    raise ValueError(f"Row {line}: column '{col}' expected TRUE/FALSE, got {value!r}")


def parse_int(value, col, line):
    v = (value or "").strip()
    if v == "":
        return 0
    try:
        return int(float(v))
    except ValueError:
        raise ValueError(f"Row {line}: column '{col}' expected a number, got {value!r}")


def load_rows():
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [k for k in KEY_ORDER if k not in reader.fieldnames]
        if missing:
            raise SystemExit(f"CSV is missing required columns: {missing}")

        rows = []
        ids = set()
        for i, raw in enumerate(reader, start=2):  # line 1 is the header
            row = {}
            for col in KEY_ORDER:
                val = raw.get(col, "")
                if col in BOOL_COLS:
                    row[col] = parse_bool(val, col, i)
                elif col in INT_COLS:
                    row[col] = parse_int(val, col, i)
                else:
                    row[col] = (val or "").strip()
            if not row["id"]:
                raise SystemExit(f"Row {i}: empty id (name={row['name']!r})")
            if row["id"] in ids:
                raise SystemExit(f"Row {i}: duplicate id {row['id']!r}")
            ids.add(row["id"])
            rows.append(row)
    return rows


def main():
    if not CSV_PATH.exists():
        raise SystemExit(f"Source CSV not found: {CSV_PATH}")
    if not HTML_PATH.exists():
        raise SystemExit(f"App HTML not found: {HTML_PATH}")

    rows = load_rows()
    data_js = "const DATA = " + json.dumps(rows, ensure_ascii=True) + ";"

    html = HTML_PATH.read_text(encoding="utf-8")
    pattern = re.compile(r"const DATA = \[.*?\];", re.S)
    if not pattern.search(html):
        raise SystemExit("Could not find `const DATA = [...]` in the HTML.")
    new_html = pattern.sub(lambda _m: data_js, html, count=1)
    HTML_PATH.write_text(new_html, encoding="utf-8")

    print(f"Built {HTML_PATH.name} from {CSV_PATH.name}: {len(rows)} blocks.")


if __name__ == "__main__":
    sys.exit(main())
