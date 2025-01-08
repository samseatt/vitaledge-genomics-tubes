# app/main.py
from fastapi import FastAPI
from app.api.routes import router
from app.utils.logging import setup_logging
# from app.api.routes.studies import router as studies_router

# Set up logging for the application
setup_logging(log_level="INFO", log_file="logs/vitaledge_genomics_handler.log")

app = FastAPI()

# Include the routes
app.include_router(router)
