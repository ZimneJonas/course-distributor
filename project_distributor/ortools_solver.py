"""
OR-Tools CP-SAT alternative to the ASP course assignment solver.

This solver implements the same constraints and optimization as model.lp:
- Each student gets exactly K courses (courses_per_student)
- Each course has min/max student limits
- Minimize preference penalties (lower rank = better)
- Handle students without preferences with penalty
"""

import argparse
import re
import sys
import time
from typing import Dict, List, Tuple, Optional
from ortools.sat.python import cp_model

from csv_parser import parse_csv_preferences


class CourseAssignmentSolver:
    """Course assignment solver using Google OR-Tools CP-SAT."""
    
    def __init__(self):
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        
        # Problem data
        self.students = []
        self.courses = []
        self.preferences = {}  # (student, course) -> rank
        
        # Configuration (matching model.lp defaults)
        self.courses_per_student = 1
        self.max_students_per_course = 30
        self.min_students_per_course = 10
        self.hard_enforced_preference = False
        self.out_of_preference_penalty = 20
        
        # Decision variables
        self.assignments = {}  # (student, course) -> BoolVar
        
    def load_from_lp_facts(self, facts_content: str):
        """Load problem data from ASP facts format"""
        lines = facts_content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('%') or line.startswith('#'):
                continue
                
            # Parse configuration
            if line.startswith('courses_per_student('):
                self.courses_per_student = int(re.search(r'\((\d+)\)', line).group(1))
            elif line.startswith('max_student_per_course('):
                self.max_students_per_course = int(re.search(r'\((\d+)\)', line).group(1))
            elif line.startswith('min_student_per_course('):
                self.min_students_per_course = int(re.search(r'\((\d+)\)', line).group(1))
            elif line.startswith('hard_enforced_preference('):
                self.hard_enforced_preference = 'true' in line
            
            # Parse facts
            elif line.startswith('course('):
                course = re.search(r'course\(([^)]+)\)', line).group(1)
                if course not in self.courses:
                    self.courses.append(course)
            elif line.startswith('student('):
                student = re.search(r'student\(([^)]+)\)', line).group(1)
                if student not in self.students:
                    self.students.append(student)
            elif line.startswith('preference('):
                match = re.search(r'preference\(([^,]+),\s*([^,]+),\s*(\d+)\)', line)
                if match:
                    student, course, rank = match.groups()
                    self.preferences[(student.strip(), course.strip())] = int(rank)
    
    def load_from_csv(self, csv_path: str):
        """Load problem data from CSV format using the shared parser"""
        courses, students = parse_csv_preferences(csv_path)
        
        self.courses = courses
        self.students = []
        self.preferences = {}
        
        for student_atom, prefs in students:
            self.students.append(student_atom)
            for course_atom, rank in prefs.items():
                self.preferences[(student_atom, course_atom)] = rank
    
    def build_model(self):
        """Build the CP-SAT model with constraints matching model.lp"""
        print(f"Building model with {len(self.students)} students and {len(self.courses)} courses")
        
        # Create decision variables: assign(student, course)
        for student in self.students:
            for course in self.courses:
                self.assignments[(student, course)] = self.model.NewBoolVar(f"assign_{student}_{course}")
        
        # Constraint: Each student gets exactly K courses
        for student in self.students:
            student_assignments = [self.assignments[(student, course)] for course in self.courses]
            self.model.Add(sum(student_assignments) == self.courses_per_student)
        
        # Constraint: Course capacity limits
        for course in self.courses:
            course_assignments = [self.assignments[(student, course)] for student in self.students]
            course_count = sum(course_assignments)
            
            # Max students per course
            self.model.Add(course_count <= self.max_students_per_course)
            
            # Min students per course (only if course has students)
            # This is tricky - we need to say: if course_count > 0, then course_count >= min
            # We can model this as: course_count == 0 OR course_count >= min
            has_students = self.model.NewBoolVar(f"has_students_{course}")
            self.model.Add(course_count >= 1).OnlyEnforceIf(has_students)
            self.model.Add(course_count == 0).OnlyEnforceIf(has_students.Not())
            self.model.Add(course_count >= self.min_students_per_course).OnlyEnforceIf(has_students)
        
        # Objective: Minimize preference penalties
        penalty_terms = []
        
        for student in self.students:
            for course in self.courses:
                assignment_var = self.assignments[(student, course)]
                
                if (student, course) in self.preferences:
                    # Student has preference for this course - use their rank as penalty
                    rank = self.preferences[(student, course)]
                    penalty_terms.append(rank * assignment_var)
                else:
                    # Student has no preference - apply out-of-preference penalty
                    if self.hard_enforced_preference:
                        # Hard constraint: cannot assign students to courses they didn't prefer
                        self.model.Add(assignment_var == 0)
                    else:
                        # Soft constraint: apply penalty
                        penalty_terms.append(self.out_of_preference_penalty * assignment_var)
        
        # Minimize total penalty
        if penalty_terms:
            self.model.Minimize(sum(penalty_terms))
    
    def solve(self, time_limit_seconds: int = 30) -> bool:
        """Solve the model and return success status"""
        self.solver.parameters.max_time_in_seconds = time_limit_seconds
        status = self.solver.Solve(self.model)
        
        if status == cp_model.OPTIMAL:
            print("Optimal solution found!")
            return True
        elif status == cp_model.FEASIBLE:
            print("Feasible solution found!")
            return True
        elif status == cp_model.INFEASIBLE:
            print("No feasible solution exists!")
            return False
        else:
            print(f"Solver status: {status}")
            return False
    
    def print_solution(self):
        """Print the solution in a format similar to ASP output"""
        if not hasattr(self, 'solver') or self.solver.StatusName() not in ['OPTIMAL', 'FEASIBLE']:
            print("No solution to display")
            return
        
        print("\n=== SOLUTION ===")
        
        # Print assignments with preferences
        assignments = []
        total_penalty = 0
        
        for student in self.students:
            for course in self.courses:
                if self.solver.Value(self.assignments[(student, course)]) == 1:
                    if (student, course) in self.preferences:
                        rank = self.preferences[(student, course)]
                        penalty = rank
                    else:
                        rank = "no_pref"
                        penalty = self.out_of_preference_penalty
                    
                    assignments.append((student, course, rank))
                    total_penalty += penalty
        
        # Sort by student for consistent output
        assignments.sort()
        
        # for student, course, rank in assignments:
        #     print(f"res({student},{course},{rank}).")
        
        # Print course counts
        print("\n=== COURSE COUNTS ===")
        for course in self.courses:
            count = sum(self.solver.Value(self.assignments[(student, course)]) for student in self.students)
            print(f"count({count},{course}).")
        
        # Print quality statistics
        print("\n=== QUALITY STATISTICS ===")
        rank_counts = {}
        for student, course, rank in assignments:
            if rank != "no_pref":
                rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        for rank in sorted(rank_counts.keys()):
            count = rank_counts[rank]
            print(f"quality(rank({rank}),amount({count})).")
        
        if any(rank == "no_pref" for _, _, rank in assignments):
            no_pref_count = sum(1 for _, _, rank in assignments if rank == "no_pref")
            print(f"quality(rank(no_preference),amount({no_pref_count})).")
        
        print(f"\nTotal penalty: {total_penalty}")
        if hasattr(self.solver, 'ObjectiveValue'):
            print(f"Objective value: {self.solver.ObjectiveValue()}")


