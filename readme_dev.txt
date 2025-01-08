#### Starting to work on the project
cd /Users/samseatt/projects/vitaledge/vitaledge-genomics-loader

# conda create -n vitaledge-genomics-loader python=3.11 -y
conda activate vitaledge-genomics-loader

# pip-compile requirements.in
pip install -r requirements.txt


#### Starting server
uvicorn app.main:app --host 0.0.0.0 --port 8020 --reload


#### Testing endpoints
## Test database connection - test-db-connection
curl http://localhost:8020/test-db-connection

## Load Patient Studies - load_patient_study
# Expected response: {"status":"success","message":"Data from /Users/samseatt/projects/vitaledge/data/loader/queued/genomic_studies.json successfully loaded into the Datalake."}
curl -X POST -H "Content-Type: application/json" -d '{"file_path": "/Users/samseatt/projects/vitaledge/data/loader/queued/genomic_studies.json"}'  http://localhost:8020/load_patient_study

## Export patient study from MongoDB genomic_pipeline_db database to a JSON file - export_patient_study
curl -X POST -H "Content-Type: application/json" -d '{"file_path": "/Users/samseatt/projects/vitaledge/data/loader/queued/genomic_studies_new.json", "patient_id": "672124a0388b9710c0e0b268"}'  http://localhost:8020/export_patient_study

