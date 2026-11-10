from app.models import SolarRecord

record = SolarRecord(
    record_id=1,
    topic="CFA Structure",
    key_rule="First 2 kW receives Rs 30000 per kW.",
    source="MNRE Operational Guidelines",
    source_section="Section 5(e) and 5(h)",
    source_pages=[5, 6]
)

print(record)
print("\nTopic:", record.topic)
print("Source pages:", record.source_pages)