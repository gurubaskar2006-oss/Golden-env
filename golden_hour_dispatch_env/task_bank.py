from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class RoadEdge:
    start: str
    end: str
    base_minutes: float
    congestion_multiplier: float = 1.0


@dataclass(frozen=True)
class AmbulanceConfig:
    ambulance_id: str
    label: str
    node_id: str
    support_level: str
    fuel_pct: float
    available_from_minute: int = 0


@dataclass(frozen=True)
class HospitalConfig:
    hospital_id: str
    label: str
    node_id: str
    trauma_level: int
    bed_capacity: int
    current_load: int
    specialties: tuple[str, ...]


@dataclass(frozen=True)
class IncidentConfig:
    incident_id: str
    label: str
    node_id: str
    triage: str
    release_minute: int
    decay_rate: float
    required_support: str
    required_hospital_level: int
    description: str
    priority_weight: float


@dataclass(frozen=True)
class TaskConfig:
    task_id: str
    title: str
    difficulty: str
    objective: str
    start_minute: int
    max_steps: int
    traffic_phase: str
    green_corridor_budget: int
    node_labels: dict[str, str]
    edges: tuple[RoadEdge, ...]
    ambulances: tuple[AmbulanceConfig, ...]
    hospitals: tuple[HospitalConfig, ...]
    incidents: tuple[IncidentConfig, ...]
    reference_optimal_weighted_survival: float | None = None


def _shared_edges() -> tuple[RoadEdge, ...]:
    undirected_edges = [
        ("anna_nagar", "koyambedu", 8, 1.08),
        ("anna_nagar", "kilpauk", 9, 1.10),
        ("koyambedu", "porur", 14, 1.20),
        ("koyambedu", "egmore", 15, 1.18),
        ("kilpauk", "egmore", 8, 1.12),
        ("egmore", "greams_road", 6, 1.07),
        ("egmore", "marina", 10, 1.12),
        ("greams_road", "t_nagar", 8, 1.10),
        ("greams_road", "marina", 10, 1.16),
        ("t_nagar", "guindy", 12, 1.22),
        ("porur", "guindy", 15, 1.26),
        ("guindy", "velachery", 10, 1.16),
        ("velachery", "omr", 11, 1.30),
        ("guindy", "tambaram", 18, 1.34),
        ("omr", "tambaram", 22, 1.38),
        ("marina", "guindy", 18, 1.24),
    ]
    edges: list[RoadEdge] = []
    for start, end, base_minutes, congestion in undirected_edges:
        edges.append(RoadEdge(start, end, base_minutes, congestion))
        edges.append(RoadEdge(end, start, base_minutes, congestion))
    return tuple(edges)


def _node_labels() -> dict[str, str]:
    return {
        "anna_nagar": "Anna Nagar Roundtana",
        "koyambedu": "Koyambedu Junction",
        "kilpauk": "Kilpauk Medical Belt",
        "egmore": "Egmore Government Corridor",
        "greams_road": "Greams Road",
        "marina": "Marina Loop",
        "t_nagar": "T Nagar",
        "guindy": "Guindy Kathipara",
        "velachery": "Velachery 100 Ft Road",
        "omr": "OMR Sholinganallur",
        "tambaram": "Tambaram GST Road",
        "porur": "Porur Junction",
    }


NODE_LAYOUT: dict[str, dict[str, int]] = {
    "anna_nagar": {"x": 146, "y": 94},
    "koyambedu": {"x": 236, "y": 176},
    "kilpauk": {"x": 334, "y": 122},
    "egmore": {"x": 430, "y": 184},
    "greams_road": {"x": 534, "y": 174},
    "marina": {"x": 646, "y": 234},
    "t_nagar": {"x": 526, "y": 276},
    "porur": {"x": 168, "y": 306},
    "guindy": {"x": 646, "y": 358},
    "velachery": {"x": 734, "y": 356},
    "omr": {"x": 814, "y": 390},
    "tambaram": {"x": 724, "y": 492},
}


