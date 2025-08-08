"""
CSV parsing utilities for course assignment problems.

This module provides functions to parse CSV files containing student course preferences
and normalize the data for use in the assignment solver.
"""

import csv
import re
import unicodedata
from typing import Dict, List, Tuple


def transliterate_german_characters(text: str) -> str:
    """Transliterate German umlauts and sharp S to ASCII equivalents.
    
    Args:
        text: Input text that may contain German characters
        
    Returns:
        Text with German characters replaced by ASCII equivalents
    """
    mapping = {
        "ä": "ae",
        "ö": "oe", 
        "ü": "ue",
        "ß": "ss",
    }
    for src, dst in mapping.items():
        text = text.replace(src, dst).replace(src.upper(), dst.upper())
    return text


def normalize_atom(base: str, *, prefix_if_starts_with_digit: str) -> str:
    """Normalize text to a valid atom name for logical programming.
    
    Args:
        base: Base text to normalize
        prefix_if_starts_with_digit: Prefix to add if text starts with a digit
        
    Returns:
        Normalized atom name safe for logical programming
    """
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
    """Parse a CSV file containing student course preferences.
    
    The CSV should have the following format:
    - First row: course names (first cell can be empty or a label)
    - Subsequent rows: student names in first column, preference ranks in other columns
    - Preference ranks should be integers (1 = best, higher = worse)
    - Empty cells or non-integer values are ignored
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        Tuple of (course_atoms, students) where:
        - course_atoms: List of normalized course names
        - students: List of (student_atom, {course_atom: rank}) tuples
        
    Raises:
        ValueError: If CSV is empty or has no valid course columns
        FileNotFoundError: If CSV file doesn't exist
    """
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        # Detect delimiter from the first non-empty line, support ";", "," and tabs
        first_line = ""
        while True:
            pos = f.tell()
            line = f.readline()
            if line == "":
                break
            if line.strip():
                first_line = line
                break
        
        delimiter = ";"
        if "," in first_line and first_line.count(",") > first_line.count(";"):
            delimiter = ","
        elif "\t" in first_line and first_line.count("\t") >= max(first_line.count(";"), first_line.count(",")):
            delimiter = "\t"
        
        # Rewind and parse with detected delimiter
        f.seek(0)
        reader = csv.reader(f, delimiter=delimiter)
        rows = list(reader)

    if not rows:
        raise ValueError("CSV file is empty")

    header = rows[0]
    # First cell is expected empty or a label for students; ensure we have at least one non-empty course column
    raw_course_names = [name.strip() for name in header[1:]]
    if not any(raw_course_names):
        raise ValueError("CSV must have at least one course column")

    course_atoms = [
        normalize_atom(name, prefix_if_starts_with_digit="c_")
        for name in raw_course_names
        if name
    ]

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
        # Iterate only over declared course columns
        for course_atom, raw_value in zip(course_atoms, row[1:]):
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
