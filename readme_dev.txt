#### Starting to work on the project
cd /Users/samseatt/projects/vitaledge/vitaledge-genomics-tubes

# conda create -n vitaledge-genomics-tubes python=3.11 -y
conda activate vitaledge-genomics-tubes

# pip-compile requirements.in
pip install -r requirements.txt


#### Starting server
uvicorn app.main:app --host 0.0.0.0 --port 8020 --reload

# To work with the database
psql -d vitaledge_datalake

#### Testing endpoints
## Test database connection - test-db-connection
curl http://localhost:8020/studies/test-db-connection

## Load Patient Studies - load_patient_study
# Expected response: {"status":"success","message":"Data from /Users/samseatt/projects/vitaledge/data/loader/queued/genomic_studies.json successfully loaded into the Datalake."}
curl -X POST -H "Content-Type: application/json" -d '{"file_path": "/Users/samseatt/projects/vitaledge/data/loader/queued/genomic_studies_new.json", "subject_id": "672124a0388b9710c0e0b268"}'  http://localhost:8020/studies/load_subject_study
curl -X POST -H "Content-Type: application/json" -d '{"file_path": "/Users/samseatt/projects/vitaledge/data/loader/queued/genomic_studies_test_patient.json", "subject_id": "test_patient"}'  http://localhost:8020/studies/load_subject_study

## Export patient study from MongoDB genomic_pipeline_db database to a JSON file - export_patient_study
curl -X POST -H "Content-Type: application/json" -d '{"file_path": "/Users/samseatt/projects/vitaledge/data/loader/queued/genomic_studies_new.json", "subject_id": "672124a0388b9710c0e0b268"}'  http://localhost:8020/studies/export_subject_study
curl -X POST -H "Content-Type: application/json" -d '{"file_path": "/Users/samseatt/projects/vitaledge/data/loader/queued/genomic_studies_test_patient.json", "subject_id": "test_patient"}'  http://localhost:8020/studies/export_subject_study

