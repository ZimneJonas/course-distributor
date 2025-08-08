#!/bin/bash
python examples/generate_students.py 100
python examples/csv_to_lp.py

clingo examples/students.lp


echo "=== Testing OR-Tools solver ==="

# Convert CSV to OR-Tools compatible format and solve
echo "Solving with OR-Tools..."
python project_distributor/ortools_solver.py examples/students.csv
