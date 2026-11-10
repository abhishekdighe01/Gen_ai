
from app.data_loader import load_solar_records


def load_records():
    return load_solar_records()


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
            result[value] = result[value] + 1
        else:
            result[value] = 1

    return result


def get_by_id(record_id):
    for record in load_records():
        if record.record_id == record_id:
            return record

    return None
