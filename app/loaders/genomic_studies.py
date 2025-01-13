import psycopg2
from psycopg2.extras import execute_batch
from pymongo import MongoClient
from pathlib import Path
import json
import logging

# Logger for this file
logger = logging.getLogger(__name__)

DB_CONFIG = {
    "dbname": "vitaledge_datalake",
    "user": "samseatt",
    "password": "password",
    "host": "localhost",
    "port": 5432
}

def load_subject_studies_to_datalake(studies_data):
    """
    Load subject study data into the Datalake PostgreSQL database.
    - studies_data: List of study records from the JSON file.
    """
    try:
        # Establish database connection
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Queries for inserting into tables
        subject_lookup_query = "SELECT id FROM subjects WHERE de_id = %s;"

        study_insert_query = """
        INSERT INTO studies (
            name, summary, description, url, category
        ) VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (name) DO UPDATE SET
            summary = EXCLUDED.summary,
            description = EXCLUDED.description,
            url = EXCLUDED.url,
            category = EXCLUDED.category
        RETURNING id;
        """

        subject_study_insert_query = """
        INSERT INTO subject_studies (
            subject_id, study_id, score, score_percentile
        ) VALUES (%s, %s, %s, %s)
        RETURNING id;
        """

        variant_insert_query = """
        INSERT INTO subject_study_variants (
            study_id, variant, genotype, effect_size, variant_frequency, significance
        ) VALUES (%s, %s, %s, %s, %s, %s);
        """

        study_ids = []

        # Process each study in the data
        for study in studies_data:
            # Extract 'de_id' from JSON, treating it as 'patient_id'
            de_id = study["patient_id"]
            cursor.execute(subject_lookup_query, (de_id,))
            result = cursor.fetchone()

            if not result:
                raise ValueError(f"No subject found with de_id: {de_id}")

            subject_id = result[0]

            study_data = study["study"]
            score_data = study["score"]
            variants_data = study.get("variants", [])

            # Insert study into studies table
            study_values = (
                study_data["name"],
                study_data.get("summary"),
                study_data.get("description"),
                study_data.get("url"),
                study_data.get("category")
            )
            logger.info("Executing query for studies:")
            logger.info(cursor.mogrify(study_insert_query, study_values))
            cursor.execute(study_insert_query, study_values)
            study_id = cursor.fetchone()[0]
            study_ids.append(study_id)

            # Insert into subject_studies table
            subject_study_values = (
                subject_id,
                study_id,
                score_data.get("genetic-score"),
                score_data.get("percentile")
            )
            logger.info("Executing query for subject_studies:")
            logger.info(cursor.mogrify(subject_study_insert_query, subject_study_values))
            cursor.execute(subject_study_insert_query, subject_study_values)
            subject_study_id = cursor.fetchone()[0]
            logger.info(f"Successfully inserted subject-study with subject_study_id: {subject_study_id}")

            # Insert phenotype tags (if any)
            for tag in study_data.get("tags", []):
                tag_id = get_or_create_phenotype_tag(cursor, tag)
                cursor.execute(
                    "INSERT INTO subject_study_phenotypes (subject_study_id, phenotype_tag_id) VALUES (%s, %s);",
                    (subject_study_id, tag_id)
                )
            logger.info(f"Successfully inserted tags.")

            # Insert variants
            variant_values = [
                (
                    subject_study_id,
                    variant.get("variant"),
                    variant.get("genotype"),
                    variant.get("effect-size"),
                    variant.get("variant-frequency"),
                    float(variant.get("significance").replace(" x 10", "e"))
                )
                for variant in variants_data
            ]
            logger.info(f"Successfully parsed {len(variants_data)} variants")
            if variant_values:
                execute_batch(cursor, variant_insert_query, variant_values)
                logger.info(f"Successfully inserted {len(variant_values)} variants")

        # Commit the transaction
        conn.commit()
        logger.info("All data successfully loaded into the Datalake.")
        return study_ids

    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_or_create_phenotype_tag(cursor, tag_name):
    """
    Insert a new phenotype tag or return the existing tag ID.
    """
    tag_query = "SELECT id FROM phenotype_tags WHERE name = %s;"
    tag_insert = "INSERT INTO phenotype_tags (name) VALUES (%s) RETURNING id;"

    cursor.execute(tag_query, (tag_name,))
    tag_id = cursor.fetchone()

    if not tag_id:
        cursor.execute(tag_insert, (tag_name,))
        tag_id = cursor.fetchone()[0]
    else:
        tag_id = tag_id[0]

    return tag_id


