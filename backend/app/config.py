import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agent_mvp.db")
FEISHU_WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL", "")
BACKEND_CORS_ORIGINS = [
    item.strip()
    for item in os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:5173").split(",")
    if item.strip()
]
