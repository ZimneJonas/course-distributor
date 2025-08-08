#!/usr/bin/env python3
import argparse
import csv
import os
import re
import sys
import unicodedata
from typing import Dict, List, Tuple


def transliterate_german_characters(text: str) -> str:
    mapping = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
    }
    for src, dst in mapping.items():
        text = text.replace(src, dst).replace(src.upper(), dst)
    return text


def normalize_atom(base: str, *, prefix_if_starts_with_digit: str) -> str:
    if base is None:
        base = ""
    # Lowercase and strip
    text = base.strip().lower()
    # Transliterate common German characters first (pre-ASCII fold)
    text = transliterate_german_characters(text)
    # Remove accents/diacritics
    text = (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    # Replace all non [a-z0-9_] with underscore
    text = re.sub(r"[^a-z0-9_]", "_", text)
    # Collapse multiple underscores
    text = re.sub(r"_+", "_", text)
    # Trim underscores from ends
    text = text.strip("_")
    # Ensure not empty
    if not text:
        text = "x"
    # Ensure it doesn't start with a digit
    if re.match(r"^[0-9]", text):
        text = f"{prefix_if_starts_with_digit}{text}"
    return text


def parse_csv_preferences(csv_path: str) -> Tuple[List[str], List[Tuple[str, Dict[str, int]]]]:
    # Returns (courses, list of (student_atom, {course_atom: rank}))
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        rows = list(reader)
    if not rows:
        raise ValueError("CSV file is empty")

    header = rows[0]
    if len(header) < 2:
        raise ValueError("CSV must have at least one course column")

    print(header)
    # First cell is expected empty or a label for students
    raw_course_names = header[1:]
    course_atoms = [normalize_atom(name, prefix_if_starts_with_digit="c_") for name in raw_course_names]
    print(course_atoms)
    students: List[Tuple[str, Dict[str, int]]] = []
    for row in rows[1:]:
        if not row:
            continue
        # Pad row to length of header to avoid index errors
        if len(row) < len(header):
            row = row + [""] * (len(header) - len(row))

        raw_name = row[0]
        if not raw_name or not raw_name.strip():
            continue
        student_atom = normalize_atom(raw_name, prefix_if_starts_with_digit="s_")

        preferences: Dict[str, int] = {}
        for idx, raw_value in enumerate(row[1:]):
            course_atom = course_atoms[idx]
            value = (raw_value or "").strip()
            if not value:
                continue
            try:
                rank = int(value)
            except ValueError:
                # Skip non-integers silently
                continue
            preferences[course_atom] = rank

        students.append((student_atom, preferences))

    return course_atoms, students


def generate_asp_facts(courses: List[str], students: List[Tuple[str, Dict[str, int]]]) -> List[str]:
    lines: List[str] = []
    lines.append('#include "model.lp".')
    lines.append("")

    # Emit unique course facts
    unique_courses = []
    seen = set()
    for c in courses:
        if c not in seen and c:
            seen.add(c)
            unique_courses.append(c)

    for c in unique_courses:
        lines.append(f"course({c}).")

    lines.append("")

    # Emit student and preference facts
    for student_atom, prefs in students:
        lines.append(f"student({student_atom}).")
    lines.append("")

    for student_atom, prefs in students:
        for course_atom, rank in prefs.items():
            lines.append(f"preference({student_atom}, {course_atom}, {rank}).")

    return lines


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Translate a CSV of student preferences into ASP facts like example.lp",
    )
    parser.add_argument(
        "csv",
        nargs="?",
        default=os.path.join(os.path.dirname(__file__), "students.csv"),
        help="Path to input CSV (default: examples/students.csv)",
    )
    parser.add_argument(
        "-o",
        "--out",
        default=os.path.join(os.path.dirname(__file__),"students.lp"),
        help="Output file path (default: stdout)",
    )
    args = parser.parse_args(argv)

    courses, students = parse_csv_preferences(args.csv)
    lines = generate_asp_facts(courses, students)

    output = "\n".join(lines) + "\n"
    if args.out == "-":
        sys.stdout.write(output)
    else:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


