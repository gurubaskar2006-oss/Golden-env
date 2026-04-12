from golden_hour_dispatch_env.graders import grade_state
from golden_hour_dispatch_env.models import DispatchAction
from golden_hour_dispatch_env.server.dispatch_environment import GoldenHourDispatchEnvironment
from golden_hour_dispatch_env.task_bank import TASKS
from task_graders import (
    grade_city_shift_priority_mix,
    grade_easy_single_critical,
    grade_hard_peak_hour_tradeoffs,
    grade_medium_split_queue,
)


TASK_GRADERS = {
    "easy_single_critical": grade_easy_single_critical,
    "medium_split_queue": grade_medium_split_queue,
    "hard_peak_hour_tradeoffs": grade_hard_peak_hour_tradeoffs,
    "city_shift_priority_mix": grade_city_shift_priority_mix,
}


def _best_priority_candidate(observation):
    incident_by_id = {incident.incident_id: incident for incident in observation.incidents}
    critical_candidates = [
        candidate
        for candidate in observation.available_dispatches
        if incident_by_id[candidate.incident_id].triage == "108"
    ]
    candidate_pool = critical_candidates or observation.available_dispatches
    return max(
        candidate_pool,
        key=lambda item: (item.weighted_survival, item.predicted_survival, -item.scene_eta_minutes),
    )


def test_tasks_can_reset_and_finish() -> None:
    for task_id in TASKS:
        env = GoldenHourDispatchEnvironment(task_id=task_id)
        observation = env.reset()
        assert observation.task.task_id == task_id
        assert 0.0 < observation.reward_breakdown.total_reward < 1.0
        while not observation.done:
            assert observation.available_dispatches
            best = _best_priority_candidate(observation)
            observation = env.step(
                DispatchAction(
                    ambulance_id=best.ambulance_id,
                    incident_id=best.incident_id,
                    hospital_id=best.hospital_id,
                    use_green_corridor=best.use_green_corridor,
                )
            )
            assert observation.reward == observation.reward_breakdown.total_reward
        graded = grade_state(env.state)
        assert 0.0 < graded["score"] < 1.0
        assert 0.7 < TASK_GRADERS[task_id](env.state) < 1.0
        assert env.state.last_reward_breakdown.total_reward == observation.reward_breakdown.total_reward


def test_task_graders_penalize_missing_payloads() -> None:
    for grader in TASK_GRADERS.values():
        assert grader(None) == 0.01


def test_incidents_have_explicit_hospital_specialties() -> None:
    for task in TASKS.values():
        for incident in task.incidents:
            assert incident.required_specialty in {"cardiac", "trauma", "maternity", "stroke"}
