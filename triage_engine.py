from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


@dataclass(frozen=True)
class HistoricalDefect:
    key: str
    summary: str
    subsystem: str
    owner_team: str
    root_cause: str


HISTORICAL_DEFECTS: list[HistoricalDefect] = [
    HistoricalDefect(
        key="APP-1021",
        summary="Login API returns 500 when auth provider times out",
        subsystem="Authentication",
        owner_team="Identity Platform",
        root_cause="Missing timeout fallback in auth adapter",
    ),
    HistoricalDefect(
        key="WEB-887",
        summary="Checkout page freezes after coupon is applied",
        subsystem="Checkout UI",
        owner_team="Web Experience",
        root_cause="State update loop triggered by discount recalculation",
    ),
    HistoricalDefect(
        key="OPS-334",
        summary="Nightly ETL job skips records with null country",
        subsystem="Data Pipeline",
        owner_team="Data Engineering",
        root_cause="Schema validation too strict for optional fields",
    ),
]


def extract_issue_key(jira_link: str) -> str:
    text = jira_link.strip().upper()
    if not text:
        return "UNKNOWN"
    if "/" in text:
        path = urlparse(text).path
        parts = [p for p in path.split("/") if p]
        if parts:
            return parts[-1].upper()
    return text


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def _predict_owner_and_subsystem(text: str) -> tuple[str, str]:
    if _contains_any(text, ("login", "auth", "token", "oauth", "password")):
        return "Identity Platform", "Authentication"
    if _contains_any(text, ("checkout", "cart", "payment", "coupon", "order")):
        return "Web Experience", "Checkout UI"
    if _contains_any(text, ("etl", "batch", "pipeline", "warehouse", "sync")):
        return "Data Engineering", "Data Pipeline"
    if _contains_any(text, ("deploy", "k8s", "infra", "latency", "timeout")):
        return "SRE", "Platform Infrastructure"
    return "Core Platform", "General Services"


def _generate_probable_root_causes(text: str) -> list[str]:
    causes: list[str] = []
    if _contains_any(text, ("500", "exception", "null", "none")):
        causes.append("Unhandled edge-case or null input in backend logic")
    if _contains_any(text, ("timeout", "slow", "latency")):
        causes.append("Missing timeout/retry strategy for downstream dependency")
    if _contains_any(text, ("ui", "freeze", "render", "browser")):
        causes.append("Client-side state management regression")
    if not causes:
        causes.append("Recent code regression requiring targeted log/trace analysis")
    return causes


def _find_similar_defects(text: str, limit: int = 2) -> list[HistoricalDefect]:
    tokens = {t for t in text.lower().split() if len(t) > 3}

    def score(item: HistoricalDefect) -> int:
        body = f"{item.summary} {item.subsystem} {item.root_cause}".lower()
        return sum(token in body for token in tokens)

    ranked = sorted(HISTORICAL_DEFECTS, key=score, reverse=True)
    return ranked[:limit]


def triage_defect(jira_link: str, notes: str = "") -> dict[str, Any]:
    issue_key = extract_issue_key(jira_link)
    combined = f"{jira_link.strip()} {notes.strip()}".strip()

    owner_team, subsystem = _predict_owner_and_subsystem(combined)
    root_causes = _generate_probable_root_causes(combined)
    similar = _find_similar_defects(combined)

    summary = notes.strip() or f"Defect reported in {subsystem}"
    next_action = (
        f"Route to {owner_team} and reproduce in {subsystem}; "
        "collect logs and compare with similar incidents before assigning fix owner."
    )
    rca_summary = (
        f"{issue_key} is likely owned by {owner_team} ({subsystem}). "
        f"Most probable cause: {root_causes[0]}."
    )

    return {
        "defect_summary": summary,
        "predicted_owner_team": owner_team,
        "predicted_subsystem": subsystem,
        "probable_root_causes": root_causes,
        "similar_historical_defects": [
            {
                "key": item.key,
                "summary": item.summary,
                "owner_team": item.owner_team,
                "subsystem": item.subsystem,
                "root_cause": item.root_cause,
            }
            for item in similar
        ],
        "recommended_next_action": next_action,
        "rca_summary": rca_summary,
    }