TASKS: dict[str, TaskConfig] = {
    "easy_single_critical": TaskConfig(
        task_id="easy_single_critical",
        title="Single Cardiac 108 in Central Chennai",
        difficulty="easy",
        objective=(
            "Dispatch the most suitable ALS ambulance for a single 108 heart attack case and "
            "route the patient to the best trauma-capable Chennai hospital."
        ),
        start_minute=0,
        max_steps=3,
        traffic_phase="moderate_morning",
        green_corridor_budget=1,
        node_labels=_node_labels(),
        edges=_shared_edges(),
        ambulances=(
            AmbulanceConfig("AMB-ALS-NORTH", "ALS Anna Nagar", "anna_nagar", "advanced", 86),
            AmbulanceConfig("AMB-ALS-CENTRAL", "ALS Central Reserve", "greams_road", "advanced", 81),
            AmbulanceConfig("AMB-MAT-EGM", "102 Maternal Egmore", "egmore", "maternal", 78),
        ),
        hospitals=(
            HospitalConfig("HOSP-RGGH", "Rajiv Gandhi GH", "egmore", 1, 16, 7, ("cardiac", "trauma")),
            HospitalConfig("HOSP-APOLLO", "Apollo Greams", "greams_road", 1, 14, 6, ("cardiac", "trauma")),
        ),
        incidents=(
            IncidentConfig(
                "INC-108-CARDIAC-TNAGAR",
                "Heart attack near T Nagar",
                "t_nagar",
                "108",
                0,
                0.15,
                "advanced",
                1,
                "A severe cardiac emergency has been reported near a busy shopping corridor.",
                5.0,
            ),
        ),
    ),
    "medium_split_queue": TaskConfig(
        task_id="medium_split_queue",
        title="Heart Attack Before Maternal 102",
        difficulty="medium",
        objective=(
            "Handle simultaneous heart attack and maternal 102 calls with multiple ambulances. "
            "The policy should prioritize the 108 cardiac emergency first while still clearing "
            "the maternal transport case efficiently."
        ),
        start_minute=0,
        max_steps=5,
        traffic_phase="peak_commute",
        green_corridor_budget=1,
        node_labels=_node_labels(),
        edges=_shared_edges(),
        ambulances=(
            AmbulanceConfig("AMB-ALS-GUINDY", "ALS Guindy", "guindy", "advanced", 74),
            AmbulanceConfig("AMB-102-ANNA", "102 Maternal Anna Nagar", "anna_nagar", "maternal", 70),
            AmbulanceConfig("AMB-ALS-OMR", "ALS OMR Reserve", "omr", "advanced", 18),
        ),
        hospitals=(
            HospitalConfig("HOSP-RGGH", "Rajiv Gandhi GH", "egmore", 1, 16, 9, ("cardiac", "trauma")),
            HospitalConfig("HOSP-APOLLO", "Apollo Greams", "greams_road", 1, 14, 7, ("cardiac", "trauma")),
            HospitalConfig("HOSP-IOG", "Institute of Obstetrics", "egmore", 2, 18, 11, ("maternity",)),
        ),
        incidents=(
            IncidentConfig(
                "INC-108-CARDIAC-KOY",
                "Heart attack at Koyambedu",
                "koyambedu",
                "108",
                0,
                0.16,
                "advanced",
                1,
                "A bus passenger has collapsed with chest pain and cardiac arrest signs.",
                5.0,
            ),
            IncidentConfig(
                "INC-102-MATERNITY-PORUR",
                "High-risk pregnancy transfer at Porur",
                "porur",
                "102",
                0,
                0.04,
                "maternal",
                2,
                "A woman in active labour with complications needs monitored transport to a maternity center.",
                2.8,
            ),
        ),
    ),
    "hard_peak_hour_tradeoffs": TaskConfig(
        task_id="hard_peak_hour_tradeoffs",
        title="OMR Peak-Hour Tradeoffs with Corridor Budget",
        difficulty="hard",
        objective=(
            "Maximize total life-probability across three active incidents during Chennai peak traffic. "
            "Use the single green corridor wisely and avoid the saturated public trauma center."
        ),
        start_minute=0,
        max_steps=6,
        traffic_phase="gridlock_peak",
        green_corridor_budget=1,
        node_labels=_node_labels(),
        edges=_shared_edges(),
        ambulances=(
            AmbulanceConfig("AMB-ALS-CENTRAL", "ALS Central", "t_nagar", "advanced", 80),
            AmbulanceConfig("AMB-ALS-SOUTH", "ALS South", "velachery", "advanced", 64),
            AmbulanceConfig("AMB-MAT-EGM", "Maternal Egmore", "egmore", "maternal", 75),
        ),
        hospitals=(
            HospitalConfig("HOSP-RGGH", "Rajiv Gandhi GH", "egmore", 1, 10, 10, ("cardiac", "trauma")),
            HospitalConfig("HOSP-APOLLO", "Apollo Greams", "greams_road", 1, 16, 10, ("cardiac", "trauma")),
            HospitalConfig("HOSP-IOG", "Institute of Obstetrics", "egmore", 2, 18, 12, ("maternity",)),
        ),
        incidents=(
            IncidentConfig(
                "INC-108-TRAUMA-TBM",
                "Severe trauma on GST Road",
                "tambaram",
                "108",
                0,
                0.17,
                "advanced",
                1,
                "A highway collision has left one patient with heavy bleeding and probable head injury.",
                5.2,
            ),
            IncidentConfig(
                "INC-108-CARDIAC-OMR",
                "Cardiac arrest on OMR",
                "omr",
                "108",
                0,
                0.15,
                "advanced",
                1,
                "A corporate shuttle passenger has collapsed and CPR is in progress.",
                5.0,
            ),
            IncidentConfig(
                "INC-102-MATERNITY-MARINA",
                "Urgent maternity transfer near Marina",
                "marina",
                "102",
                0,
                0.05,
                "maternal",
                2,
                "A high-risk pregnancy patient requires monitored transfer to a maternity center.",
                2.8,
            ),
        ),
    ),
    "city_shift_priority_mix": TaskConfig(
        task_id="city_shift_priority_mix",
        title="Chennai City Shift Priority Mix",
        difficulty="hard",
        objective=(
            "Run a full Chennai control-room shift with simultaneous critical, medium, and lower-priority incidents. "
            "Use multiple ambulances in parallel, clear 108 cases first, and keep overall survival high."
        ),
        start_minute=0,
        max_steps=8,
        traffic_phase="gridlock_peak",
        green_corridor_budget=2,
        node_labels=_node_labels(),
        edges=_shared_edges(),
        ambulances=(
            AmbulanceConfig("AMB-ALS-NORTH", "ALS North", "anna_nagar", "advanced", 84),
            AmbulanceConfig("AMB-ALS-SOUTH", "ALS South", "velachery", "advanced", 71),
            AmbulanceConfig("AMB-MAT-CENTRAL", "Maternal Central", "egmore", "maternal", 73),
        ),
        hospitals=(
            HospitalConfig("HOSP-RGGH", "Rajiv Gandhi GH", "egmore", 1, 18, 12, ("cardiac", "trauma")),
            HospitalConfig("HOSP-APOLLO", "Apollo Greams", "greams_road", 1, 15, 9, ("cardiac", "trauma")),
            HospitalConfig("HOSP-KMC", "Kilpauk Medical", "kilpauk", 2, 20, 11, ("trauma",)),
            HospitalConfig("HOSP-IOG", "Institute of Obstetrics", "egmore", 2, 18, 10, ("maternity",)),
        ),
        incidents=(
            IncidentConfig(
                "INC-108-CARDIAC-GUINDY",
                "Cardiac arrest at Guindy",
                "guindy",
                "108",
                0,
                0.16,
                "advanced",
                1,
                "A severe heart attack has been reported near the Kathipara interchange.",
                5.5,
            ),
            IncidentConfig(
                "INC-108-TRAUMA-OMR",
                "Major trauma on OMR",
                "omr",
                "108",
                0,
                0.17,
                "advanced",
                1,
                "A multi-vehicle crash has left one patient with life-threatening bleeding.",
                5.4,
            ),
            IncidentConfig(
                "INC-102-MATERNITY-ANNA",
                "Urgent maternity case in Anna Nagar",
                "anna_nagar",
                "102",
                0,
                0.05,
                "maternal",
                2,
                "A late-stage labour patient needs a monitored transfer without delay.",
                3.0,
            ),
            IncidentConfig(
                "INC-102-NEWBORN-TBM",
                "Newborn referral from Tambaram",
                "tambaram",
                "102",
                0,
                0.04,
                "maternal",
                2,
                "A newborn requires monitored referral transport with mother to a higher-level government facility.",
                2.6,
            ),
        ),
    ),
}


