import asyncio
from datetime import datetime
from sqlalchemy import select
from app.database import SessionLocal
from app.models import ReviewReport, ReviewTask
from app.services.notifier import notify_feishu
from app.services.orchestrator import MultiAgentOrchestrator, report_to_json

class InMemoryTaskQueue:
    """Simple in-process queue for MVP.

    Production upgrade path:
    - Replace this with Celery / RQ / Dramatiq.
    - Put Redis or RabbitMQ behind it.
    - Add retry policy, dead-letter queue, and distributed locks.
    """

    def __init__(self) -> None:
        self.queue: asyncio.Queue[int] = asyncio.Queue()
        self.worker_started = False

    async def enqueue(self, task_id: int) -> None:
        await self.queue.put(task_id)

    async def start_worker(self) -> None:
        if self.worker_started:
            return
        self.worker_started = True
        asyncio.create_task(self._worker_loop())

    async def _worker_loop(self) -> None:
        while True:
            task_id = await self.queue.get()
            try:
                await self._process(task_id)
            finally:
                self.queue.task_done()

    async def _process(self, task_id: int) -> None:
        db = SessionLocal()
        orchestrator = MultiAgentOrchestrator()

        try:
            task = db.execute(select(ReviewTask).where(ReviewTask.id == task_id)).scalar_one()
            task.status = "running"
            task.started_at = datetime.utcnow()
            task.error = None
            db.commit()

            await notify_feishu("Code Review Agent started", f"Task #{task.id}: {task.title}")

            report = await orchestrator.run({
                "id": task.id,
                "title": task.title,
                "repo_path": task.repo_path,
                "branch": task.branch,
            })

            findings_json, recommendations_json = report_to_json(report)

            db_report = ReviewReport(
                task_id=task.id,
                summary=report["summary"],
                risk_score=report["risk_score"],
                findings_json=findings_json,
                recommendations_json=recommendations_json,
            )
            db.add(db_report)

            task.status = "completed"
            task.finished_at = datetime.utcnow()
            db.commit()

            await notify_feishu(
                "Code Review Agent completed",
                f"Task #{task.id} completed. Risk score: {report['risk_score']}/100",
            )

        except Exception as exc:
            db.rollback()
            task = db.execute(select(ReviewTask).where(ReviewTask.id == task_id)).scalar_one_or_none()
            if task:
                task.status = "failed"
                task.error = str(exc)
                task.finished_at = datetime.utcnow()
                db.commit()
            await notify_feishu("Code Review Agent failed", f"Task #{task_id}: {exc}")
        finally:
            db.close()

task_queue = InMemoryTaskQueue()
