from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from openai import OpenAI

from golden_hour_dispatch_env.client import GoldenHourDispatchEnv
from golden_hour_dispatch_env.models import DispatchAction, DispatchObservation
from golden_hour_dispatch_env.server.dispatch_environment import GoldenHourDispatchEnvironment
from golden_hour_dispatch_env.task_bank import TASKS

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
API_KEY = os.getenv("API_KEY") or HF_TOKEN or os.getenv("OPENAI_API_KEY")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")
BENCHMARK = "golden_hour_dispatch_env"
SUCCESS_SCORE_THRESHOLD = float(os.getenv("SUCCESS_SCORE_THRESHOLD", "0.65"))
MAX_STEPS_OVERRIDE = os.getenv("MAX_STEPS")

SYSTEM_PROMPT = """You are an EMS control-room dispatcher.
Choose exactly one valid ambulance dispatch from the observation.
Optimize for survival gain while avoiding backlog, invalid actions, and unnecessary corridor usage.
Return only compact JSON with these keys:
{
  "ambulance_id": "string",
  "incident_id": "string",
  "hospital_id": "string",
  "use_green_corridor": true_or_false,
  "rationale": "short explanation"
}
Never invent ids and only use available_dispatches."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the EMS baseline for a single Golden Hour Dispatch episode or across all benchmark tasks."
    )
    parser.add_argument(
        "--policy",
        choices=("llm", "heuristic"),
        default="llm",
        help="Use the OpenAI client baseline or the built-in heuristic.",
    )
    parser.add_argument(
        "--all-tasks",
        action="store_true",
        help="Run one episode per benchmark task.",
    )
    parser.add_argument(
        "--single-episode",
        action="store_true",
        help="Override the default benchmark sweep and run just one episode.",
    )
    parser.add_argument(
        "--task-id",
        choices=tuple(TASKS.keys()),
        help="Run a specific benchmark task in-process. If omitted, the environment's default task selection is used.",
    )
    return parser.parse_args()


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: str | None) -> None:
    error_value = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_value}",
        flush=True,
    )


def log_end(success: bool, steps: int, rewards: list[float]) -> None:
    rewards_str = ",".join(f"{reward:.2f}" for reward in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}",
        flush=True,
    )


def main() -> None:
    args = parse_args()
    client = build_openai_client(args.policy)

    run_all_tasks = not args.single_episode
    if args.all_tasks:
        run_all_tasks = True

    if args.task_id:
        run_all_tasks = False

    if args.all_tasks and args.single_episode:
        raise RuntimeError("Use either --all-tasks or --single-episode, not both.")
    if args.all_tasks and args.task_id:
        raise RuntimeError("Use either --all-tasks or --task-id, not both.")
    if args.single_episode and args.task_id:
        raise RuntimeError("Use either --single-episode or --task-id, not both.")

    if LOCAL_IMAGE_NAME:
        reports = run_via_docker_client(
            client=client,
            policy=args.policy,
            run_all_tasks=run_all_tasks,
        )
    else:
        reports = run_in_process(
            client=client,
            policy=args.policy,
            run_all_tasks=run_all_tasks,
            task_id=args.task_id,
        )

    mean_score = round(sum(report["score"] for report in reports) / len(reports), 4) if reports else 0.0
    output = {
        "benchmark": BENCHMARK,
        "policy": args.policy,
        "model_name": MODEL_NAME if args.policy == "llm" else "heuristic",
        "mode": "all_tasks" if run_all_tasks else "single_episode",
        "mean_score": mean_score,
        "tasks": reports,
    }
    Path("outputs").mkdir(exist_ok=True)
    Path("outputs/baseline_scores.json").write_text(json.dumps(output, indent=2), encoding="utf-8")


def build_openai_client(policy: str) -> OpenAI | None:
    if policy != "llm":
        return None
    if not API_KEY:
        raise RuntimeError("API_KEY (or HF_TOKEN/OPENAI_API_KEY fallback) must be set for the LLM baseline.")
    return OpenAI(base_url=API_BASE_URL, api_key=API_KEY)


def run_in_process(
    client: OpenAI | None,
    policy: str,
    run_all_tasks: bool,
    task_id: str | None,
) -> list[dict[str, Any]]:
    if run_all_tasks:
        reports: list[dict[str, Any]] = []
        for benchmark_task_id in TASKS:
            env = GoldenHourDispatchEnvironment(task_id=benchmark_task_id)
            reports.append(
                run_episode(env=env, task_label=benchmark_task_id, client=client, policy=policy)
            )
        return reports

    env = GoldenHourDispatchEnvironment(task_id=task_id)
    return [run_episode(env=env, task_label=task_id, client=client, policy=policy)]


def run_via_docker_client(
    client: OpenAI | None,
    policy: str,
    run_all_tasks: bool,
) -> list[dict[str, Any]]:
    env = GoldenHourDispatchEnv.from_docker_image(LOCAL_IMAGE_NAME)
    reports: list[dict[str, Any]] = []
    try:
        run_count = len(TASKS) if run_all_tasks else 1
        for _ in range(run_count):
            reports.append(run_episode(env=env, task_label=None, client=client, policy=policy))
    finally:
        env.close()
    return reports


def run_episode(
    env: Any,
    task_label: str | None,
    client: OpenAI | None,
    policy: str,
) -> dict[str, Any]:
    rewards: list[float] = []
    steps_taken = 0
    success = False
    task_id = task_label or "unknown"
    observation = None
    final_state = None

    try:
        observation = env.reset()
        if hasattr(observation, "observation"):
            observation = observation.observation
        task_id = observation.task.task_id
        max_steps = int(MAX_STEPS_OVERRIDE or observation.max_steps)
        model_label = MODEL_NAME if policy == "llm" else "heuristic"
        log_start(task=task_id, env=BENCHMARK, model=model_label)

        while not observation.done and steps_taken < max_steps:
            action, action_repr, action_error = choose_action(
                client=client,
                policy=policy,
                observation=observation,
            )
            step_result = env.step(action)
            if hasattr(step_result, "observation"):
                observation = step_result.observation
                reward = float(step_result.reward or 0.0)
                done = bool(step_result.done)
            else:
                observation = step_result
                reward = float(observation.reward or 0.0)
                done = bool(observation.done)

            steps_taken += 1
            rewards.append(reward)
            log_step(
                step=steps_taken,
                action=action_repr,
                reward=reward,
                done=done,
                error=action_error,
            )
            if done:
                break

        final_state = env.state if not callable(getattr(env, "state", None)) else env.state()
        score = float(final_state.task_score or 0.0)
        success = score >= SUCCESS_SCORE_THRESHOLD
        report = {
            "task_id": task_id,
            "score": round(score, 4),
        }
        return report
    finally:
        if final_state is None and observation is not None:
            try:
                final_state = env.state if not callable(getattr(env, "state", None)) else env.state()
                success = float(final_state.task_score or 0.0) >= SUCCESS_SCORE_THRESHOLD
            except Exception:
                success = False
        log_end(success=success, steps=steps_taken, rewards=rewards)


def choose_action(
    client: OpenAI | None,
    policy: str,
    observation: DispatchObservation,
) -> tuple[DispatchAction, str, str | None]:
    if policy == "heuristic":
        action = heuristic_action(observation)
        return action, action_to_log_string(action), None

    try:
        action = choose_with_llm(client=client, observation=observation)
        return action, action_to_log_string(action), None
    except Exception as exc:
        action = heuristic_action(observation)
        return action, action_to_log_string(action), str(exc)


def choose_with_llm(client: OpenAI, observation: DispatchObservation) -> DispatchAction:
    if client is None:
        raise RuntimeError("LLM policy requested without an initialized OpenAI client.")

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        max_tokens=220,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(observation.model_dump(mode="json"), separators=(",", ":")),
            },
        ],
    )
    content = response.choices[0].message.content or ""
    data = extract_json_object(content)
    return DispatchAction(**data)


def heuristic_action(observation: DispatchObservation) -> DispatchAction:
    if not observation.available_dispatches:
        raise RuntimeError("No valid dispatches are available and the episode should already be done.")
    best = max(
        observation.available_dispatches,
        key=lambda candidate: (
            candidate.weighted_survival,
            candidate.predicted_survival,
        ),
    )
    return DispatchAction(
        ambulance_id=best.ambulance_id,
        incident_id=best.incident_id,
        hospital_id=best.hospital_id,
        use_green_corridor=best.use_green_corridor,
        rationale="Selected the highest weighted-survival valid candidate.",
    )


def action_to_log_string(action: DispatchAction) -> str:
    payload = action.model_dump(exclude_none=True)
    return json.dumps(payload, separators=(",", ":"))


def extract_json_object(content: str) -> dict[str, Any]:
    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model response.")
    return json.loads(content[start : end + 1])


if __name__ == "__main__":
    main()
