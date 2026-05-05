import json
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.config import BACKEND_CORS_ORIGINS
from app.database import Base, engine, get_db
from app.models import ReviewReport, ReviewTask
from app.schemas import ReportOut, TaskCreate, TaskOut
from app.services.queue import task_queue

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Code Review / Tech Debt Governance Agent MVP",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event() -> None:
    await task_queue.start_worker()

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/tasks", response_model=TaskOut)
async def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> ReviewTask:
    task = ReviewTask(
        title=payload.title,
        repo_path=payload.repo_path,
        branch=payload.branch,
        status="created",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@app.post("/tasks/{task_id}/run", response_model=TaskOut)
async def run_task(task_id: int, db: Session = Depends(get_db)) -> ReviewTask:
    task = db.execute(select(ReviewTask).where(ReviewTask.id == task_id)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status in {"queued", "running"}:
        return task

    task.status = "queued"
    db.commit()
    db.refresh(task)
    await task_queue.enqueue(task.id)
    return task

@app.get("/tasks", response_model=list[TaskOut])
async def list_tasks(db: Session = Depends(get_db)) -> list[ReviewTask]:
    return list(db.execute(select(ReviewTask).order_by(desc(ReviewTask.id))).scalars().all())

@app.get("/tasks/{task_id}", response_model=TaskOut)
async def get_task(task_id: int, db: Session = Depends(get_db)) -> ReviewTask:
    task = db.execute(select(ReviewTask).where(ReviewTask.id == task_id)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/tasks/{task_id}/report", response_model=ReportOut)
async def get_report(task_id: int, db: Session = Depends(get_db)) -> ReportOut:
    report = db.execute(
        select(ReviewReport)
        .where(ReviewReport.task_id == task_id)
        .order_by(desc(ReviewReport.id))
    ).scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found yet")

    return ReportOut(
        id=report.id,
        task_id=report.task_id,
        summary=report.summary,
        risk_score=report.risk_score,
        findings=json.loads(report.findings_json),
        recommendations=json.loads(report.recommendations_json),
        generated_at=report.generated_at,
    )
