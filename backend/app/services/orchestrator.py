import json
from typing import Any
from app.agents.scanner_agent import ScannerAgent
from app.agents.debt_agent import DebtAgent
from app.agents.security_agent import SecurityAgent
from app.agents.quality_agent import QualityAgent
from app.agents.report_agent import ReportAgent

class MultiAgentOrchestrator:
    """Sequential multi-agent workflow.

    MVP flow:
    ScannerAgent -> DebtAgent + SecurityAgent + QualityAgent -> ReportAgent

    The middle agents can be parallelized later. For the MVP, sequential execution
    makes logs and debugging easier.
    """

    def __init__(self) -> None:
        self.scanner = ScannerAgent()
        self.debt = DebtAgent()
        self.security = SecurityAgent()
        self.quality = QualityAgent()
        self.reporter = ReportAgent()

    async def run(self, task: dict[str, Any]) -> dict[str, Any]:
        context = {
            "task_id": task["id"],
            "title": task["title"],
            "repo_path": task["repo_path"],
            "branch": task["branch"],
            "logs": [],
        }

        for agent in [self.scanner, self.debt, self.security, self.quality, self.reporter]:
            context["logs"].append(f"Running {agent.name}")
            context = await agent.run(context)

        return context["report"]

def report_to_json(report: dict[str, Any]) -> tuple[str, str]:
    return (
        json.dumps(report.get("findings", []), ensure_ascii=False),
        json.dumps(report.get("recommendations", []), ensure_ascii=False),
    )
