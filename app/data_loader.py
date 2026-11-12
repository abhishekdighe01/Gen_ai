
import json
from app.models import Record, SolarRecord


def load_solar_records():
    """Load records from data/records.json and return a list of Record objects."""
    with open("data/records.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    solar_records = []

    for item in data:
        try:
            record = Record(
                record_id=item["record_id"],
                document_title=item.get("document_title", ""),
                issuing_body=item.get("issuing_body", ""),
                date_issued=item.get("date_issued", ""),
                topic=item["topic"],
                key_rule=item["key_rule"],
                # Support both legacy key "source" and new key "source_url"
                source_url=item.get("source_url") or item.get("source", ""),
                source_section=item.get("source_section", ""),
                source_pages=item.get("source_pages", []),
            )
            solar_records.append(record)
        except (KeyError, TypeError) as error:
            print(f"Skipping malformed record (id={item.get('record_id', '?')}): {error}")

    return solar_records
