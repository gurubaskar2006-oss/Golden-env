from __future__ import annotations

from openenv.core.client_types import StepResult
from openenv.core.env_client import EnvClient

from .models import DispatchAction, DispatchObservation, DispatchState


class GoldenHourDispatchEnv(EnvClient[DispatchAction, DispatchObservation, DispatchState]):
    def _step_payload(self, action: DispatchAction) -> dict:
        return action.model_dump(exclude_none=True)

    def _parse_result(self, data: dict) -> StepResult[DispatchObservation]:
        observation = DispatchObservation(**data["observation"])
        return StepResult(
            observation=observation,
            reward=data.get("reward", observation.reward),
            done=data.get("done", observation.done),
        )

    def _parse_state(self, data: dict) -> DispatchState:
        return DispatchState(**data)

