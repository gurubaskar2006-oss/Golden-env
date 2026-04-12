from __future__ import annotations

from .models import DispatchState
from .task_bank import TASKS, list_task_cards

SCORE_EPSILON = 1e-3


def _clamp_score_metric(value: float) -> float:
    return max(SCORE_EPSILON, min(1.0 - SCORE_EPSILON, value))


def grade_state(state: DispatchState) -> dict[str, float]:
    weighted_ratio = (
        min(state.weighted_survival_gained / state.optimal_weighted_survival, 1.0)
        if state.optimal_weighted_survival > 0
        else 1.0
    )
    coverage_ratio = (
        len(state.resolved_incident_ids) / state.total_incidents if state.total_incidents else 1.0
    )
    critical_total = sum(1 for outcome in state.incident_outcomes if outcome.triage == "108")
    critical_resolved = sum(
        1 for outcome in state.incident_outcomes if outcome.triage == "108" and outcome.resolved
    )
    critical_coverage = critical_resolved / critical_total if critical_total else 1.0
    action_hygiene = max(
        0.0,
        1.0 - (state.invalid_actions / max(state.max_steps, 1)),
    )
    weighted_ratio = _clamp_score_metric(weighted_ratio)
    coverage_ratio = _clamp_score_metric(coverage_ratio)
    critical_coverage = _clamp_score_metric(critical_coverage)
    action_hygiene = _clamp_score_metric(action_hygiene)
    raw_score = (
        0.60 * weighted_ratio
        + 0.15 * coverage_ratio
        + 0.15 * critical_coverage
        + 0.10 * action_hygiene
    )
    score = _clamp_score_metric(raw_score)
    return {
        "score": round(score, 4),
        "weighted_ratio": round(weighted_ratio, 4),
        "coverage_ratio": round(coverage_ratio, 4),
        "critical_coverage": round(critical_coverage, 4),
        "action_hygiene": round(action_hygiene, 4),
    }


def task_cards() -> list[dict[str, str]]:
    return list_task_cards()


__all__ = ["TASKS", "grade_state", "task_cards"]
