from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    
    api_name: str = "Object Detection service"
    revision: str = "local"
    yolo_version: str = "yolov8x.pt"
    log_level: str = "DEBUG"
    telegram_token: str
    api_url: str = "http://localhost:8000/"



@cache
def get_settings():
    print("getting settings...")
    return Settings()