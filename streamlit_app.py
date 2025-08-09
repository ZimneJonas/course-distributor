import tempfile
from pathlib import Path

import streamlit as st

from project_distributor.ortools_solver import solve_csv_file


st.set_page_config(page_title="Project Distributor", page_icon="📊", layout="centered")
st.title("Project Distributor (OR-Tools)")
st.write(
    "Upload a CSV like `examples/students.csv`. The app will run the OR-Tools solver "
    "on your data in the cloud session and show the textual results."
)


uploaded = st.file_uploader("CSV with student preferences", type=["csv"]) 

with st.expander("Solver settings"):
    time_limit = st.number_input("Time limit (seconds)", min_value=1, max_value=300, value=30)
    courses_per_student = st.number_input("Courses per student", min_value=1, value=1)
    min_students_per_course = st.number_input("Min students per course", min_value=0, value=10)
    max_students_per_course = st.number_input("Max students per course", min_value=1, value=30)
    hard_pref = st.checkbox("Hard enforce preferences (disallow no-preference assignments)", value=False)


if st.button("Run solver", type="primary"):
    if not uploaded:
        st.warning("Please upload a CSV file first.")
        st.stop()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_csv = Path(tmpdir) / "input.csv"
        tmp_csv.write_bytes(uploaded.getvalue())

        with st.spinner("Solving..."):
            success, output = solve_csv_file(
                str(tmp_csv),
                time_limit_seconds=int(time_limit),
                courses_per_student=int(courses_per_student),
                max_students_per_course=int(max_students_per_course),
                min_students_per_course=int(min_students_per_course),
                hard_enforced_preference=bool(hard_pref),
            )

        st.subheader("Solver output")
        st.code(output or "(no output)", language="text")

        if not success:
            st.error("No feasible solution or solver failed. See output above.")


st.markdown(
    """
    Notes:
    - The CSV is processed locally in this session and not persisted.
    - See `examples/students.csv` for the expected format.
    """
)


