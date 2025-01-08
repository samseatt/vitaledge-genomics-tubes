# file: screen_scrape_formatter.py
# python ./screen_scrape_formatter.py /Users/samseatt/projects/vitaledge/data/loader/raw/raw_studies.txt /Users/samseatt/projects/vitaledge/data/loader/queued/genomic_studies_001.txt

import re
import sys

def parse_raw_studies(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        raw_data = infile.read()
        records = raw_data.split("---END RECORD---")
        
        formatted_records = []
        
        for record in records:
            record = record.strip()
            if not record:
                continue

            # Parse study name
            study_name_match = re.search(r"SHARE\s+(.*)\n", record)
            study_name = study_name_match.group(1).strip() if study_name_match else "Unknown Study"

            # Parse tags
            tags_match = re.search(r"SHARE\n(.*)STUDY SUMMARY", record, re.S)
            tags = []
            if tags_match:
                tags_section = tags_match.group(1).splitlines()
                tags = [line.strip() for line in tags_section if line.strip()]

            # Parse study summary
            summary_match = re.search(r"STUDY SUMMARY\s+([^\n]+)", record)
            study_summary = summary_match.group(1).strip() if summary_match else "No summary available."

            # Parse your result
            percentile_match = re.search(r"YOUR RESULT\s+(\d+)(?:th|st|nd|rd)?\s+PERCENTILE", record)
            percentile = int(percentile_match.group(1)) if percentile_match else 0
            genetic_score_match = re.search(r"your personal genetic score.*?([\d.]+)", record, re.S | re.I)
            genetic_score = float(genetic_score_match.group(1).rstrip('.')) if genetic_score_match else 0.0

            # Parse study description
            description_match = re.search(r"STUDY DESCRIPTION\s+(.*?)\s+DID YOU KNOW\?", record, re.S)
            study_description = description_match.group(1).strip() if description_match else "No description available."

            # Parse variants
            variants_match = re.search(r"VARIANTS\s+(Variant.*?Significance.*?)(?=\n\n|\Z)", record, re.S)
            variants = []
            if variants_match:
                variant_lines = variants_match.group(1).splitlines()
                headers = variant_lines[0]
                for line in variant_lines[1:]:
                    if not line.strip():
                        continue
                    variants.append(line.strip())

            # Combine structured data
            formatted_record = (
                f"STUDY\n"
                f"Name: {study_name}\n"
                f"Tags: {', '.join(tags)}\n\n"
                f"STUDY SUMMARY\n"
                f"{study_summary}\n\n"
                f"YOUR RESULT\n"
                f"Percentile: {percentile}\n"
                f"Genetic Score: {genetic_score}\n\n"
                f"STUDY DESCRIPTION\n"
                f"{study_description}\n\n"
                f"VARIANTS\n"
                f"Variant\tGenotype\tEffect Size\tVariant Frequency\tSignificance\n"
                f"{chr(10).join(variants)}"
            )

            formatted_records.append(formatted_record)

        # Write formatted records to the output file
        outfile.write("\n---END RECORD---\n".join(formatted_records) + "\n---END RECORD---\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python screen_scrape_formatter.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    parse_raw_studies(input_file, output_file)
