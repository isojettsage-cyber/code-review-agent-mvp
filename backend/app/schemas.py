from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(default="Code Review / Tech Debt Scan")
    repo_path: str = Field(default="./app/sample_repo")
    branch: str = Field(default="main")

class TaskOut(BaseModel):
    id: int
    title: str
    repo_path: str
    branch: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True

class ReportOut(BaseModel):
    id: int
    task_id: int
    summary: str
    risk_score: int
    findings: List[dict[str, Any]]
    recommendations: List[dict[str, Any]]
    generated_at: datetime
