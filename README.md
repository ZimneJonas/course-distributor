# Project Distributor

Assign students to courses based on preferences using Google OR-Tools CP-SAT.

## Quickstart (CLI)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python project_distributor/ortools_solver.py examples/students.csv
```

## Web UI (Streamlit)

Run locally:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the provided local URL. Upload a CSV like `examples/students.csv`.

## CSV Format

The first row lists course names; each subsequent row lists a student name in the first column and preference ranks in following columns. See `examples/students.csv`.

## Library/API

The solver exposes a helper function for programmatic use:

```python
from project_distributor.ortools_solver import solve_csv_file

success, output = solve_csv_file(
    "examples/students.csv",
    time_limit_seconds=30,
    courses_per_student=1,
    min_students_per_course=10,
    max_students_per_course=30,
    hard_enforced_preference=False,
)
print(output)
```