def main():
    """Main entry point for the OR-Tools solver CLI."""
    parser = argparse.ArgumentParser(
        description="Solve course assignment problem using OR-Tools CP-SAT"
    )
    parser.add_argument(
        "input",
        help="Input file (.lp facts or .csv)"
    )
    parser.add_argument(
        "--time-limit",
        type=int,
        default=30,
        help="Time limit in seconds (default: 30)"
    )
    parser.add_argument(
        "--courses-per-student",
        type=int,
        help="Number of courses per student (overrides input file)"
    )
    parser.add_argument(
        "--max-students-per-course",
        type=int,
        help="Maximum students per course (overrides input file)"
    )
    parser.add_argument(
        "--min-students-per-course",
        type=int,
        help="Minimum students per course (overrides input file)"
    )
    
    args = parser.parse_args()
    
    # Create solver
    solver = CourseAssignmentSolver()
    
    # Load input data
    if args.input.endswith('.csv'):
        solver.load_from_csv(args.input)
    else:
        with open(args.input, 'r') as f:
            content = f.read()
        solver.load_from_lp_facts(content)
    
    # Override configuration if specified
    if args.courses_per_student is not None:
        solver.courses_per_student = args.courses_per_student
    if args.max_students_per_course is not None:
        solver.max_students_per_course = args.max_students_per_course
    if args.min_students_per_course is not None:
        solver.min_students_per_course = args.min_students_per_course
    
    print(f"Configuration:")
    print(f"  Courses per student: {solver.courses_per_student}")
    print(f"  Max students per course: {solver.max_students_per_course}")
    print(f"  Min students per course: {solver.min_students_per_course}")
    print(f"  Hard enforce preferences: {solver.hard_enforced_preference}")
    
    # Build and solve model
    solver.build_model()
    
    if solver.solve(args.time_limit):
        solver.print_solution()
    else:
        sys.exit(1)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f"Time taken: {round(time.time() - start_time, 4)} seconds")
