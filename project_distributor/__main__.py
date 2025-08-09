"""
Main entry point for the project_distributor package.

This module allows the package to be run as a module:
    python -m project_distributor [command] [options]
"""

import sys
from .ortools_solver import main as ortools_main
from .asp_solver import main as asp_main


def main():
    """Main entry point that delegates to the appropriate command."""
    if len(sys.argv) > 1 and sys.argv[1] == "solve":
        # Syntax: python -m project_distributor solve [--backend {ortools,asp}] <input> [options]
        backend = "ortools"
        args = sys.argv[2:]

        def _consume_flag(flag: str):
            nonlocal args
            if flag in args:
                i = args.index(flag)
                if i + 1 < len(args):
                    val = args[i + 1]
                    # remove flag and its value
                    args = args[:i] + args[i + 2 :]
                    return val
            return None

        # Support both long and short flags
        b = _consume_flag("--backend") or _consume_flag("-b")
        if b in {"asp", "ortools"}:
            backend = b

        # Hand off to the appropriate solver CLI by rewriting sys.argv.
        # Argparse expects sys.argv[0] to be the program name, so we must
        # include a dummy program name before the actual arguments.
        if backend == "asp":
            sys.argv = ["project_distributor.asp_solver"] + args
            asp_main()
        else:
            sys.argv = ["project_distributor.ortools_solver"] + args
            ortools_main()
        return

    # Default help output
    print("Project Distributor - Course Assignment Solver")
    print()
    print("Available commands:")
    print("  solve <input_file> [options]  - Solve course assignment problem")
    print()
    print("Options for 'solve':")
    print("  --backend, -b {ortools,asp}   Select backend (default: ortools)")
    print()
    print("Examples:")
    print("  python -m project_distributor solve students.csv")
    print("  python -m project_distributor solve -b asp examples/students.lp --time-limit 60")
    print()
    print("For more help on a solver:")
    print("  python -m project_distributor solve --help   # OR-Tools options")
    print("  python -m project_distributor solve -b asp --help   # ASP options")


if __name__ == "__main__":
    main()
