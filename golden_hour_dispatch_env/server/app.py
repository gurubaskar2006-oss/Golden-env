from __future__ import annotations

import argparse
import inspect
import uvicorn
from fastapi.responses import HTMLResponse
from fastapi import Body
from pydantic import BaseModel
from openenv.core.env_server.http_server import create_app
from openenv.core.env_server.serialization import serialize_observation
from openenv.core.env_server.types import ResetRequest, ResetResponse, SchemaResponse, StepRequest, StepResponse

from ..models import DispatchAction, DispatchObservation, DispatchState
from ..task_bank import DEFAULT_DEMO_TASK_ID, DEMO_TASKS, TASKS, list_demo_task_cards, list_task_cards, resolve_demo_task, ui_graph
from .dispatch_environment import GoldenHourDispatchEnvironment
from .dashboard import render_dashboard

app = create_app(
    GoldenHourDispatchEnvironment,
    DispatchAction,
    DispatchObservation,
    env_name="golden_hour_dispatch_env",
)

_http_env = GoldenHourDispatchEnvironment()
_demo_context: dict[str, object] = {
    "requested_task_id": DEFAULT_DEMO_TASK_ID,
    "requested_title": DEMO_TASKS[DEFAULT_DEMO_TASK_ID].title,
    "resolved_task_id": DEFAULT_DEMO_TASK_ID,
    "resolved_title": DEMO_TASKS[DEFAULT_DEMO_TASK_ID].title,
    "mode": "showcase",
    "bonus_multiplier": 1.18,
}


class DemoResetRequest(BaseModel):
    task_id: str | None = None
    seed: int | None = None


class DemoAutoRunRequest(BaseModel):
    max_steps: int | None = None


def _remove_default_route(path: str, method: str) -> None:
    app.router.routes = [
        route
        for route in app.router.routes
        if not (
            getattr(route, "path", None) == path
            and method in getattr(route, "methods", set())
        )
    ]


for _path, _method in (
    ("/reset", "POST"),
    ("/step", "POST"),
    ("/state", "GET"),
    ("/schema", "GET"),
):
    _remove_default_route(_path, _method)


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return render_dashboard()


def _set_env(task_id: str | None = None) -> GoldenHourDispatchEnvironment:
    global _http_env
    _http_env = GoldenHourDispatchEnvironment(task_id=task_id)
    return _http_env


def _current_env() -> GoldenHourDispatchEnvironment:
    return _http_env


def _heuristic_action(observation: DispatchObservation) -> DispatchAction:
    best = _best_candidate(observation)
    return DispatchAction(
        ambulance_id=best.ambulance_id,
        incident_id=best.incident_id,
        hospital_id=best.hospital_id,
        use_green_corridor=best.use_green_corridor,
        rationale="Auto-managed by the built-in dispatch policy.",
    )


def _best_candidate(observation: DispatchObservation):
    if not observation.available_dispatches:
        raise RuntimeError("No valid dispatch candidates remain.")

    incident_by_id = {incident.incident_id: incident for incident in observation.incidents}
    critical_candidates = [
        candidate
        for candidate in observation.available_dispatches
        if incident_by_id.get(candidate.incident_id) and incident_by_id[candidate.incident_id].triage == "108"
    ]
    candidate_pool = critical_candidates or observation.available_dispatches
    return max(
        candidate_pool,
        key=lambda candidate: (
            candidate.weighted_survival,
            candidate.predicted_survival,
            -candidate.scene_eta_minutes,
        ),
    )


def _dispatch_wave(max_actions: int | None = None) -> tuple[DispatchObservation, list[dict[str, object]]]:
    env = _current_env()
    observation = env.last_observation
    if observation.done:
        return observation, []

    anchor_minute = observation.current_time_minute
    trace: list[dict[str, object]] = []
    while not observation.done and observation.current_time_minute == anchor_minute and observation.available_dispatches:
        candidate = _best_candidate(observation)
        action = DispatchAction(
            ambulance_id=candidate.ambulance_id,
            incident_id=candidate.incident_id,
            hospital_id=candidate.hospital_id,
            use_green_corridor=candidate.use_green_corridor,
            rationale="Auto-managed by the built-in dispatch policy.",
        )
        observation = env.step(action)
        trace.append(
            {
                "minute": anchor_minute,
                "action": action.model_dump(mode="json"),
                "candidate": candidate.model_dump(mode="json"),
                "reward": observation.reward,
                "done": observation.done,
            }
        )
        if max_actions is not None and len(trace) >= max_actions:
            break
    return observation, trace


def _serialize_demo() -> dict[str, object]:
    env = _current_env()
    ops_score = round(
        min(float(env.state.task_score or 0.0) * float(_demo_context.get("bonus_multiplier", 1.0)), 1.0),
        4,
    )
    return {
        "observation": env.last_observation.model_dump(mode="json"),
        "state": env.state.model_dump(mode="json"),
        "done": env.last_observation.done,
        "demo_context": {
            **_demo_context,
            "ops_score": ops_score,
        },
    }


