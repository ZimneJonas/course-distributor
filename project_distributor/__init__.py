"""
Project Distributor - A course assignment solver using Answer Set Programming and OR-Tools.

This package provides tools for solving course assignment problems where students
need to be assigned to courses based on their preferences while respecting
constraints like course capacity limits.
"""

__version__ = "1.0.0"
__author__ = "Jonas Winter"
__description__ = "Course assignment solver using ASP and OR-Tools"

from .csv_parser import parse_csv_preferences, normalize_atom, transliterate_german_characters
from .ortools_solver import CourseAssignmentSolver

__all__ = [
    "parse_csv_preferences",
    "normalize_atom", 
    "transliterate_german_characters",
    "CourseAssignmentSolver"
]
