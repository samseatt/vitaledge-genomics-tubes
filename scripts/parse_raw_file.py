import re
import json
import sys
from pathlib import Path
from parsing_utils import parse_nebula_dna_score  # Assuming this contains the logic you provided earlier

def parse_raw_file(input_file, output_file, patient_id):
    print(f"parse_raw_file called")
    # Read raw input file
    with open(input_file, "r") as infile:
        raw_data = infile.read()

    # Split records by the separator
    records = raw_data.split("######")
    print(f"{len(records)} records read")
    structured_records = []

    for record in records:
        record = record.strip()
        if not record:
            continue

        try:
            # Parse the study using existing logic
            study_url = "https://example.com"  # Placeholder, replace with real logic if necessary
            print(f"Parsed study_url: {study_url}")
            known_tags = []  # Pass known tags if required
            parsed_study = parse_nebula_dna_score(patient_id, study_url, record, known_tags=known_tags)
            print(f"Parsed parsed_study: {parsed_study}")
        
            if not parsed_study:
                print(f"Skipping empty or unparseable record: {record[:50]}...")
                continue

            # Add to structured records
            structured_records.append(parsed_study)

        except Exception as e:
            print(f"Error parsing record: {record[:50]}... - {e}")
            continue

    # Write the structured records to the output file
    with open(output_file, "w") as outfile:
        json.dump(structured_records, outfile, indent=4)

    print(f"Structured records written to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python parse_raw_file.py <input_file> <output_file> <patient_id>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    patient_id = sys.argv[3]

    parse_raw_file(input_file, output_file, patient_id)
