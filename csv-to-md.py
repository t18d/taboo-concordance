#!/usr/bin/env python3

# © 2025. This program is free software: you can
# redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You may obtain a copy of the License at
#
#     https://www.gnu.org/licenses/gpl-3.0.txt

import csv
import os
from datetime import datetime, timezone

MARKER = "<!-- Anything"  # stop copying preface after this line
LAST_MODIFIED_KEY = "last_modified_at:"
CSV_PATH = "concordance.csv"
MD_PATH = "README.md"

def escape_markdown_cell(cell: str) -> str:
    """Escape pipes in markdown table cells."""
    return cell.replace("|", "\\|")

def update_last_modified(lines: list, filename: str) -> list:
    """Update last_modified_at line; error if not found."""
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    found_key = False
    updated_lines = []
    for line in lines:
        if line.strip().startswith(LAST_MODIFIED_KEY):
            updated_lines.append(f"{LAST_MODIFIED_KEY} {timestamp}\n")
            found_key = True
        else:
            updated_lines.append(line)
    if not found_key:
        raise RuntimeError(f"'{LAST_MODIFIED_KEY}' not found in {filename}")
    return updated_lines

def parse_and_validate_csv(csv_path: str):
    """
    Parse CSV once, validating RFC4180-like rules.
    Returns list of rows if valid, raises RuntimeError otherwise.
    """
    rows = []
    try:
        with open(csv_path, "r", encoding="utf8", newline="") as f:
            reader = csv.reader(f, strict=True)
            expected_len = None
            for i, row in enumerate(reader, start=1):
                if expected_len is None:
                    expected_len = len(row)
                elif len(row) != expected_len:
                    raise RuntimeError(
                        f"Row {i} in {csv_path} has {len(row)} fields; expected {expected_len}"
                    )
                rows.append(row)
    except csv.Error as e:
        raise RuntimeError(f"CSV parsing error in {csv_path}: {e}")
    return rows

def main():
    if not os.path.exists(MD_PATH):
        raise RuntimeError(f"Markdown file {MD_PATH} does not exist")

    # Read preface up to marker
    preface_lines = []
    marker_found = False
    with open(MD_PATH, "r", encoding="utf8") as md_file:
        for line in md_file:
            preface_lines.append(line)
            if MARKER in line:
                marker_found = True
                break
    if not marker_found:
        raise RuntimeError(f"Marker '{MARKER}' not found in {MD_PATH}")

    # Validate and parse CSV in one pass
    rows = parse_and_validate_csv(CSV_PATH)

    # Build markdown table
    table_lines = []
    if rows:
        header = [escape_markdown_cell(cell) for cell in rows[0]]
        table_lines.append("|".join(header) + "|\n")
        table_lines.append("|".join("---" for _ in header) + "|\n")
        for row in rows[1:]:
            escaped_row = [escape_markdown_cell(cell) for cell in row]
            table_lines.append("|".join(escaped_row) + "|\n")

    # Update last_modified_at in preface
    preface_lines = update_last_modified(preface_lines, MD_PATH)

    # Write final markdown
    with open(MD_PATH, "w", encoding="utf8") as md_file:
        md_file.writelines(preface_lines)
        md_file.write("\n")
        md_file.writelines(table_lines)

    print(f"Updated {MD_PATH} with table from {CSV_PATH}.")

if __name__ == "__main__":
    main()
