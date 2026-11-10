
import json
from app.models import SolarRecord


def load_solar_records():
    with open("data/records.json", "r", encoding="utf-8") as file:
        data = json.load(file)

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

    return solar_records
