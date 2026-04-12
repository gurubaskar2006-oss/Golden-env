from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from golden_hour_dispatch_env.graders import grade_state

SCORE_EPSILON = 1e-2
FALLBACK_SCORE = SCORE_EPSILON


def _clamp_score(value: float) -> float:
    return round(max(SCORE_EPSILON, min(1.0 - SCORE_EPSILON, float(value))), 4)


def _score_from_state_like(value: Any) -> float | None:
    if value is None:
        return None

    task_score = getattr(value, "task_score", None)
    if task_score is not None:
        return _clamp_score(task_score)

    if hasattr(value, "incident_outcomes") and hasattr(value, "max_steps"):
        return _clamp_score(grade_state(value)["score"])

    score_breakdown = getattr(value, "score_breakdown", None)
    if isinstance(score_breakdown, Mapping) and "score" in score_breakdown:
        return _clamp_score(score_breakdown["score"])

    metadata = getattr(value, "metadata", None)
    if isinstance(metadata, Mapping) and "task_score_preview" in metadata:
        return _clamp_score(metadata["task_score_preview"])

    return None


def _score_from_mapping(payload: Mapping[str, Any]) -> float | None:
    direct_score_keys = (
        "task_score",
        "score",
        "task_score_preview",
        "final_score",
        "grader_score",
    )
    for key in direct_score_keys:
        if key in payload and isinstance(payload[key], (int, float)):
            return _clamp_score(payload[key])

    nested_keys = (
        "state",
        "observation",
        "metadata",
        "score_breakdown",
        "episode_grade",
        "result",
        "final_state",
        "final_observation",
        "payload",
    )
    for key in nested_keys:
        if key in payload:
            nested = _extract_score(payload[key])
            if nested is not None:
                return nested

    return None


def _score_from_sequence(items: Sequence[Any]) -> float | None:
    for item in items:
        nested = _extract_score(item)
        if nested is not None:
            return nested
    return None


def _extract_score(value: Any) -> float | None:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return _clamp_score(value)

    state_like = _score_from_state_like(value)
    if state_like is not None:
        return state_like

    if hasattr(value, "state"):
        state_attr = getattr(value, "state")
        nested_state = state_attr() if callable(state_attr) else state_attr
        nested = _extract_score(nested_state)
        if nested is not None:
            return nested

    if isinstance(value, Mapping):
        return _score_from_mapping(value)

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return _score_from_sequence(value)

    return None


def _score_for_task(expected_task_id: str, *args: Any, **kwargs: Any) -> float:
    for candidate in [*args, *kwargs.values()]:
        score = _extract_score(candidate)
        if score is not None:
            return score
    return FALLBACK_SCORE


def grade_easy_single_critical(*args: Any, **kwargs: Any) -> float:
    return _score_for_task("easy_single_critical", *args, **kwargs)


def grade_medium_split_queue(*args: Any, **kwargs: Any) -> float:
    return _score_for_task("medium_split_queue", *args, **kwargs)


def grade_hard_peak_hour_tradeoffs(*args: Any, **kwargs: Any) -> float:
    return _score_for_task("hard_peak_hour_tradeoffs", *args, **kwargs)


def grade_city_shift_priority_mix(*args: Any, **kwargs: Any) -> float:
    return _score_for_task("city_shift_priority_mix", *args, **kwargs)
