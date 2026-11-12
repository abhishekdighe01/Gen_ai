
import os


folder = "data/processed"

for filename in os.listdir(folder):

    if filename.endswith(".txt"):

        file_path = os.path.join(folder, filename)

        print("\n==============================")
        print("DOCUMENT:", filename)
        print("==============================")

        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        for line in lines:

            line = line.strip()

            if line and (
                line[0].isdigit()
                or line.lower().startswith("annexure")
                or line.lower().startswith("appendix")
            ):
                print(line)