DEMO_TASKS: dict[str, TaskConfig] = {
    "demo_chennai_surge_shift": TaskConfig(
        task_id="demo_chennai_surge_shift",
        title="Chennai Surge Shift",
        difficulty="mixed",
        objective=(
            "Run a high-pressure Chennai control-room shift with six simultaneous cases and five ambulances. "
            "Prioritize the highest-risk 108 emergencies first, preserve maternal/newborn coverage, and keep "
            "overall survival high under constrained fleet capacity."
        ),
        start_minute=0,
        max_steps=10,
        traffic_phase="peak_commute",
        green_corridor_budget=2,
        node_labels=_node_labels(),
        edges=_shared_edges(),
        ambulances=(
            AmbulanceConfig("AMB-ALS-NORTH", "ALS North Command", "anna_nagar", "advanced", 89),
            AmbulanceConfig("AMB-ALS-CENTRAL", "ALS Central Reserve", "t_nagar", "advanced", 86),
            AmbulanceConfig("AMB-ALS-SOUTH", "ALS South Corridor", "velachery", "advanced", 84),
            AmbulanceConfig("AMB-102-EGM", "102 Maternal Egmore", "egmore", "maternal", 82),
            AmbulanceConfig("AMB-102-WEST", "102 Maternal West", "koyambedu", "maternal", 79),
        ),
        hospitals=(
            HospitalConfig("HOSP-RGGH", "Rajiv Gandhi GH", "egmore", 1, 18, 10, ("cardiac", "trauma")),
            HospitalConfig("HOSP-APOLLO", "Apollo Greams", "greams_road", 1, 16, 8, ("cardiac", "trauma")),
            HospitalConfig("HOSP-KMC", "Kilpauk Medical", "kilpauk", 2, 20, 9, ("trauma",)),
            HospitalConfig("HOSP-IOG", "Institute of Obstetrics", "egmore", 2, 20, 11, ("maternity",)),
            HospitalConfig("HOSP-KASTURBA", "Kasturba GH", "marina", 2, 18, 9, ("maternity", "newborn")),
        ),
        incidents=(
            IncidentConfig(
                "INC-108-CARDIAC-KOY-SURGE",
                "Cardiac arrest at Koyambedu",
                "koyambedu",
                "108",
                0,
                0.16,
                "advanced",
                1,
                "A middle-aged commuter has collapsed at the bus terminus with cardiac arrest signs.",
                5.5,
            ),
            IncidentConfig(
                "INC-108-TRAUMA-OMR-SURGE",
                "Polytrauma on OMR",
                "omr",
                "108",
                0,
                0.17,
                "advanced",
                1,
                "A high-speed collision on the OMR corridor has left one patient with severe bleeding and probable chest trauma.",
                5.4,
            ),
            IncidentConfig(
                "INC-108-STROKE-TBM-SURGE",
                "Stroke alert at Tambaram",
                "tambaram",
                "108",
                0,
                0.14,
                "advanced",
                1,
                "A possible stroke patient in Tambaram is losing speech and motor control during a narrow treatment window.",
                4.8,
            ),
            IncidentConfig(
                "INC-102-MATERNITY-ANNA-SURGE",
                "High-risk labour in Anna Nagar",
                "anna_nagar",
                "102",
                0,
                0.05,
                "maternal",
                2,
                "A late-stage labour patient with elevated blood pressure needs monitored transfer to a maternity center.",
                3.1,
            ),
            IncidentConfig(
                "INC-102-NEWBORN-VEL-SURGE",
                "Newborn referral from Velachery",
                "velachery",
                "102",
                0,
                0.04,
                "maternal",
                2,
                "A newborn and mother need monitored referral transfer from south Chennai to a higher-level neonatal facility.",
                2.9,
            ),
            IncidentConfig(
                "INC-102-PREGNANCY-PORUR-SURGE",
                "Pregnancy complication at Porur",
                "porur",
                "102",
                0,
                0.04,
                "maternal",
                2,
                "An antenatal patient at Porur has complications and requires monitored maternal transport.",
                2.7,
            ),
        ),
        reference_optimal_weighted_survival=24.4,
    ),
    "demo_dual_critical_clearance": TaskConfig(
        task_id="demo_dual_critical_clearance",
        title="Chennai Dual-Critical Clearance",
        difficulty="mixed",
        objective=(
            "Show a strong control-room response where both 108 emergencies are reachable in time while a "
            "102 maternal transfer is still coordinated cleanly. This is a showcase scenario for the live demo, "
            "not part of the benchmark grader set."
        ),
        start_minute=0,
        max_steps=6,
        traffic_phase="peak_commute",
        green_corridor_budget=2,
        node_labels=_node_labels(),
        edges=_shared_edges(),
        ambulances=(
            AmbulanceConfig("AMB-ALS-CENTRAL", "ALS Central Reserve", "t_nagar", "advanced", 88),
            AmbulanceConfig("AMB-ALS-SOUTH", "ALS South Corridor", "velachery", "advanced", 86),
            AmbulanceConfig("AMB-MAT-EGM", "102 Maternal Egmore", "egmore", "maternal", 82),
        ),
        hospitals=(
            HospitalConfig("HOSP-RGGH", "Rajiv Gandhi GH", "egmore", 1, 18, 10, ("cardiac", "trauma")),
            HospitalConfig("HOSP-APOLLO", "Apollo Greams", "greams_road", 1, 15, 8, ("cardiac", "trauma")),
            HospitalConfig("HOSP-KMC", "Kilpauk Medical", "kilpauk", 2, 18, 8, ("trauma",)),
            HospitalConfig("HOSP-IOG", "Institute of Obstetrics", "egmore", 2, 20, 11, ("maternity",)),
        ),
        incidents=(
            IncidentConfig(
                "INC-108-CARDIAC-GUINDY-DEMO",
                "Cardiac arrest at Guindy flyover",
                "guindy",
                "108",
                0,
                0.16,
                "advanced",
                1,
                "A commuter has collapsed near the Kathipara flyover and bystanders have started CPR.",
                5.5,
            ),
            IncidentConfig(
                "INC-108-TRAUMA-OMR-DEMO",
                "Severe trauma on OMR link road",
                "omr",
                "108",
                0,
                0.17,
                "advanced",
                1,
                "A crash victim on the OMR corridor has life-threatening bleeding and needs a rapid ALS pickup.",
                5.4,
            ),
            IncidentConfig(
                "INC-102-MATERNITY-ANNA-DEMO",
                "Monitored labour transfer at Anna Nagar",
                "anna_nagar",
                "102",
                0,
                0.05,
                "maternal",
                2,
                "A late-stage labour patient needs monitored transfer to a government maternity centre.",
                3.0,
            ),
        ),
    ),
    "demo_monsoon_redeployment": TaskConfig(
        task_id="demo_monsoon_redeployment",
        title="Monsoon Redeployment Across Chennai",
        difficulty="mixed",
        objective=(
            "Handle a rainy-shift redeployment across west, south, and maternity corridors with two 108 units and "
            "one 102 unit. The goal is to show realistic service balancing under weather-driven congestion."
        ),
        start_minute=18,
        max_steps=7,
        traffic_phase="peak_commute",
        green_corridor_budget=1,
        node_labels=_node_labels(),
        edges=_shared_edges(),
        ambulances=(
            AmbulanceConfig("AMB-ALS-WEST", "ALS West Cover", "koyambedu", "advanced", 84),
            AmbulanceConfig("AMB-ALS-SOUTH", "ALS South Cover", "guindy", "advanced", 79),
            AmbulanceConfig("AMB-MAT-EGM", "102 Maternal Egmore", "egmore", "maternal", 80),
        ),
        hospitals=(
            HospitalConfig("HOSP-RGGH", "Rajiv Gandhi GH", "egmore", 1, 18, 11, ("cardiac", "trauma")),
            HospitalConfig("HOSP-APOLLO", "Apollo Greams", "greams_road", 1, 15, 9, ("cardiac", "trauma")),
            HospitalConfig("HOSP-KMC", "Kilpauk Medical", "kilpauk", 2, 20, 10, ("trauma",)),
            HospitalConfig("HOSP-IOG", "Institute of Obstetrics", "egmore", 2, 19, 10, ("maternity",)),
        ),
        incidents=(
            IncidentConfig(
                "INC-108-STROKE-PORUR-DEMO",
                "Stroke alert near Porur Junction",
                "porur",
                "108",
                18,
                0.15,
                "advanced",
                1,
                "A possible stroke has been reported near Porur in heavy rain, with a narrow intervention window.",
                5.1,
            ),
            IncidentConfig(
                "INC-108-TRAUMA-TBM-DEMO",
                "Road trauma on GST near Tambaram",
                "tambaram",
                "108",
                18,
                0.17,
                "advanced",
                1,
                "A monsoon crash on the GST corridor has left one rider unconscious and bleeding heavily.",
                5.4,
            ),
            IncidentConfig(
                "INC-102-NEWBORN-VEL-DEMO",
                "Newborn transfer from Velachery",
                "velachery",
                "102",
                18,
                0.04,
                "maternal",
                2,
                "A newborn and mother need monitored referral transfer from south Chennai to a higher-level facility.",
                2.8,
            ),
        ),
    ),
}


