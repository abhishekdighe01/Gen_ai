
from data.sample_records import records


def load_records():
    return records


def search(keyword):
    results = []

    for record in records:
        if keyword.lower() in record["topic"].lower() or keyword.lower() in record["key_rule"].lower():
            results.append(record)

    return results


def count_by(field):
    result = {}

    for record in records:
        value = record[field]

        if value in result:
            result[value] = result[value] + 1
        else:
            result[value] = 1

    return result


def get_by_id(record_id):
    for record in records:
        if record["record_id"] == record_id:
            return record

    return None
