import random
import os

def generate_students_csv_content(amount: int) -> str:
    """Return generated students CSV content as a string without writing to disk."""
    lines = [";Fußball;Basketball;Frisbee;Volleyball;Tennis;Handball;Hockey\n"]
    for i in range(amount):
        options = ["", "", "1", "2", "3", "4", "5"]
        random.shuffle(options)
        lines.append(f"student_{i};{';'.join(options)}\n")
    return "".join(lines)


# write file (CLI compatibility)
def generate_students(amount: int) -> None:
    out_path = os.path.join(os.path.dirname(__file__), "students.csv")
    content = generate_students_csv_content(amount)
    with open(out_path, "w", encoding="utf-8", newline="") as file:
        file.write(content)

if __name__ == "__main__":
    import sys
    amount = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    generate_students(amount)
