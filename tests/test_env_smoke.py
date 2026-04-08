from golden_hour_dispatch_env.graders import grade_state
from golden_hour_dispatch_env.models import DispatchAction
from golden_hour_dispatch_env.server.dispatch_environment import GoldenHourDispatchEnvironment
from golden_hour_dispatch_env.task_bank import TASKS


def test_tasks_can_reset_and_finish() -> None:
    for task_id in TASKS:
        env = GoldenHourDispatchEnvironment(task_id=task_id)
        observation = env.reset()
        assert observation.task.task_id == task_id
        assert 0.0 < observation.reward_breakdown.total_reward < 1.0
        while not observation.done:
            assert observation.available_dispatches
            best = max(observation.available_dispatches, key=lambda item: item.weighted_survival)
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
        assert 0.0 <= graded["score"] <= 1.0
        assert env.state.last_reward_breakdown.total_reward == observation.reward_breakdown.total_reward
