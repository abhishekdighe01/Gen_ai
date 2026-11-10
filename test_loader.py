from app.data_loader import load_solar_records

records = load_solar_records()

print("Total records:", len(records))

for record in records:
    print(record.record_id, "-", record.topic)