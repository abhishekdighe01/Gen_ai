
from data.sample_records import records as sample_records
from app.models import SolarRecord


def load_records():
    solar_records = []

    for item in sample_records:
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


def search(keyword):
    results = []

    for record in load_records():
        if keyword.lower() in record.topic.lower() or keyword.lower() in record.key_rule.lower():
            results.append(record)

    return results


def count_by(field):
    result = {}

    for record in load_records():
        value = getattr(record, field)

        if value in result:
            result[value] += 1
        else:
            result[value] = 1

    return result


def get_by_id(record_id):
    for record in load_records():
        if record.record_id == record_id:
            return record

    return None
