
import json
from app.models import SolarRecord

# Open the JSON file
with open("data/records.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Convert dictionaries into SolarRecord objects
solar_records = []

for item in data:
    record = SolarRecord(
        record_id=item["record_id"],
        topic=item["topic"],
        key_rule=item["key_rule"],
        source=item["source"],
        source_section=item["source_section"],
        source_pages=item["source_pages"]
    )

    solar_records.append(record)

# Display the records
print("Total records:", len(solar_records))

for record in solar_records:
    print("\nTopic:", record.topic)
    print("Rule:", record.key_rule)