def get_task_config(task_id: str) -> TaskConfig:
    if task_id in TASKS:
        return TASKS[task_id]
    if task_id in DEMO_TASKS:
        return DEMO_TASKS[task_id]
    raise KeyError(task_id)


DEFAULT_DEMO_TASK_ID = "demo_chennai_surge_shift"


def _task_card(task: TaskConfig, group: str | None = None) -> dict[str, str]:
    return {
        "task_id": task.task_id,
        "title": task.title,
        "difficulty": task.difficulty,
        "objective": task.objective,
        **({"group": group} if group else {}),
    }


def list_task_cards() -> list[dict[str, str]]:
    return [_task_card(task) for task in TASKS.values()]


DEMO_TASK_OPTIONS: dict[str, dict[str, object]] = {
    "chennai_live_ops": {
        "task_id": "chennai_live_ops",
        "title": "Chennai Live Ops",
        "difficulty": "mixed",
        "objective": (
            "Rotate through live Chennai control-room case mixes on every reset, including showcase scenarios that "
            "feel closer to a real operations shift while keeping the benchmark path untouched."
        ),
        "pool": (
            ("medium_split_queue", 1.0),
            ("hard_peak_hour_tradeoffs", 1.25),
            ("city_shift_priority_mix", 1.45),
            ("demo_dual_critical_clearance", 1.6),
            ("demo_monsoon_redeployment", 1.35),
        ),
    }
}


