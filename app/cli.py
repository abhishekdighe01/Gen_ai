
from app.records import load_records, search, count_by, get_by_id


while True:

    print("SuryaGharSathi Records")
    print("1. Show all records")
    print("2. Search records")
    print("3. Count records by topic")
    print("4. Find record by ID")
    print("0. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        all_records = load_records()

        for record in all_records:
            print("\nID:", record["record_id"])
            print("Topic:", record["topic"])
            print("Rule:", record["key_rule"])

    elif choice == "2":
        keyword = input("Enter keyword: ")
        results = search(keyword)

        for record in results:
            print("\nID:", record["record_id"])
            print("Topic:", record["topic"])
            print("Rule:", record["key_rule"])

        if len(results) == 0:
            print("No records found.")

    elif choice == "3":
        result = count_by("topic")

        for topic, count in result.items():
            print(topic, ":", count)

    elif choice == "4":
        record_id = int(input("Enter record ID: "))
        record = get_by_id(record_id)

        if record:
            print("\nTopic:", record["topic"])
            print("Rule:", record["key_rule"])
            print("Source:", record["source_url"])
        else:
            print("Record not found.")

    elif choice == "0":
        print("Thank you for using SuryaGharSathi!")
        break

    else:
        print("Invalid choice. Try again.")
