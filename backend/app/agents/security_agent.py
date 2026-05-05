import re
from typing import Any
from .base import Agent

SECRET_PATTERNS = [
    ("hardcoded_api_key", re.compile(r"(api[_-]?key|token|secret|password)\s*=\s*['\"][^'\"]{8,}['\"]", re.IGNORECASE)),
    ("private_key", re.compile(r"BEGIN\s+(RSA\s+)?PRIVATE\s+KEY")),
]

DANGEROUS_CALLS = [
    ("eval_usage", re.compile(r"\beval\s*\(")),
    ("shell_true", re.compile(r"shell\s*=\s*True")),
    ("exec_usage", re.compile(r"\bexec\s*\(")),
]

class SecurityAgent(Agent):
    name = "security-agent"

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []

        for file in context.get("files", []):
            lines = file["content"].splitlines()
            for idx, line in enumerate(lines, start=1):
                for finding_type, pattern in SECRET_PATTERNS:
                    if pattern.search(line):
                        findings.append({
                            "agent": self.name,
                            "type": finding_type,
                            "severity": "high",
                            "file": file["path"],
                            "line": idx,
                            "message": "Possible hardcoded secret found. Move it to environment variables or a secret manager.",
                        })

                for finding_type, pattern in DANGEROUS_CALLS:
                    if pattern.search(line):
                        findings.append({
                            "agent": self.name,
                            "type": finding_type,
                            "severity": "high",
                            "file": file["path"],
                            "line": idx,
                            "message": "Potentially dangerous dynamic execution or shell invocation detected.",
                        })

        return {**context, "security_findings": findings}