def load_patient_studies_to_datalake_DELETE_ME(studies_data):
    """
    Load patient study data into the Datalake PostgreSQL database.
    - studies_data: List of study records from the JSON file.
    """
    try:
        # Establish database connection
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Insert studies into patient_studies table
        study_insert_query = """
        INSERT INTO patient_studies (
            patient_id, study_name, study_summary, study_description, study_url, genetic_score, percentile
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """

        variant_insert_query = """
        INSERT INTO patient_variants (
            study_id, variant, genotype, effect_size, variant_frequency, significance
        ) VALUES (%s, %s, %s, %s, %s, %s);
        """

        study_ids = []

        for study in studies_data:
            # Use patient_id directly as a string
            patient_id = study["patient_id"]

            study_data = study["study"]
            score_data = study["score"]
            variants_data = study.get("variants", [])

            # Insert study
            study_values = (
                patient_id,
                study_data["name"],
                study_data.get("summary"),
                study_data.get("description"),
                study_data.get("url"),
                score_data.get("genetic-score"),
                score_data.get("percentile")
            )
            logger.info("Executing query:")
            logger.info(cursor.mogrify(study_insert_query, study_values))
            cursor.execute(study_insert_query, study_values)
            logger.debug(f"Inserted study")
            result = cursor.fetchone()
            if not result:
                raise ValueError("Study insertion failed, no ID returned.")
            study_id = result[0]
            study_ids.append(study_id)

            # Insert phenotype tags
            for tag in study_data.get("tags", []):
                tag_id = get_or_create_phenotype_tag(cursor, tag)
                cursor.execute(
                    "INSERT INTO patient_study_phenotypes (patient_study_id, phenotype_tag_id) VALUES (%s, %s);",
                    (study_id, tag_id)
                )

            # Insert associated variants
            variant_values = [
                (
                    study_id,
                    variant["variant"],
                    variant.get("genotype"),
                    variant.get("effect-size"),
                    variant.get("variant-frequency"),
                    variant.get("significance")
                )
                for variant in variants_data
            ]
            execute_batch(cursor, variant_insert_query, variant_values)

        # Commit the transaction
        conn.commit()

        logger.info("All data successfully loaded into the Datalake.")
        return study_ids

    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_or_create_phenotype_tag_DELETE_ME(cursor, tag_name):
    """
    Insert a new phenotype tag or return the existing tag ID.
    """
    tag_query = "SELECT id FROM phenotype_tags WHERE name = %s;"
    tag_insert = "INSERT INTO phenotype_tags (name) VALUES (%s) RETURNING id;"

    cursor.execute(tag_query, (tag_name,))
    tag_id = cursor.fetchone()

    if not tag_id:
        cursor.execute(tag_insert, (tag_name,))
        tag_id = cursor.fetchone()[0]
    else:
        tag_id = tag_id[0]

    return tag_id

def export_subject_studies_to_json(subject_id, output_file):
    # MongoDB connection
    mongo_uri = "mongodb://localhost:27017"  # Update if needed
    db_name = "genomic_pipeline_db"
    collection_name = "studies"

    try:
        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        logger.info(f"Connected to Beaker at {mongo_uri} using collection: {collection_name}")

        # Query for the subject's studies
        query = {"patient_id": subject_id}
        logger.info(f"Getting studies for subject: {subject_id}")
        studies = list(collection.find(query))

        if not studies:
            logger.warning(f"No studies found for subject_id: {subject_id}")
            return

        # Convert MongoDB data to JSON-serializable format
        for study in studies:
            study["_id"] = str(study["_id"])  # Convert ObjectId to string

        # Write data to the JSON file
        output_path = Path(output_file)
        with output_path.open("w") as outfile:
            json.dump(studies, outfile, indent=4)

        logger.info(f"Exported {len(studies)} studies for subject_id '{subject_id}' to {output_file}")

    except Exception as e:
        logger.error(f"Error: {e}")

    finally:
        client.close()
