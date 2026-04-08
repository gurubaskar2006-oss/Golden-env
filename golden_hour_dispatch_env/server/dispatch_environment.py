from __future__ import annotations

from uuid import uuid4

from openenv.core.env_server.interfaces import Environment

from ..models import DispatchAction, DispatchObservation, DispatchState
from ..simulator import (
    apply_action,
    build_observation,
    build_state,
    combine_reward_breakdowns,
    create_episode,
    force_finish,
)
from ..task_bank import TASKS


class GoldenHourDispatchEnvironment(Environment[DispatchAction, DispatchObservation, DispatchState]):
    def __init__(self, task_id: str | None = None):
        self._task_ids = list(TASKS.keys())
        self._task_index = 0
        self._fixed_task_id = task_id
        self._episode_id = str(uuid4())
        self._steps_taken = 0
        self._snapshot = None
        self._state_cache: DispatchState | None = None
        self._last_observation: DispatchObservation | None = None

    def reset(self) -> DispatchObservation:
        task_id = self._fixed_task_id or self._task_ids[self._task_index % len(self._task_ids)]
        if self._fixed_task_id is None:
            self._task_index += 1
        self._episode_id = str(uuid4())
        self._steps_taken = 0
        self._snapshot = create_episode(task_id)
        self._state_cache = build_state(self._snapshot, self._steps_taken)
        self._last_observation = build_observation(
            self._snapshot,
            self._steps_taken,
            reward_breakdown=self._snapshot.last_reward_breakdown,
        )
        return self._last_observation

    def step(self, action: DispatchAction) -> DispatchObservation:
        if self._snapshot is None:
            return self.reset()

        self._steps_taken += 1
        reward_breakdown = apply_action(self._snapshot, action)
        if self._steps_taken >= self._snapshot.task_config.max_steps and self._snapshot.done_reason is None:
            reward_breakdown = combine_reward_breakdowns(
                reward_breakdown,
                force_finish(self._snapshot, "step_budget_exhausted"),
            )
        self._state_cache = build_state(self._snapshot, self._steps_taken)
        self._last_observation = build_observation(
            self._snapshot,
            self._steps_taken,
            reward_breakdown=reward_breakdown,
        )
        return self._last_observation

    @property
    def state(self) -> DispatchState:
        if self._snapshot is None:
            self.reset()
        if self._state_cache is None:
            self._state_cache = build_state(self._snapshot, self._steps_taken)
        return self._state_cache

    @property
    def last_observation(self) -> DispatchObservation:
        if self._last_observation is None:
            return self.reset()
        return self._last_observation
