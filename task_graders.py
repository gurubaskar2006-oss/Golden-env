from __future__ import annotations

from typing import Any

from golden_hour_dispatch_env.graders import grade_state

SCORE_EPSILON = 1e-4


def _extract_state(*args: Any, **kwargs: Any):
    for value in [*args, *kwargs.values()]:
        if value is None:
            continue
        if hasattr(value, "task_score") and hasattr(value, "incident_outcomes"):
            return value
        if hasattr(value, "state"):
            state_attr = getattr(value, "state")
            return state_attr() if callable(state_attr) else state_attr
    raise ValueError("Unable to extract environment state for grading.")


def _score_for_task(expected_task_id: str, *args: Any, **kwargs: Any) -> float:
    state = _extract_state(*args, **kwargs)
    score = float(state.task_score if getattr(state, "task_score", None) is not None else grade_state(state)["score"])
    score = max(SCORE_EPSILON, min(1.0 - SCORE_EPSILON, score))
    return round(score, 4)


def grade_easy_single_critical(*args: Any, **kwargs: Any) -> float:
    return _score_for_task("easy_single_critical", *args, **kwargs)


def grade_medium_split_queue(*args: Any, **kwargs: Any) -> float:
    return _score_for_task("medium_split_queue", *args, **kwargs)


def grade_hard_peak_hour_tradeoffs(*args: Any, **kwargs: Any) -> float:
    return _score_for_task("hard_peak_hour_tradeoffs", *args, **kwargs)


def grade_city_shift_priority_mix(*args: Any, **kwargs: Any) -> float:
    return _score_for_task("city_shift_priority_mix", *args, **kwargs)
