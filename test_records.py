
from app.records import load_records, search, count_by, get_by_id

# 1. Load all records
all_records = load_records()
print("Total records:", len(all_records))

# 2. Search records
results = search("subsidy")
print("\nSearch results:", len(results))

for record in results:
    print(record["topic"])

# 3. Count records by topic
topic_count = count_by("topic")
print("\nTotal topics:", len(topic_count))

# 4. Find a record by ID
record = get_by_id(18)

if record:
    print("\nRecord found:", record["topic"])
else:
    print("\nRecord not found")
