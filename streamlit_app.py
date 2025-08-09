import tempfile
from pathlib import Path

import streamlit as st

from project_distributor.ortools_solver import solve_csv_file as solve_csv_ortools
from project_distributor.asp_solver import solve_csv_file as solve_csv_asp
from examples.generate_students import (
    generate_students,
    generate_students_csv_content,
)


# Basic page configuration (static title to keep set_page_config at the top)
st.set_page_config(page_title="Project Distributor", page_icon="📊", layout="centered")


# Localization dictionary
TEXTS = {
    "en": {
        "title": "Project Distributor",
        "desc": (
            "Upload a CSV like `examples/students.csv`. The app will run the solver "
            "on your data in the cloud session and show the textual results."
        ),
        "lang_label": "Language / Sprache",
        "file_uploader": "CSV with student preferences",
        "expander": "Solver settings",
        "backend": "Backend",
        "time_limit": "Time limit (seconds)",
        "courses_per_student": "Courses per student",
        "min_students": "Min students per course",
        "max_students": "Max students per course",
        "hard_pref": "Hard enforce preferences (disallow no-preference assignments)",
        "run_solver": "Run solver",
        "upload_warning": "Please upload a CSV file first.",
        "solving": "Solving...",
        "solver_output": "Solver output",
        "no_output": "(no output)",
        "error_no_solution": "No feasible solution or solver failed. See output below.",
        "notes_title": "Notes:",
        "note_processing_local": "- The CSV is processed locally in this session and not persisted.",
        "note_example_format": "- See `examples/students.csv` for the expected format.",
        # New example helpers
        "example_label": "Example file:",
        "open_example": "Open example (preview)",
        "download_example": "Download example CSV",
    },
    "de": {
        "title": "Projektverteiler",
        "desc": (
            "Laden Sie eine CSV wie `examples/students.csv` hoch. Die App führt den "
            "Solver in dieser Cloud-Session aus und zeigt die textuellen Ergebnisse an."
        ),
        "lang_label": "Language / Sprache",
        "file_uploader": "CSV mit Studierendenpräferenzen",
        "expander": "Solver-Einstellungen",
        "backend": "Backend",
        "time_limit": "Zeitlimit (Sekunden)",
        "courses_per_student": "Kurse pro Studierendem",
        "min_students": "Min. Studierende pro Kurs",
        "max_students": "Max. Studierende pro Kurs",
        "hard_pref": "Präferenzen strikt erzwingen (keine Zuweisungen ohne Präferenz)",
        "run_solver": "Solver starten",
        "upload_warning": "Bitte laden Sie zuerst eine CSV-Datei hoch.",
        "solving": "Lösen...",
        "solver_output": "Solver-Ausgabe",
        "no_output": "(keine Ausgabe)",
        "error_no_solution": "Keine zulässige Lösung oder Solver-Fehler. Siehe Ausgabe unten.",
        "notes_title": "Hinweise:",
        "note_processing_local": "- Die CSV wird lokal in dieser Session verarbeitet und nicht gespeichert.",
        "note_example_format": "- Siehe `examples/students.csv` für das erwartete Format.",
        # New example helpers
        "example_label": "Beispieldatei:",
        "open_example": "Beispiel öffnen (Vorschau)",
        "download_example": "Beispiel-CSV herunterladen",
    },
}


# Language selector at the top (with flags)
default_lang_key = st.session_state.get("lang", "en")
label_text = TEXTS[default_lang_key]["lang_label"]
options = ["en", "de"]
labels = {"en": "🇬🇧", "de": "🇩🇪"}

col_spacer, col_lang = st.columns([4, 1])
lang_choice = col_lang.segmented_control(
    label_text,
    options=options,
    default=default_lang_key,
    format_func=lambda code: labels.get(code, code),
    label_visibility="collapsed",
)
lang = lang_choice
st.session_state["lang"] = lang
t = TEXTS[lang]