@app.post("/reset", response_model=ResetResponse, tags=["Environment Control"])
def reset(request: ResetRequest = Body(default_factory=ResetRequest)) -> ResetResponse:
    kwargs = {}
    reset_signature = inspect.signature(_http_env.reset)
    if "seed" in reset_signature.parameters and request.seed is not None:
        kwargs["seed"] = request.seed
    if "episode_id" in reset_signature.parameters and request.episode_id is not None:
        kwargs["episode_id"] = request.episode_id
    observation = _http_env.reset(**kwargs)
    return ResetResponse(**serialize_observation(observation))


@app.post("/step", response_model=StepResponse, tags=["Environment Control"])
def step(request: StepRequest) -> StepResponse:
    action = DispatchAction(**request.action)
    observation = _http_env.step(action)
    return StepResponse(**serialize_observation(observation))


@app.get("/state", response_model=DispatchState, tags=["State Management"])
def state() -> DispatchState:
    return _http_env.state


@app.get("/schema", response_model=SchemaResponse, tags=["Schema"])
def schema() -> SchemaResponse:
    return SchemaResponse(
        action=DispatchAction.model_json_schema(),
        observation=DispatchObservation.model_json_schema(),
        state=DispatchState.model_json_schema(),
    )


@app.get("/tasks")
def tasks() -> list[dict[str, str]]:
    return list_task_cards()


@app.get("/demo/config")
def demo_config() -> dict[str, object]:
    return {
        "tasks": list_demo_task_cards(),
        "graph": ui_graph(),
        "default_task_id": DEFAULT_DEMO_TASK_ID,
    }


@app.post("/demo/reset")
def demo_reset(request: DemoResetRequest = Body(default_factory=DemoResetRequest)) -> dict[str, object]:
    global _demo_context
    requested_task_id = request.task_id or DEFAULT_DEMO_TASK_ID
    if requested_task_id not in TASKS and requested_task_id not in {card["task_id"] for card in list_demo_task_cards()}:
        return {
            "error": f"Unknown task_id '{requested_task_id}'",
            "available_tasks": [card["task_id"] for card in list_demo_task_cards()],
        }
    task_id, _demo_context = resolve_demo_task(requested_task_id)
    env = _set_env(task_id)
    env.reset()
    return _serialize_demo()


@app.post("/demo/step")
def demo_step(request: StepRequest) -> dict[str, object]:
    action = DispatchAction(**request.action)
    observation = _current_env().step(action)
    payload = _serialize_demo()
    payload["observation"] = observation.model_dump(mode="json")
    payload["state"] = _current_env().state.model_dump(mode="json")
    return payload


@app.post("/demo/auto-step")
def demo_auto_step() -> dict[str, object]:
    env = _current_env()
    observation = env.last_observation
    if observation.done:
        payload = _serialize_demo()
        payload["action"] = None
        return payload

    candidate = _best_candidate(observation)
    action = DispatchAction(
        ambulance_id=candidate.ambulance_id,
        incident_id=candidate.incident_id,
        hospital_id=candidate.hospital_id,
        use_green_corridor=candidate.use_green_corridor,
        rationale="Auto-managed by the built-in dispatch policy.",
    )
    next_observation = env.step(action)
    payload = _serialize_demo()
    payload["observation"] = next_observation.model_dump(mode="json")
    payload["state"] = env.state.model_dump(mode="json")
    payload["action"] = action.model_dump(mode="json")
    payload["candidate"] = candidate.model_dump(mode="json")
    return payload


@app.post("/demo/auto-wave")
def demo_auto_wave() -> dict[str, object]:
    observation, trace = _dispatch_wave()
    payload = _serialize_demo()
    payload["observation"] = observation.model_dump(mode="json")
    payload["state"] = _current_env().state.model_dump(mode="json")
    payload["trace"] = trace
    payload["steps_taken"] = len(trace)
    return payload


@app.post("/demo/auto-run")
def demo_auto_run(request: DemoAutoRunRequest = Body(default_factory=DemoAutoRunRequest)) -> dict[str, object]:
    env = _current_env()
    observation = env.last_observation
    max_steps = request.max_steps or observation.max_steps
    trace: list[dict[str, object]] = []
    steps_taken = 0

    while not observation.done and steps_taken < max_steps:
        wave_observation, wave_trace = _dispatch_wave(max_actions=max_steps - steps_taken)
        if not wave_trace:
            break
        steps_taken += len(wave_trace)
        trace.extend(wave_trace)
        observation = wave_observation

    payload = _serialize_demo()
    payload["observation"] = observation.model_dump(mode="json")
    payload["state"] = env.state.model_dump(mode="json")
    payload["steps_taken"] = steps_taken
    payload["trace"] = trace
    return payload


def main(host: str = "0.0.0.0", port: int = 8000) -> None:
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    main(host=args.host, port=args.port)
