from pymongo import MongoClient
import json
import sys
from pathlib import Path

def export_studies_to_json(patient_id, output_file):
    # MongoDB connection
    mongo_uri = "mongodb://localhost:27017"  # Update if needed
    db_name = "genomic_pipeline_db"
    collection_name = "studies"

    try:
        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]

        # Query for the patient's studies
        query = {"patient_id": patient_id}
        studies = list(collection.find(query))

        if not studies:
            print(f"No studies found for patient_id: {patient_id}")
            return

        # Convert MongoDB data to JSON-serializable format
        for study in studies:
            study["_id"] = str(study["_id"])  # Convert ObjectId to string

        # Write data to the JSON file
        output_path = Path(output_file)
        with output_path.open("w") as outfile:
            json.dump(studies, outfile, indent=4)

        print(f"Exported {len(studies)} studies for patient_id '{patient_id}' to {output_file}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python export_studies_to_json.py <patient_id> <output_file>")
        sys.exit(1)

    patient_id = sys.argv[1]
    output_file = sys.argv[2]

    export_studies_to_json(patient_id, output_file)
