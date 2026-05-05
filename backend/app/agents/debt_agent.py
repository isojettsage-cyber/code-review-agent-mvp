import re
from typing import Any
from .base import Agent

class DebtAgent(Agent):
    name = "tech-debt-agent"

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []

        for file in context.get("files", []):
            content = file["content"]
            lines = content.splitlines()

            # Rule 1: very long files
            if file["line_count"] > 300:
                findings.append({
                    "agent": self.name,
                    "type": "large_file",
                    "severity": "medium",
                    "file": file["path"],
                    "line": 1,
                    "message": f"File has {file['line_count']} lines; consider splitting by responsibility.",
                })

            # Rule 2: TODO/FIXME/HACK markers
            for idx, line in enumerate(lines, start=1):
                if re.search(r"\b(TODO|FIXME|HACK)\b", line, re.IGNORECASE):
                    findings.append({
                        "agent": self.name,
                        "type": "debt_marker",
                        "severity": "low",
                        "file": file["path"],
                        "line": idx,
                        "message": "Found TODO/FIXME/HACK marker; convert it to a tracked issue or resolve it.",
                    })

            # Rule 3: functions that are too long, simple heuristic
            function_start = None
            function_name = None
            indent = None
            for idx, line in enumerate(lines, start=1):
                match = re.match(r"^(\s*)(def|function)\s+([A-Za-z0-9_]+)", line)
                if match:
                    function_start = idx
                    function_name = match.group(3)
                    indent = len(match.group(1))
                    continue

                if function_start and idx - function_start > 80:
                    current_indent = len(line) - len(line.lstrip(" "))
                    if line.strip() and current_indent <= (indent or 0):
                        findings.append({
                            "agent": self.name,
                            "type": "large_function",
                            "severity": "medium",
                            "file": file["path"],
                            "line": function_start,
                            "message": f"Function '{function_name}' appears longer than 80 lines; extract smaller units.",
                        })
                        function_start = None
                        function_name = None
                        indent = None

        return {**context, "debt_findings": findings}
