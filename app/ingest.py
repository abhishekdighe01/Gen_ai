
import os
import json
import shutil
from PyPDF2 import PdfReader


pdf_files = [
    "data/raw/mnre_guidelines.pdf",
    "data/raw/discom_incentives_guidelines.pdf",
    "data/raw/resco_guidelines.pdf"
]


def extract_pdf_text(pdf_path):

    try:
        os.makedirs("data/processed", exist_ok=True)

        filename = os.path.basename(pdf_path)
        text_filename = filename.replace(".pdf", ".txt")
        output_path = os.path.join("data/processed", text_filename)

        print("\nProcessing:", filename)

        reader = PdfReader(pdf_path)

        extracted_text = ""

        for page_number, page in enumerate(reader.pages, start=1):

            page_text = page.extract_text()

            if page_text and page_text.strip():
                extracted_text += f"\n--- Page {page_number} ---\n"
                extracted_text += page_text

        if not extracted_text.strip():
            print("Warning: No readable text found:", filename)
            return

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(extracted_text)

        print("Extraction successful:", output_path)
        print("Pages:", len(reader.pages))

    except FileNotFoundError:
        print("PDF not found:", pdf_path)

    except Exception as error:
        print("Error processing PDF:", error)


def validate_json():

    input_path = "data/records.json"

    try:
        with open(input_path, "r", encoding="utf-8") as file:
            records = json.load(file)

        if not isinstance(records, list):
            raise ValueError("JSON data must contain a list of records.")

        # Create backup before changing the original file
        backup_path = "data/records_backup.json"
        shutil.copy2(input_path, backup_path)

        clean_records = []
        seen_ids = set()

        required_fields = [
            "record_id",
            "topic",
            "key_rule",
            "source",
            "source_section",
            "source_pages"
        ]

        for record in records:

            try:
                if not isinstance(record, dict):
                    raise ValueError("Record must be a dictionary")

                for field in required_fields:
                    if field not in record:
                        raise ValueError("Missing field: " + field)

                if not isinstance(record["record_id"], int) or isinstance(record["record_id"], bool):
                    raise ValueError("Record ID must be an integer")

                if record["record_id"] in seen_ids:
                    raise ValueError("Duplicate record ID")

                if not all(isinstance(record[field], str) and record[field].strip()
                           for field in ["topic", "key_rule", "source", "source_section"]):
                    raise ValueError("Text fields cannot be empty")

                if not isinstance(record["source_pages"], list):
                    raise ValueError("Source pages must be a list")

                if not all(isinstance(page, int) and page > 0
                           for page in record["source_pages"]):
                    raise ValueError("Source pages must contain positive integers")

                seen_ids.add(record["record_id"])
                clean_records.append(record)

            except (ValueError, TypeError) as error:
                print("Skipping invalid record:", error)

        with open(input_path, "w", encoding="utf-8") as file:
            json.dump(clean_records, file, indent=4, ensure_ascii=False)

        print("\nJSON validation completed.")
        print("Total records:", len(records))
        print("Valid records:", len(clean_records))
        print("Invalid records:", len(records) - len(clean_records))
        print("Backup created:", backup_path)

    except FileNotFoundError:
        print("Records file not found.")

    except json.JSONDecodeError:
        print("Invalid JSON format.")

    except Exception as error:
        print("Validation error:", error)


if __name__ == "__main__":

    print("Starting PDF ingestion...")

    for pdf_file in pdf_files:
        extract_pdf_text(pdf_file)

    print("\nStarting JSON validation...")

    validate_json()