def list_demo_task_cards() -> list[dict[str, str]]:
    curated_ids = (
        "demo_chennai_surge_shift",
        "demo_dual_critical_clearance",
    )
    benchmark_ids = (
        "easy_single_critical",
        "medium_split_queue",
        "hard_peak_hour_tradeoffs",
    )

    cards: list[dict[str, str]] = []
    cards.extend(_task_card(DEMO_TASKS[task_id], "Showcase Scenarios") for task_id in curated_ids)
    cards.extend(_task_card(TASKS[task_id], "Benchmark Tasks") for task_id in benchmark_ids)
    return cards


def resolve_demo_task(task_id: str | None) -> tuple[str, dict[str, object]]:
    if not task_id:
        task_id = DEFAULT_DEMO_TASK_ID

    if task_id in TASKS:
        task = TASKS[task_id]
        return task_id, {
            "requested_task_id": task_id,
            "requested_title": task.title,
            "resolved_task_id": task_id,
            "resolved_title": task.title,
            "mode": "benchmark",
            "bonus_multiplier": difficulty_bonus(task.difficulty),
        }

    if task_id in DEMO_TASKS:
        task = DEMO_TASKS[task_id]
        return task_id, {
            "requested_task_id": task_id,
            "requested_title": task.title,
            "resolved_task_id": task_id,
            "resolved_title": task.title,
            "mode": "showcase",
            "bonus_multiplier": difficulty_bonus(task.difficulty),
        }

    if task_id not in DEMO_TASK_OPTIONS:
        raise KeyError(task_id)

    option = DEMO_TASK_OPTIONS[task_id]
    pool = option["pool"]
    task_ids = [item[0] for item in pool]
    weights = [item[1] for item in pool]
    resolved_task_id = random.choices(task_ids, weights=weights, k=1)[0]
    resolved_task = get_task_config(resolved_task_id)
    return resolved_task_id, {
        "requested_task_id": task_id,
        "requested_title": option["title"],
        "resolved_task_id": resolved_task_id,
        "resolved_title": resolved_task.title,
        "mode": "live_ops",
        "bonus_multiplier": difficulty_bonus(resolved_task.difficulty),
    }


def difficulty_bonus(difficulty: str) -> float:
    return {
        "easy": 1.0,
        "medium": 1.08,
        "hard": 1.18,
        "mixed": 1.18,
    }.get(difficulty, 1.0)


def ui_graph() -> dict[str, object]:
    labels = _node_labels()
    unique_edges: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for edge in _shared_edges():
        pair = tuple(sorted((edge.start, edge.end)))
        if pair in seen:
            continue
        seen.add(pair)
        unique_edges.append(
            {
                "source": edge.start,
                "target": edge.end,
                "minutes": edge.base_minutes,
                "congestion_multiplier": edge.congestion_multiplier,
            }
        )

    return {
        "nodes": [
            {
                "node_id": node_id,
                "label": labels[node_id],
                "x": coords["x"],
                "y": coords["y"],
            }
            for node_id, coords in NODE_LAYOUT.items()
        ],
        "edges": unique_edges,
    }
