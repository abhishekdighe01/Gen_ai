
import json

file_path = "data/records.json"

with open(file_path, "r", encoding="utf-8") as file:
    records = json.load(file)

# Assign sequential IDs without deleting records
for index, record in enumerate(records, start=1):
    record["record_id"] = index

with open(file_path, "w", encoding="utf-8") as file:
    json.dump(records, file, indent=4, ensure_ascii=False)

print("Record IDs updated successfully!")
print("Total records:", len(records))
