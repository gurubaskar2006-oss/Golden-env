---
title: Golden Hour Dispatch Environment
emoji: 🚑
colorFrom: red
colorTo: yellow
sdk: docker
pinned: false
app_port: 8000
tags:
  - openenv
  - emergency-dispatch
  - healthcare
  - india
---

# Golden Hour Dispatch Environment

Golden Hour Dispatch is an original OpenEnv environment for emergency medical service dispatch in the Tamil Nadu `108/102` context. The agent acts as a control-room dispatcher who must allocate ambulances, pick hospitals, and optionally trigger a green corridor for critical cases while balancing traffic, fuel, hospital capacity, and patient deterioration.

This environment is designed for real-world utility instead of toy routing. It models a genuine human task: deciding which ambulance should handle which emergency call under incomplete operational slack and strict time pressure.

## Why this environment matters

- Real-world utility: dispatchers already make these decisions every day.
- Better reward design: reward is tied to survival preservation, not just average travel time.
- Real constraints: traffic, fuel reserve, hospital capability, and unavailable ambulances all matter.
- Tamil Nadu-specific framing: `108` covers acute emergencies, trauma, and cardiac events with ALS support, while `102` covers maternal and newborn transport through the public health system.

## Human Evaluation Alignment

- Problem relevance: the environment models emergency medical dispatch, a high-stakes public-service workflow with real prioritization pressure.
- Environment design quality: the task is not a static classifier or toy route planner; each step recomputes valid assignments from ambulance availability, support level, fuel reserve, traffic, hospital specialty, capacity, and green-corridor budget.
- Meaningful grader logic: final scores combine weighted survival versus an oracle optimum, incident coverage, critical `108` coverage, and action hygiene so agents are judged on operational outcomes rather than only on reaching a destination.
- Code quality: typed OpenEnv action, observation, and state models are separated from the simulator, task bank, grader functions, server wrapper, dashboard endpoints, and baseline runner.
- Innovation: the environment combines RL-style dense rewards with a domain-specific EMS control-room scenario, separating benchmark tasks from richer showcase shifts for human inspection.

## Environment summary

- Domain: emergency dispatch
- API: OpenEnv `reset()`, `step()`, and `state()`
- Runtime: FastAPI
- Deployment target: Hugging Face Docker Space tagged with `openenv`
- Demo UI: browser dashboard at `/` for live scenario playback, multi-ambulance auto-dispatch waves, and route animations

The environment uses a Chennai-inspired road graph and computes shortest-path travel times with traffic multipliers. Each decision step exposes valid dispatch candidates, masked actions with reasons, and a natural-language briefing for LLM agents.

The benchmark tasks stay compact and deterministic for evaluation, while the flagship showcase scenario now models a larger surge shift with five ambulances and six simultaneous cases so judges can see the system handle real dispatch pressure.

The demo dashboard supports:

- manual dispatch selection from the current candidate list
- `Auto Dispatch Wave`, which can assign multiple ambulances in the same minute
- `Auto Run Shift`, which resolves the whole scenario using the built-in priority-aware policy
- a curated scenario selector with grouped `Showcase Scenarios` and `Benchmark Tasks`
- difficulty labels directly in the scenario picker, for example `(easy)`, `(medium)`, and `(hard)`
- two showcase scenarios exposed in the picker: `Chennai Surge Shift` and `Chennai Dual-Critical Clearance`
- animated ambulance movement along the selected road path
- clickable ambulances with unit-focus details
- a fleet board with live ambulance location, fuel, support type, and last assignment
- a hospital watch panel that surfaces saturation and specialty capacity at a glance
- a live queue, service split, and mission-control style metrics for `108` and `102`
- a top-level event ticker and map-first Chennai command-center layout
- direct links to `OpenEnv Docs`, `Schema JSON`, and `Live State`
- floating reward feedback on the map after dispatch decisions

The built-in auto policy always clears active `108` incidents before `102` incidents when valid resources exist, so a heart attack is dispatched before a maternal or newborn transfer.

## Action space

The agent submits a typed `DispatchAction`:

- `action_type`: currently `dispatch`
- `ambulance_id`: ambulance to assign
- `incident_id`: incident to serve
- `hospital_id`: destination hospital
- `use_green_corridor`: whether to activate a traffic-clearing corridor for a `108` case
- `rationale`: optional free-text explanation

Invalid actions are penalized and leave the episode state unchanged.

## Observation space

Each `DispatchObservation` includes:

- task descriptor and mission objective
- current time and remaining step budget
- ambulance snapshots
- incident snapshots
- hospital snapshots
- valid dispatch candidates with predicted survival, required hospital specialty, and fuel impact
- masked action reasons
- decision log
- per-step `reward_breakdown` for transparent learning signals
- natural-language summary for agent prompting

