import random
import os

# write file
def generate_students(amount: int):
    with open(os.path.join(os.path.dirname(__file__), "students.csv"), "w") as file:
        file.write(";Fußball;Basketball;Frisbee;Volleyball;Tennis;Handball;Hockey\n")
        for i in range(AMOUNT):
            options = ["","", "1", "2", "3","4","5"]
            random.shuffle(options)
            file.write(f"student_{i};{';'.join(options)}\n")

if __name__ == "__main__":
    import sys
    # default amount is 100
    AMOUNT = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    generate_students(AMOUNT)
