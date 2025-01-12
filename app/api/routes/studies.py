# app/api/routes/studies.py
from fastapi import APIRouter, HTTPException
import logging
import os
import json
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from typing import Optional
from app.core.config import config  # Import the instantiated Config
from app.services.embeddings_service import EmbeddingsService
from app.services.vectordb_service import VectorDBService
from app.loaders.genomic_studies import load_subject_studies_to_datalake, export_subject_studies_to_json

# Logger for this file
logger = logging.getLogger(__name__)

# Initialize services
embeddings_service = EmbeddingsService()
vectordb_service = VectorDBService()

router = APIRouter()

# Data and folder configuration
DATA_FOLDER = "vitaledge/data/loader/queued"
ARCHIVE_FOLDER = "vitaledge/data/loader/archive"

# Use Config to fetch the database configuration
db_config = config.DATABASE  # This is a dictionary generated by the property method
db_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"

# Define a Pydantic model for the request body
class LoadRequestStudies(BaseModel):
    file_path: str  # Path to the JSON file containing subject studies
    subject_id: Optional[str]  # Subject ID for additional filtering or validation

class ExportRequestStudies(BaseModel):
    file_path: str  # Path to the JSON file to be created that will contain exported subject studies
    subject_id: Optional[str]  # Subject ID for additional filtering or validation

# Test database connection endpoint
@router.get("/test-db-connection")
async def test_db_connection():
    logger.debug("test_db_connection called.")
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
        return {"status": "success", "message": "Database connection is working"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/load_subject_study")
async def load_subject_study_endpoint(data: LoadRequestStudies):
    """
    Endpoint to load subject study data into the Datalake from a JSON file.
    - file_path: Path to the JSON file containing subject studies.
    - subject_id: Optional subject ID for validation.
    """
    try:
        file_path = data.file_path
        logger.debug(f"Called load_subject_study with file: {file_path}")

        # Validate file existence
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

        # Load JSON data
        with open(file_path, "r") as json_file:
            studies_data = json.load(json_file)

        # Call the loader function to load study data into Datalake
        study_ids = load_subject_studies_to_datalake(studies_data)
        i = 0
        logger.info(f"Study IDs from Datalake: {study_ids}")

        # Generate embeddings and populate VectorDB
        enriched_data = []
        logger.info(f"Reading studies data  for {len(studies_data)} studies")
        for study in studies_data:
            de_id = study["patient_id"]
            study_id = study_ids[i]
            i += 1
            study = study["study"]
            logger.info(f"Processing study {study_id} named {study['name']}")

            text = f"{study['summary']}\n{study['description']}"
            logger.debug(f"Calling embedding service.")
            tags = study['tags']
            embedding = await embeddings_service.generate_embedding(text)
            logger.info(f"Embeddings generated {len(embedding)}")
            enriched_data.append({
                "id": study_id,  # Use study ID as unique identifier
                "text": text,
                "embedding": embedding,
                "category": "genomics",
                "tags": tags
            })

        # Populate VectorDB
        logger.info(f"Calling vetctordb.populate with enriched data: {len(enriched_data)}")
        await vectordb_service.populate(enriched_data)  # Calls VectorDB `/populate`

        return {"status": "success", "message": f"Data from {file_path} successfully loaded into the Datalake."}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in the file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/export_subject_study")
async def export_subject_study_endpoint(data: ExportRequestStudies):
    """
    Endpoint to export subject study from MongoDB genomics database, to a JSON file.
    - file_path: Path to the JSON file that will be created to contain subject studies.
    - subject_id: Subject ID of the study individual.
    """
    try:
        output_file = data.file_path
        subject_id = data.subject_id
        logger.info(f"Exporting studied for subject {subject_id} to file: {output_file}")

        # Call the exporter function
        export_subject_studies_to_json(subject_id, output_file)
     
        return {"status": "success", "message": f"Subject studies from genomics database successfully exported to {output_file}."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
