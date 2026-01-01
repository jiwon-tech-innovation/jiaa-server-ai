import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "JIAA Intelligence Worker"
    API_V1_STR: str = "/api/v1"
    
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_S3_REGION: str = os.getenv("AWS_S3_REGION", os.getenv("AWS_REGION", "us-east-1"))

    class Config:
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()
