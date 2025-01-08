import os
from dotenv import load_dotenv
from pydantic import Field, validator
from pydantic_settings import BaseSettings

# Load environment variables from .env
load_dotenv()


class Config(BaseSettings):
    # Database settings
    DB_NAME: str = Field(default="vitaledge_datalake", description="Database name")
    DB_USER: str = Field(default="samseatt", description="Database user")
    DB_PASSWORD: str = Field(default="password", description="Database password")
    DB_HOST: str = Field(default="localhost", description="Database host")
    DB_PORT: int = Field(default=5432, description="Database port")

    @property
    def DATABASE(self) -> dict:
        return {
            "dbname": self.DB_NAME,
            "user": self.DB_USER,
            "password": self.DB_PASSWORD,
            "host": self.DB_HOST,
            "port": self.DB_PORT,
        }

    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Embeddings service settings
    EMBEDDINGS_HOST: str = Field(default="127.0.0.1", description="Host for the Embeddings microservice")
    EMBEDDINGS_PORT: int = Field(default=8007, description="Port for the Embeddings microservice")
    EMBEDDINGS_URL: str = Field(default=None, description="URL for the Embeddings microservice")

    @validator("EMBEDDINGS_URL", pre=True, always=True)
    def set_embeddings_url(cls, v, values):
        # Generate URL if not explicitly set
        if not v:
            host = values.get("EMBEDDINGS_HOST", "127.0.0.1")
            port = values.get("EMBEDDINGS_PORT", 8007)
            return f"http://{host}:{port}"
        return v

    VECTORDB_HOST: str = Field(default="127.0.0.1", description="Host for the VectorDB microservice")
    VECTORDB_PORT: int = Field(default=8008, description="Port for the VectorDB microservice")
    VECTORDB_URL: str = Field(default=None, description="URL for the VectorDB microservice")

    @validator("VECTORDB_URL", pre=True, always=True)
    def set_vectordb_url(cls, v, values):
        if not v:
            host = values.get("VECTORDB_HOST", "127.0.0.1")
            port = values.get("VECTORDB_PORT", 8008)
            return f"http://{host}:{port}"
        return v
    
# Instantiate the config
config = Config()
