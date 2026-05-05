import os
from pathlib import Path
from typing import Any
from .base import Agent

SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go"}

class ScannerAgent(Agent):
    name = "scanner-agent"

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        repo_path = Path(context["repo_path"]).resolve()
        if not repo_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

        files: list[dict[str, Any]] = []
        for path in repo_path.rglob("*"):
            if not path.is_file() or path.suffix not in SUPPORTED_EXTENSIONS:
                continue
            if any(part in {".git", "node_modules", ".venv", "__pycache__", "dist", "build"} for part in path.parts):
                continue

            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            lines = content.splitlines()
            files.append({
                "path": str(path.relative_to(repo_path)),
                "absolute_path": str(path),
                "extension": path.suffix,
                "line_count": len(lines),
                "content": content,
            })

        return {
            **context,
            "repo_path": str(repo_path),
            "files": files,
            "scan_stats": {
                "file_count": len(files),
                "total_lines": sum(item["line_count"] for item in files),
            },
        }
