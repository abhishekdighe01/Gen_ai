
import shutil
from pathlib import Path
from pprint import pformat

from data.sample_records import records


# Section and page references from the MNRE guidelines
references = {
    1: ("Section 1 - Background", [2]),
    2: ("Section 2 - Scope", [2, 3]),
    3: ("Section 3 - Aim and Objectives", [3]),
    4: ("Section 4 - Transition From Existing Scheme", [3, 4]),
    5: ("Section 5 - Central Financial Assistance", [4, 8]),
    6: ("Section 6 - Method of Implementation", [9, 12]),
    7: ("Section 7 - Vendor Registration and Performance", [12, 13]),
    8: ("Section 8 - National Portal Functionalities", [14, 16]),
    9: ("Section 9 - System Components and Technical Specifications", [16]),
    10: ("Section 10 - Quality of Installations", [16, 17]),
    11: ("Section 11 - Grievance Redressal", [17]),
    12: ("Section 12 - MoU", [17]),
    13: ("Section 13 - Implementation Agency", [18]),
    14: ("Section 14 - Fund Release Mechanism", [18]),
    15: ("Section 15 - Scheme Monitoring", [19]),
    16: ("Section 16 - Amendment of Scheme Guidelines", [19]),

    17: ("Section 6(d) - Scheme Cost", [9]),
    18: ("Section 5(h) - Central Financial Assistance", [6, 7]),
    19: ("Sections 5(b) and 5(d) - Eligibility", [4, 5]),
    20: ("Section 6 - Application Process", [9, 10, 11]),

    # This information comes from TNEB, not the MNRE PDF.
    21: ("TNEB FAQ - Area Required", []),

    22: ("Section 7(d) and Annexure 2 - Warranty", [13, 24]),
    23: ("Section 7(d) and Annexure 2 - Operation and Maintenance", [13, 24]),
    24: ("Section 6(l) - Net Metering", [11]),
}


updated_records = []

for item in records:
    section, pages = references[item["record_id"]]

    new_record = {
        "record_id": item["record_id"],
        "topic": item["topic"],
        "key_rule": item["key_rule"],
        "source": item["source_url"],
        "source_section": section,
        "source_pages": pages
    }

    updated_records.append(new_record)


# Keep a backup before changing the original file
file_path = Path("data/sample_records.py")
backup_path = Path("data/sample_records_backup.py")

shutil.copy(file_path, backup_path)

# Write the updated records
file_content = "records = " + pformat(updated_records, width=100) + "\n"

file_path.write_text(file_content, encoding="utf-8")

print("Day 2 records updated successfully.")
print("Total records:", len(updated_records))
print("Backup created:", backup_path)
print("Fields:", list(updated_records[0].keys()))