## Sample API Interaction

Reset the current benchmark episode:

```bash
curl -X POST http://localhost:8000/reset \
  -H "Content-Type: application/json" \
  -d "{}"
```

The response contains a normalized OpenEnv observation with task metadata, current fleet state, active incidents, hospital capacity, and `available_dispatches`. A typical first task id is `easy_single_critical`.

Dispatch one valid candidate:

```bash
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{
    "action": {
      "ambulance_id": "AMB-ALS-CENTRAL",
      "incident_id": "INC-108-CARDIAC-TNAGAR",
      "hospital_id": "HOSP-APOLLO",
      "use_green_corridor": true,
      "rationale": "Fastest compatible ALS response for the active 108 cardiac case."
    }
  }'
```

Inspect the final state and deterministic score:

```bash
curl http://localhost:8000/state
```

Expected benchmark score range is strict `(0, 1)`, exposed as `0.001` to `0.999`.

## Reward design

The environment separates dense step reward from final grader score:

- `reward`: dense learning signal returned every step
- `grader score`: deterministic normalized task score used for final evaluation

The step reward is shaped around survival preservation and anti-stalling pressure:

`reward = survival_gain - backlog_pressure - invalid_action_penalty - corridor_cost - missed_incident_penalty`

Where:

- `survival_gain = priority_weight * exp(-decay_rate * effective_minutes)`
- `108` incidents have higher decay and higher weight than `102` maternal/newborn transfers
- `backlog_pressure` adds a small dense penalty for leaving active incidents unresolved, with extra weight on waiting `108` cases
- invalid actions receive escalating penalties, which discourages repeated spammy moves
- missed incidents add a stronger terminal penalty, especially for unresolved `108` emergencies
- `reward_breakdown` is exposed in observations and state for debugging and judge inspection

This makes the environment useful for both RL and agentic planning evaluation.

## Reward Safety

To reduce reward hacking, the environment includes:

- escalating invalid-action penalties for repeated bad actions
- backlog pressure so the agent cannot gain by dithering while patients wait
- stronger penalties for missed critical incidents
- a separate deterministic grader score so terminal evaluation is not tied only to step reward

## Tasks

The environment ships with four deterministic benchmark tasks plus curated showcase scenarios for the dashboard:

1. `easy_single_critical`
   Single `108` cardiac case in central Chennai with one clear ALS choice.

2. `medium_split_queue`
   Concurrent `108` heart attack and `102` maternity transport calls with one ambulance masked out by low fuel.

3. `hard_peak_hour_tradeoffs`
   Three active incidents during Chennai peak congestion with one green corridor budget and a saturated trauma center.

4. `city_shift_priority_mix`
   A Chennai control-room shift with simultaneous critical emergencies plus maternal/newborn `102` cases so multiple ambulances can operate in parallel.

Showcase-only dashboard scenarios:

- `demo_chennai_surge_shift`
  The flagship live demo: six simultaneous incidents with five ambulances, forcing the agent to prioritize multiple `108` emergencies before clearing maternal/newborn `102` cases.

- `demo_dual_critical_clearance`
  A polished live-demo shift where both `108` emergencies are realistically reachable while the `102` maternal case is still handled cleanly.

The default dashboard selector is intentionally refined to keep the story easy to follow:

- `Chennai Surge Shift (mixed)`
- `Chennai Dual-Critical Clearance (mixed)`
- `Single Cardiac 108 in Central Chennai (easy)`
- `Heart Attack Before Maternal 102 (medium)`
- `OMR Peak-Hour Tradeoffs with Corridor Budget (hard)`

The showcase scenarios improve the human demo, but they do not replace the deterministic benchmark tasks used by the grader or baseline script. The extra benchmark task `city_shift_priority_mix` remains available in the task bank and evaluation code even though it is hidden from the default picker to keep the UI focused.

## Grading

Each task is scored with a normalized final value inside `(0, 1)` using:

- weighted survival achieved versus an oracle optimum
- incident coverage
- action hygiene, including invalid-action penalties

The graders are deterministic because tasks, traffic, and seeds are fixed.

## Local setup

```bash
pip install -e .
uvicorn golden_hour_dispatch_env.server.app:app --host 0.0.0.0 --port 8000
openenv validate
pytest
```

## Docker

```bash
docker build -t golden-hour-dispatch-env .
docker run -p 8000:8000 golden-hour-dispatch-env
```

## Hugging Face Space

Deploy as a Docker Space and keep the `openenv` tag in the Space metadata. The server exposes the OpenEnv endpoints plus two helper endpoints:

