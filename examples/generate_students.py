import random
import os

# write file
def generate_students(amount: int) -> None:
    out_path = os.path.join(os.path.dirname(__file__), "students.csv")
    with open(out_path, "w", encoding="utf-8", newline="") as file:
        file.write(";Fußball;Basketball;Frisbee;Volleyball;Tennis;Handball;Hockey\n")
        for i in range(amount):
            options = ["", "", "1", "2", "3", "4", "5"]
            random.shuffle(options)
            file.write(f"student_{i};{';'.join(options)}\n")

if __name__ == "__main__":
    import sys
    amount = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    generate_students(amount)
