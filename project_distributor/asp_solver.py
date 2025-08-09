"""
ASP (clingo) backend for the course assignment solver.

This module runs clingo on the provided ASP model (`model.lp`) together with
facts generated either from a CSV file or provided as a .lp facts file.

Notes/Limitations:
- Settings like `courses_per_student/1` are currently taken from `model.lp`.
  Overrides from CLI/UI are not applied for the ASP backend.
"""

from __future__ import annotations

import argparse
import io
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:  # When imported as part of the package
    from .csv_parser import parse_csv_preferences
except Exception:  # When executed directly as a script
    from csv_parser import parse_csv_preferences


def _ensure_clingo_available() -> Tuple[bool, str]:
    if shutil.which("clingo") is None:
        return False, (
            "clingo executable not found. Install clingo (e.g., brew install clingo) "
            "and ensure it is on your PATH."
        )
    return True, ""


def _model_path() -> Path:
    return Path(__file__).resolve().parent / "model.lp"


def _generate_facts_from_csv(csv_path: str) -> str:
    courses, students = parse_csv_preferences(csv_path)
    lines: List[str] = []
    for student_atom, prefs in students:
        for course_atom, rank in prefs.items():
            lines.append(f"preference({student_atom}, {course_atom}, {rank}).")
    return "\n".join(lines) + "\n"


def _run_clingo(files: List[Path], time_limit_seconds: int) -> Tuple[bool, str]:
    ok, msg = _ensure_clingo_available()
    if not ok:
        return False, msg + "\n"

    cmd = [
        "clingo",
        *[str(p) for p in files],
        "--time-limit",
        str(time_limit_seconds),
    ]
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    except Exception as exc:
        return False, f"Failed to run clingo: {exc}\n"

    output = proc.stdout or ""
    # clingo/clasp convention: 10 = SAT, 20 = UNSAT, 30 = UNKNOWN
    success = proc.returncode == 10
    return success, output


def _extract_last_answer_atoms(output: str) -> Optional[str]:
    """Extract the atom line(s) from the last Answer block in clingo output.

    Returns a single whitespace-separated string of atoms or None if not found.
    """
    lines = (output or "").splitlines()
    last_answer_idx = None
    for i, line in enumerate(lines):
        if line.startswith("Answer:"):
            last_answer_idx = i
    if last_answer_idx is None:
        return None

    # Collect subsequent lines until a status/summary line
    acc: List[str] = []
    for line in lines[last_answer_idx + 1 :]:
        if (
            line.startswith("Optimization:")
            or line.startswith("OPTIMUM")
            or line.startswith("SATISFIABLE")
            or line.startswith("UNSATISFIABLE")
            or line.startswith("UNKNOWN")
        ):
            break
        if not line.strip():
            continue
        acc.append(line.strip())
    if not acc:
        return None
    return " ".join(acc)


def _ordinal(n: int) -> str:
    if 10 <= (n % 100) <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _format_sorted_output(raw_output: str) -> str:
    atoms_line = _extract_last_answer_atoms(raw_output)
    if not atoms_line:
        return raw_output

    import re

    res_matches = re.findall(r"res\(([^,]+),([^,]+),(\d+)\)", atoms_line)
    count_matches = re.findall(r"count\(([^,]+),(\d+)\)", atoms_line)
    quality_matches = re.findall(r"quality\(rank\((\d+)\),amount\((\d+)\)\)", atoms_line)

    # Build structures
    course_to_students: Dict[str, List[Tuple[str, int]]] = {}
    for s, c, r in res_matches:
        try:
            r_int = int(r)
        except ValueError:
            continue
        course_to_students.setdefault(c, []).append((s, r_int))

    course_counts: Dict[str, int] = {c: int(n) for c, n in count_matches}
    quality: Dict[int, int] = {int(r): int(n) for r, n in quality_matches}

    # Sort
    sorted_courses = sorted(set(list(course_to_students.keys()) + list(course_counts.keys())))

    lines: List[str] = []
    lines.append("=== SOLUTION (ASP) ===")
    for course in sorted_courses:
        entries = course_to_students.get(course, [])
        if not entries:
            continue
        entries.sort(key=lambda x: (x[1], x[0]))  # by rank then student
        parts = [f"  {s} ({_ordinal(r)} choice)" for s, r in entries]
        lines.append(f"{course}:\n" + "\n".join(parts) + "\n")

    if course_counts:
        lines.append("=== COURSE COUNTS ===")
        for course in sorted_courses:
            if course in course_counts:
                lines.append(f"{course_counts[course]} got assigned to {course}.")

    if quality:
        lines.append("=== QUALITY STATISTICS ===")
        for rank in sorted(quality.keys()):
            lines.append(f"{quality[rank]} got their {_ordinal(rank)} choice.")

    # Append a brief footer to indicate formatting
    lines.append("\n(note: output sorted and formatted from clingo answer)")
    return "\n".join(lines) + "\n"


def solve_csv_file(
    csv_path: str,
    *,
    time_limit_seconds: int = 30,
) -> Tuple[bool, str]:
    """Solve a CSV input using ASP and return (success, textual_output)."""
    model = _model_path()
    if not model.exists():
        return False, f"Model not found at {model}\n"

    facts_text = _generate_facts_from_csv(csv_path)
    with tempfile.TemporaryDirectory() as tmpdir:
        facts_path = Path(tmpdir) / "facts.lp"
        facts_path.write_text(facts_text, encoding="utf-8")
        success, output = _run_clingo([model, facts_path], time_limit_seconds)
        if success:
            return True, _format_sorted_output(output)
        return success, output


def solve_lp_file(
    lp_path: str,
    *,
    time_limit_seconds: int = 30,
) -> Tuple[bool, str]:
    """Solve an .lp file. If it doesn't include the model, we pass model.lp too."""
    model = _model_path()
    user_lp = Path(lp_path)
    if not user_lp.exists():
        return False, f"Input file not found: {lp_path}\n"

    # If the lp already includes model.lp via #include, clingo will ignore duplicates.
    success, output = _run_clingo([model, user_lp], time_limit_seconds)
    if success:
        return True, _format_sorted_output(output)
    return success, output


def main():
    parser = argparse.ArgumentParser(
        description="Solve course assignment problem using ASP (clingo)",
    )
    parser.add_argument("input", help="Input file (.lp facts or .csv)")
    parser.add_argument(
        "--time-limit",
        type=int,
        default=30,
        help="Time limit in seconds (default: 30)",
    )

    args = parser.parse_args()

    success: bool
    output: str
    if args.input.endswith(".csv"):
        success, output = solve_csv_file(args.input, time_limit_seconds=args.time_limit)
    else:
        success, output = solve_lp_file(args.input, time_limit_seconds=args.time_limit)

    print(output)
    if not success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()


