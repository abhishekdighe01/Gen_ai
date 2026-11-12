
import json
from app.models import Record, SolarRecord


def _load_from_json():
    """Internal helper: read data/records.json and return list of Record objects."""
    with open("data/records.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    records = []
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
            records.append(record)
        except (KeyError, TypeError) as error:
            print(f"Skipping malformed record (id={item.get('record_id', '?')}): {error}")

    return records


def load_records():
    """Return all records from data/records.json as Record objects."""
    return _load_from_json()


def search(keyword: str):
    """Return records whose topic or key_rule contains keyword (case-insensitive)."""
    results = []
    for record in load_records():
        if keyword.lower() in record.topic.lower() or keyword.lower() in record.key_rule.lower():
            results.append(record)
    return results


def count_by(field: str):
    """Return a dict mapping each unique value of field to its record count."""
    result = {}
    for record in load_records():
        value = getattr(record, field, None)
        if value is None:
            continue
        result[value] = result.get(value, 0) + 1
    return result


def get_by_id(record_id: int):
    """Return the first record matching record_id, or None if not found."""
    for record in load_records():
        if record.record_id == record_id:
            return record
    return None
