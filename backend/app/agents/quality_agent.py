import ast
from typing import Any
from .base import Agent

class QualityAgent(Agent):
    name = "quality-agent"

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []

        for file in context.get("files", []):
            if file["extension"] != ".py":
                continue

            try:
                tree = ast.parse(file["content"])
            except SyntaxError as exc:
                findings.append({
                    "agent": self.name,
                    "type": "syntax_error",
                    "severity": "high",
                    "file": file["path"],
                    "line": exc.lineno or 1,
                    "message": f"Python syntax error: {exc.msg}",
                })
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not ast.get_docstring(node):
                        findings.append({
                            "agent": self.name,
                            "type": "missing_docstring",
                            "severity": "low",
                            "file": file["path"],
                            "line": node.lineno,
                            "message": f"Function '{node.name}' has no docstring.",
                        })

                    arg_count = len(node.args.args)
                    if arg_count > 6:
                        findings.append({
                            "agent": self.name,
                            "type": "too_many_args",
                            "severity": "medium",
                            "file": file["path"],
                            "line": node.lineno,
                            "message": f"Function '{node.name}' has {arg_count} arguments; consider an options object.",
                        })

        return {**context, "quality_findings": findings}
