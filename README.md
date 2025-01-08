# VitalEdge Genomics Tubes

VitalEdge Genomics Tubes - TUBES to move data around Genomics PIPE and Genomics FLASK

The **VitalEdge Genomics Tubes** is a microservice within the VitalEdge ecosystem designed to process, transform, and load datasets into the centralized **vitaledge-datalake**. It ensures that incoming data, received via **DataBridge**, is cleaned, validated, and inserted into structured database tables for use by downstream systems like analytics pipelines and RxGen.

---

## Features

- **Data Transformation and Normalization**:
  - Processes datasets such as PharmGKB annotations, clinical trial metadata, and patient-specific genomic files.
- **Database Integration**:
  - Inserts processed data into PostgreSQL with referential integrity.
- **REST API**:
  - Programmatic access for triggering data loading tasks and monitoring their progress.
- **Extensible Design**:
  - Modular architecture allows support for new data types with minimal changes.
- **Logging and Monitoring**:
  - Tracks processing tasks, logs errors, and provides detailed feedback.

---

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Running the API](#running-the-api)
  - [Using the REST API](#using-the-rest-api)
- [Database Schema](#database-schema)
- [Future Enhancements](#future-enhancements)

---

## Requirements

- **Python**: Version 3.11 or higher
- **PostgreSQL**: Version 14 or higher with TimescaleDB extension
- **Dependencies**:
  - Python Libraries: `pandas`, `sqlalchemy`, `psycopg2`, `fastapi`, `uvicorn`

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/vitaledge/vitaledge-data-loader.git
   cd vitaledge-data-loader
   ```

2. **Set Up the Environment**:
   - Using Conda:
     ```bash
     conda create -n data-loader python=3.11
     conda activate data-loader
     pip install -r requirements.txt
     ```

3. **Set Up the Database**:
   - Ensure PostgreSQL is running and configured.
   - Create the required tables (see [Database Schema](#database-schema)).

4. **Configure the Application**:
   - Copy the sample `.env.example` file:
     ```bash
     cp .env.example .env
     ```
   - Update `.env` with database credentials and configuration values.

---

## Configuration

### Environment Variables

The application uses the `.env` file for configuration. Example:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vitaledge_datalake
DB_USER=your_username
DB_PASS=your_password
LOG_LEVEL=info
INPUT_FOLDER=data/loader/queued
ARCHIVE_FOLDER=data/loader/archive
```

---

## Usage

### Running the API

Start the FastAPI server:
```bash
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

### Using the REST API

1. **Trigger Data Loading**:
   - Endpoint: `/load`
   - Example:
     ```bash
     curl -X POST http://localhost:8000/load \
          -H "Content-Type: application/json" \
          -d '{"file_path": "data/loader/queued/pharmgkb_var_drug_ann.tsv", "type": "pharmgkb"}'
     ```

2. **Validate an Input File**:
   - Endpoint: `/validate`
   - Example:
     ```bash
     curl -X POST http://localhost:8000/validate \
          -H "Content-Type: application/json" \
          -d '{"file_path": "data/loader/queued/pharmgkb_var_drug_ann.tsv"}'
     ```

3. **Check Task Status**:
   - Endpoint: `/status`
   - Example:
     ```bash
     curl -X GET "http://localhost:8000/status?task_id=12345"
     ```

---

## Database Schema

### Example: Pharmacogenomic Annotations Table

This table stores catalog data used by RxGen for variant annotation:
```sql
CREATE TABLE pharmacogenomic_annotations (
    variant_id VARCHAR PRIMARY KEY,
    gene VARCHAR NOT NULL,
    drug_id VARCHAR NOT NULL,
    significance TEXT,
    notes TEXT,
    direction_of_effect TEXT
);
```

### Example: Data Loader Logs Table

This table tracks the status of data loading tasks:
```sql
CREATE TABLE data_loader_logs (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR NOT NULL UNIQUE,
    file_name VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW() ON UPDATE NOW()
);
```

---

## Future Enhancements

- **Parallel Processing**:
  - Implement chunked or distributed data loading for large files.
- **Dynamic Schema Support**:
  - Automatically map new data types to database tables.
- **Web Dashboard**:
  - Add a monitoring UI for task statuses and logs.
- **Data Lineage**:
  - Track the source and transformation history of each dataset.

---

## Contributing

We welcome contributions! Please fork the repository and submit a pull request.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Contact

For questions or support, please contact the **VitalEdge Development Team** at `support@vitaledge.org`.

---