- `GET /health`
- `GET /tasks`
- `GET /demo/config`
- `POST /demo/reset`
- `POST /demo/step`
- `POST /demo/auto-step`
- `POST /demo/auto-wave`
- `POST /demo/auto-run`

### Deploy to Hugging Face

1. Create a new Space on Hugging Face and choose `Docker` as the SDK.
2. Name the Space something like `golden-hour-dispatch-env`.
3. Upload the contents of this repo root to the Space root:
   `README.md`, `Dockerfile`, `openenv.yaml`, `pyproject.toml`, `uv.lock`, `inference.py`, `task_graders.py`, `golden_hour_dispatch_env/`, `server/`, `tests/`, and optionally `outputs/`.
4. Make sure the YAML block at the top of `README.md` stays intact because Hugging Face reads the Space configuration from there.
5. Wait for the image build to complete. This project listens on port `8000`, which already matches the `app_port` value in the README front matter.
6. After the Space turns green, test:
   - `/`
   - `/health`
   - `/tasks`
   - `/demo/reset`
   - the OpenEnv `reset()` endpoint used by the validator

If you want to run the baseline model call from the Space as well, add these in Space Settings:

- Variable: `API_BASE_URL`
- Variable: `MODEL_NAME`
- Secret: `HF_TOKEN`

## Baseline inference

The required baseline script is `inference.py`. It uses the OpenAI client and reads:

- `API_BASE_URL`
- `MODEL_NAME`
- `HF_TOKEN`
- `LOCAL_IMAGE_NAME` optionally, if you want the script to connect through `from_docker_image(...)` instead of the in-process fallback

Run:

```bash
python inference.py
```

By default, this runs one episode per benchmark task and emits a `[START] ... [END]` trace for each task, which makes the task sweep explicit for evaluation and baseline reproduction. If `HF_TOKEN` is absent, the script falls back to the deterministic heuristic policy so the automated baseline still completes without network credentials. The routed LLM path uses `HF_TOKEN` through the OpenAI client.

Optional heuristic smoke test:

```bash
python inference.py --policy heuristic --single-episode
```

To reproduce the benchmark table across all deterministic tasks, use:

```bash
python inference.py --policy heuristic
```

If you want a routed LLM baseline across every benchmark task, set `HF_TOKEN`, plus `API_BASE_URL` and `MODEL_NAME`, then use:

```bash
python inference.py
```

If you want to force only one episode, use:

```bash
python inference.py --single-episode
```

The script emits organizer-style stdout logs per episode:

- `[START] task=<task_name> env=<benchmark> model=<model_name>`
- `[STEP] step=<n> action=<json> reward=<0.00> done=<true|false> error=<msg|null>`
- `[END] success=<true|false> steps=<n> rewards=<r1,r2,...,rn>`

Verified benchmark baselines:

| Task | Heuristic score | LLM score (`Qwen/Qwen2.5-72B-Instruct`) |
| --- | --- | --- |
| `easy_single_critical` | `0.999` | `0.999` |
| `medium_split_queue` | `0.999` | `0.999` |
| `hard_peak_hour_tradeoffs` | `0.8743` | `0.8743` |
| `city_shift_priority_mix` | `0.8493` | `0.8493` |
| `mean` | `0.9304` | `0.9304` |

The heuristic values are stored in `outputs/baseline_scores_heuristic.json`. The routed LLM values are stored in both `outputs/baseline_scores_llm.json` and the primary `outputs/baseline_scores.json` after running `python inference.py --policy llm --all-tasks` with `HF_TOKEN`, `API_BASE_URL`, and `MODEL_NAME` set. Scores are deliberately kept strictly inside `(0, 1)` to avoid validator edge cases on exact endpoint values.

## Submission Lock Checklist

Before submission, treat the deterministic benchmark path as frozen and verify these items end to end:

1. `docker build .`
2. `openenv validate`
3. `python inference.py --policy heuristic --single-episode`
4. `python inference.py --policy heuristic`
5. `python inference.py` with `HF_TOKEN`, plus `API_BASE_URL` and `MODEL_NAME`
6. if you want a routed single-episode smoke test, run `python inference.py --single-episode`
7. update the README score table with real baseline values
8. make the Hugging Face Space public
9. run the provided validator script against the public Space URL
10. confirm `POST /reset` on the public `.hf.space` URL returns `200`

The showcase dashboard scenarios are only for product demonstration. The benchmark tasks and baseline script should remain deterministic for validator and grader reproducibility.

## Project structure

```text
golden_hour_dispatch_env/
  models.py
  task_bank.py
  simulator.py
  graders.py
  client.py
  server/
    app.py
    dispatch_environment.py
server/
  app.py
tests/
inference.py
task_graders.py
openenv.yaml
pyproject.toml
uv.lock
Dockerfile
README.md
```
