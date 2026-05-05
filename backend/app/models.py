from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from .database import Base

class ReviewTask(Base):
    __tablename__ = "review_tasks"

    id = Column(Integer, primary_key=True, index=True)
    repo_path = Column(String(500), nullable=False)
    branch = Column(String(120), default="main")
    title = Column(String(255), nullable=False)
    status = Column(String(50), default="created", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)

class ReviewReport(Base):
    __tablename__ = "review_reports"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, index=True, nullable=False)
    summary = Column(Text, nullable=False)
    risk_score = Column(Integer, default=0)
    findings_json = Column(Text, nullable=False)
    recommendations_json = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
