from collections import Counter
from typing import Any
from .base import Agent

SEVERITY_WEIGHT = {
    "low": 1,
    "medium": 4,
    "high": 8,
}

class ReportAgent(Agent):
    name = "report-agent"

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        findings = []
        findings.extend(context.get("debt_findings", []))
        findings.extend(context.get("security_findings", []))
        findings.extend(context.get("quality_findings", []))

        severity_counter = Counter(item.get("severity", "low") for item in findings)
        raw_score = sum(SEVERITY_WEIGHT.get(item.get("severity", "low"), 1) for item in findings)
        risk_score = min(100, raw_score)

        recommendations = self._build_recommendations(findings)
        summary = (
            f"Scanned {context.get('scan_stats', {}).get('file_count', 0)} files and "
            f"{context.get('scan_stats', {}).get('total_lines', 0)} lines. "
            f"Found {len(findings)} issues: "
            f"{severity_counter.get('high', 0)} high, "
            f"{severity_counter.get('medium', 0)} medium, "
            f"{severity_counter.get('low', 0)} low. "
            f"Risk score: {risk_score}/100."
        )

        return {
            **context,
            "report": {
                "summary": summary,
                "risk_score": risk_score,
                "findings": findings,
                "recommendations": recommendations,
            },
        }

    def _build_recommendations(self, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        recommendations = []
        by_type = Counter(item["type"] for item in findings)

        if by_type.get("hardcoded_api_key") or by_type.get("private_key"):
            recommendations.append({
                "priority": "P0",
                "title": "Remove possible hardcoded secrets",
                "action": "Move secrets into environment variables or a managed secret store, then rotate exposed credentials.",
            })

        if by_type.get("eval_usage") or by_type.get("shell_true") or by_type.get("exec_usage"):
            recommendations.append({
                "priority": "P0",
                "title": "Review dangerous execution paths",
                "action": "Replace dynamic execution with explicit allow-listed logic and sanitize all user-controlled inputs.",
            })

        if by_type.get("large_function") or by_type.get("large_file"):
            recommendations.append({
                "priority": "P1",
                "title": "Break down large modules and functions",
                "action": "Split code by bounded responsibility and add regression tests before refactoring.",
            })

        if by_type.get("missing_docstring") or by_type.get("too_many_args"):
            recommendations.append({
                "priority": "P2",
                "title": "Improve maintainability",
                "action": "Add concise docstrings, reduce long parameter lists, and clarify ownership of complex functions.",
            })

        if not recommendations:
            recommendations.append({
                "priority": "P3",
                "title": "No urgent risk detected",
                "action": "Keep the baseline scan in CI and compare risk score changes on every pull request.",
            })

        return recommendations