st.title(t["title"])
st.write(t["desc"])


uploaded = st.file_uploader(t["file_uploader"], type=["csv"]) 

with st.expander(t["expander"]):
    time_limit = st.number_input(t["time_limit"], min_value=1, max_value=300, value=10)
    courses_per_student = st.number_input(t["courses_per_student"], min_value=1, value=1)
    min_students_per_course = st.number_input(t["min_students"], min_value=0, value=10)
    max_students_per_course = st.number_input(t["max_students"], min_value=1, value=30)
    hard_pref = st.checkbox(t["hard_pref"], value=False)
    backend = st.selectbox(t["backend"], ["OR-Tools", "ASP (clingo)"])


if st.button(t["run_solver"], type="primary"):
    if not uploaded:
        st.warning(t["upload_warning"])
        st.stop()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_csv = Path(tmpdir) / "input.csv"
        tmp_csv.write_bytes(uploaded.getvalue())

        with st.spinner(t["solving"]):
            if backend.startswith("OR-Tools"):
                success, output = solve_csv_ortools(
                    str(tmp_csv),
                    time_limit_seconds=int(time_limit),
                    courses_per_student=int(courses_per_student),
                    max_students_per_course=int(max_students_per_course),
                    min_students_per_course=int(min_students_per_course),
                    hard_enforced_preference=bool(hard_pref),
                )
            else:
                # ASP backend currently ignores overrides; uses defaults in model.lp
                success, output = solve_csv_asp(
                    str(tmp_csv),
                    time_limit_seconds=int(time_limit),
                )

        st.subheader(t["solver_output"])
        if not success:
            st.error(t["error_no_solution"])
        st.code(output or t["no_output"], language="text")



st.markdown(f"""
{t['notes_title']}
{t['note_processing_local']}
{t['note_example_format']}
""")

# Inline example: preview + download
EXAMPLE_CSV_PATH = Path(__file__).resolve().parent / "examples" / "students.csv"

# Prefer in-memory content if a refreshed sample was generated
example_bytes = st.session_state.get("example_csv_bytes")
example_text = st.session_state.get("example_csv_text")

if example_bytes is None:
    if EXAMPLE_CSV_PATH.exists():
        example_bytes = EXAMPLE_CSV_PATH.read_bytes()

if example_text is None and example_bytes is not None:
    try:
        example_text = example_bytes.decode("utf-8")
    except Exception:
        example_text = EXAMPLE_CSV_PATH.read_text(errors="replace") if EXAMPLE_CSV_PATH.exists() else ""

if example_text:
    st.caption(t.get("example_label", "Example:"))
    with st.popover(t.get("open_example", "Open example (preview)")):
        st.code(example_text, language="csv")
        # Controls row: download (left), spacer, sample size with inline refresh (right)
        col_dl, _spacer, col_controls = st.columns([2, 1, 2])
        with col_dl:
            st.download_button(
                t.get("download_example", "Download example CSV"),
                data=(example_bytes or example_text.encode("utf-8")),
                file_name="students.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col_controls:
            num_col, btn_col = st.columns([5, 1.5])
            with num_col:
                sample_size = st.number_input(
                    "Sample size",
                    min_value=10,
                    max_value=5000,
                    step=10,
                    value=int(st.session_state.get("example_rows", 59)),
                    help="Number of rows to generate for the example CSV.",
                    label_visibility="collapsed",
                )
                if st.session_state.get("example_rows") != int(sample_size):
                    st.session_state["example_rows"] = int(sample_size)
                    st.rerun()

            with btn_col:
                # refresh examples (in-memory only; do not overwrite file)
                if st.button("🔄", type="secondary", use_container_width=True):
                    text = generate_students_csv_content(int(st.session_state.get("example_rows", 100)))
                    st.session_state["example_csv_text"] = text
                    st.session_state["example_csv_bytes"] = text.encode("utf-8")
                    st.rerun()
     
        # refresh streamlit app
        