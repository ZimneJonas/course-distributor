"""
Main entry point for the project_distributor package.

This module allows the package to be run as a module:
    python -m project_distributor [command] [options]
"""

import sys
from .ortools_solver import main as solver_main


def main():
    """Main entry point that delegates to the appropriate command."""
    if len(sys.argv) > 1 and sys.argv[1] == "solve":
        # Remove the "solve" command and pass remaining args to solver
        sys.argv = sys.argv[1:]
        solver_main()
    else:
        print("Project Distributor - Course Assignment Solver")
        print()
        print("Available commands:")
        print("  solve <input_file> [options]  - Solve course assignment problem")
        print()
        print("Examples:")
        print("  python -m project_distributor solve students.csv")
        print("  python -m project_distributor solve students.lp --time-limit 60")
        print()
        print("For more help on a command:")
        print("  python -m project_distributor solve --help")


if __name__ == "__main__":
    main()
