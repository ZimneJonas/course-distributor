# Project Distributor

Assign students to courses based on preferences using either Google OR-Tools CP-SAT or ASP (clingo).

## Quickstart (CLI)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# OR-Tools backend (default)
python -m project_distributor solve examples/students.csv

# ASP backend (requires clingo in PATH)
python -m project_distributor solve -b asp examples/students.csv
```

ASP can alternatively can be run directly ```clingo examples/students.lp```

## Web UI (Streamlit)

Run locally:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open the provided local URL. Upload a CSV like `examples/students.csv`.

## Deploy

Pushes to `main` trigger `.github/workflows/docker.yml`, which builds `linux/amd64` and pushes `zimne/course-distributor:latest` (plus a `sha-<short>` tag) to Docker Hub. Requires repo secrets `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`.

Manual build:

```bash
docker buildx build --platform linux/amd64 -t zimne/course-distributor:latest .
docker push zimne/course-distributor:latest
```

## CSV Format

The first row lists course names; each subsequent row lists a student name in the first column and preference ranks in following columns. See `examples/students.csv`.

## Library/API

The OR-Tools solver exposes a helper function for programmatic use:

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

For ASP backend, you can call:

```python
from project_distributor.asp_solver import solve_csv_file

success, output = solve_csv_file(
    "examples/students.csv",
    time_limit_seconds=30,
)
print(output)
```


