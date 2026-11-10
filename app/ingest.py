
import json

input_path = "data/records.json"

try:
    # Read JSON records
    with open(input_path, "r", encoding="utf-8") as file:
        records = json.load(file)

    clean_records = []

    # Required fields in every record
    required_fields = [
        "record_id",
        "topic",
        "key_rule",
        "source",
        "source_section",
        "source_pages"
    ]

    # Check each record
    for record in records:
        try:
            for field in required_fields:
                if field not in record:
                    raise ValueError("Missing field: " + field)

            if not isinstance(record["record_id"], int):
                raise ValueError("Record ID must be an integer")

            if not isinstance(record["source_pages"], list):
                raise ValueError("Source pages must be a list")

            clean_records.append(record)

        except (ValueError, TypeError) as error:
            print("Skipping invalid record:", error)

    # Save validated records
    with open(input_path, "w", encoding="utf-8") as file:
        json.dump(clean_records, file, indent=4, ensure_ascii=False)

    print("\nData validation completed.")
    print("Total records:", len(records))
    print("Valid records:", len(clean_records))
    print("Invalid records:", len(records) - len(clean_records))

except FileNotFoundError:
    print("Records file not found.")

except json.JSONDecodeError:
    print("Invalid JSON format.")

except Exception as error:
    print("Error:", error)
