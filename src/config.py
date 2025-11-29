import os

class Settings:
    # UPDATE THIS WITH YOUR PASSWORD
    DATABASE_URL = "postgresql+asyncpg://postgres:9548911@localhost:5432/aivendance_db"

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # DeepFace handles its own model paths, so we don't need a manual dir here anymore
    
    # Websocket
    WS_HEARTBEAT_INTERVAL = 30

settings = Settings()