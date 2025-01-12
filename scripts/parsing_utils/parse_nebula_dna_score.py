"""
api/utils/parsing_utils.py
"""
import json
import re
import unidecode
import logging

def parse_nebula_dna_score(patient_id, study_url, text, known_tags=[]):
    print(f"parse_nebula_dna_score called")
    logging.debug(f"Utility method parse_nebula_dna_score called with {len(text)} characters of text to parse for the study: {study_url}")

    # print(f"$$$$ known_tags: {known_tags}")
    # # Step 1: Parse "study" details
    # study_match = re.search(r"SHARE\s+(.+?\(\w+, \d{4}\))", text, re.S)
    # study_name = unidecode.unidecode(study_match.group(1).strip()) if study_match else None
    
    # Step 1: Parse "study" details
    study_match = re.search(r"SHARE\s+(.+?\(\w+, \d{4}\))", text, re.S)
    study_name = unidecode.unidecode(study_match.group(1).strip()) if study_match else None
    logging.debug(f"Parsed study name: {study_name}")

    # Step 2: Extract tags/categories based on single-word lines only
    # Look for potential tags between "SHARE" and "STUDY SUMMARY"
    tags_section_match = re.search(r"SHARE\s+(.+?)STUDY SUMMARY", text, re.S)
    tags = []

    if tags_section_match:
        # Split the section into lines and filter for single-word lines in known_tags
        lines = tags_section_match.group(1).splitlines()
        for line in lines:
            line = line.strip()
            # Check if the line is in known_tags and is a single word
            if line in known_tags:
                tags.append(line)

    logging.debug(f"Parsed tags: {tags}")

    summary_match = re.search(r"STUDY SUMMARY\s+([^\n]+)", text)
    study_summary = summary_match.group(1).strip() if summary_match else None
    logging.debug(f"Parsed study summary of {len(study_summary)} characters")

    description_match = re.search(r"STUDY DESCRIPTION\s+(.*?)\s+DID YOU KNOW\?", text, re.S)
    study_description = description_match.group(1).strip() if description_match else None
    logging.debug(f"Parsed study description of {len(study_description)} characters")

    study_info = {
        "name": study_name,
        "summary": study_summary,
        "description": study_description,
        "url": study_url,
        "tags": tags
    }

    # Step 2: Parse "score" details
    percentile_match = re.search(r"YOUR RESULT\s+(\d+)(?:th|st|nd|rd)?\s+PERCENTILE", text)
    percentile = int(percentile_match.group(1)) if percentile_match else None
    logging.debug(f"Parsed percentile: {percentile}")

    genetic_score_match = re.search(r"your personal genetic score.*?([\d.]+)", text)
    genetic_score = float(genetic_score_match.group(1).strip('.')) if genetic_score_match else None
    logging.debug(f"Parsed genetic score: {genetic_score}")

    score_info = {
        "percentile": percentile,
        "genetic-score": genetic_score
    }

    # logging.debug(f"TEXT: $$$$$ {text} $$$")

    # Step 3: Parse "variants" table
    # Find the start of the variants table after "SIGNIFICANCE" label
    ncol = 5    # Set the expected number of columns to parse in the variants table
    headers = ["variant", "genotype", "effect-size", "variant-frequency", "significance"]
    variant_table_start = text.find("VARIANT\nYOUR GENOTYPE\nEFFECT SIZE\nVARIANT FREQUENCY\nSIGNIFICANCE")
    if variant_table_start == -1:
        logging.debug(f"5-column variant table not found. Unable to parse")
        ncol = 6
        headers = ["variant", "genotype", "gene", "effect-size", "variant-frequency", "significance"]
        variant_table_start = text.find("VARIANT\nYOUR GENOTYPE\nGENE\nEFFECT SIZE\nVARIANT FREQUENCY\nSIGNIFICANCE")
        if variant_table_start == -1:
            return None  # Table not found, return None or raise an error
    
    logging.debug(f"Variants table exists.")
 
    # Split lines for table parsing
    variant_lines = text[variant_table_start:].splitlines()
    logging.debug(f"{len(variant_lines)} variant entries found.")
    variants = []

    # Process data rows in chunks of five lines each
    for i in range(ncol, len(variant_lines), ncol):
        j = i   # count columns within a row - to support/skip optional columns

        # Check if the current variant line starts with 'rs' followed by digits
        if not re.match(r"^rs\d+", variant_lines[j]):
            logging.debug(f"Invalid variant: {variant_lines[j]}")
            break  # Stop parsing if it's not a valid variant identifier

        variant = variant_lines[j].strip()
        logging.debug(f"Variant: {variant}")

        j += 1
        genotype = variant_lines[j].replace("YOUR ", "").strip()
        logging.debug(f"Genotype: {variant}")

        # Parse and throw away the GENE column if present
        if ncol == 6:
            j += 1

        # Effect Size: clean special symbols and validate numeric conversion
        j += 1
        effect_size_str = re.sub(r"\s*\(.*?\)", "", variant_lines[j]).strip()
        try:
            effect_size = float(effect_size_str)
        except ValueError:
            logging.debug(f"Error: ValueError in effect size.")
            effect_size = None  # Set to None if conversion fails

        logging.debug(f"Effect Size: {effect_size}")

        # Variant Frequency: strip '%' and validate conversion
        j += 1
        variant_freq_str = variant_lines[j].replace("%", "").strip()
        try:
            variant_frequency = float(variant_freq_str)
        except ValueError:
            logging.debug(f"Error: ValueError in variant frequency.")
            variant_frequency = None  # Set to None if conversion fails

        logging.debug(f"Variant Frequency: {variant_frequency}")

        # Significance is kept as a string
        j += 1
        significance = variant_lines[j].strip()
        logging.debug(f"Significance: {significance}")

        # Append the cleaned data to the list as a dictionary
        variants.append({
            "variant": variant,
            "genotype": genotype,
            "effect-size": effect_size,
            "variant-frequency": variant_frequency,
            "significance": significance
        })

    # Combine all parsed data into final JSON structure
    result = {
        "patient_id": patient_id,
        "study": study_info,
        "score": score_info,
        "variants": variants
    }

    # Return JSON structure as a string
    logging.debug(f"Parser successfully parsed the study {result['study']['name']} with {len(result['variants'])} variants")
    return result
