from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from openenv.core.env_server.types import Action, Observation, State


class TriageLevel(str, Enum):
    CRITICAL_108 = "108"
    URGENT_102 = "102"


class ActionType(str, Enum):
    DISPATCH = "dispatch"


class AmbulanceMode(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"


class SupportLevel(str, Enum):
    ADVANCED = "advanced"
    BASIC = "basic"
    MATERNAL = "maternal"


class TaskDescriptor(BaseModel):
    task_id: str = Field(description="Stable identifier for the scenario.")
    title: str = Field(description="Human-friendly task title.")
    difficulty: str = Field(description="Difficulty label: easy, medium, or hard.")
    objective: str = Field(description="Concrete objective the dispatcher must optimize.")


class AmbulanceSnapshot(BaseModel):
    ambulance_id: str
    label: str
    node_id: str
    location_name: str
    support_level: SupportLevel
    mode: AmbulanceMode
    fuel_pct: float = Field(ge=0.0, le=100.0)
    available_from_minute: int = Field(ge=0)
    last_assignment: str | None = None


class IncidentSnapshot(BaseModel):
    incident_id: str
    label: str
    node_id: str
    location_name: str
    triage: TriageLevel
    status: str
    release_minute: int = Field(ge=0)
    wait_minutes: float = Field(ge=0.0)
    required_support: SupportLevel
    required_hospital_level: int = Field(ge=1, le=3)
    required_specialty: str
    decay_rate: float = Field(gt=0.0)
    description: str


class HospitalSnapshot(BaseModel):
    hospital_id: str
    label: str
    node_id: str
    location_name: str
    trauma_level: int = Field(ge=1, le=3)
    bed_capacity: int = Field(ge=0)
    current_load: int = Field(ge=0)
    specialties: list[str] = Field(default_factory=list)


class DispatchCandidate(BaseModel):
    candidate_id: str
    ambulance_id: str
    incident_id: str
    incident_triage: TriageLevel
    hospital_id: str
    use_green_corridor: bool = False
    route_node_ids: list[str] = Field(default_factory=list)
    scene_eta_minutes: float = Field(ge=0.0)
    transport_eta_minutes: float = Field(ge=0.0)
    effective_minutes: float = Field(ge=0.0)
    predicted_survival: float = Field(ge=0.0, le=1.0)
    weighted_survival: float = Field(ge=0.0)
    fuel_after_pct: float = Field(ge=0.0, le=100.0)
    route_summary: str
    why_it_is_valid: str


class MaskedActionReason(BaseModel):
    subject_id: str
    reason: str


class DecisionLogEntry(BaseModel):
    minute: int = Field(ge=0)
    action_label: str
    explanation: str
    reward_delta: float


class RewardBreakdown(BaseModel):
    survival_gain: float = 0.0
    backlog_pressure_penalty: float = 0.0
    invalid_action_penalty: float = 0.0
    corridor_cost: float = 0.0
    missed_incident_penalty: float = 0.0
    total_reward: float = 0.0


class IncidentOutcome(BaseModel):
    incident_id: str
    triage: TriageLevel
    ambulance_id: str | None = None
    hospital_id: str | None = None
    survival_probability: float = Field(default=0.0, ge=0.0, le=1.0)
    weighted_survival: float = Field(default=0.0, ge=0.0)
    resolved: bool = False
    missed: bool = False


class DispatchAction(Action):
    action_type: ActionType = Field(default=ActionType.DISPATCH)
    ambulance_id: str = Field(description="Ambulance to dispatch.")
    incident_id: str = Field(description="Incident to serve.")
    hospital_id: str = Field(description="Hospital destination.")
    use_green_corridor: bool = Field(
        default=False,
        description="Only valid for critical 108 incidents when corridor budget remains.",
    )
    rationale: str | None = Field(
        default=None,
        description="Optional explanation from the agent for why this assignment was chosen.",
    )


class DispatchObservation(Observation):
    task: TaskDescriptor
    current_time_minute: int = Field(ge=0)
    max_steps: int = Field(ge=1)
    steps_taken: int = Field(ge=0)
    step_budget_remaining: int = Field(ge=0)
    green_corridors_remaining: int = Field(ge=0)
    ambulances: list[AmbulanceSnapshot] = Field(default_factory=list)
    incidents: list[IncidentSnapshot] = Field(default_factory=list)
    hospitals: list[HospitalSnapshot] = Field(default_factory=list)
    available_dispatches: list[DispatchCandidate] = Field(default_factory=list)
    masked_actions: list[MaskedActionReason] = Field(default_factory=list)
    decision_log: list[DecisionLogEntry] = Field(default_factory=list)
    reward_breakdown: RewardBreakdown = Field(default_factory=RewardBreakdown)
    summary: str


class DispatchState(State):
    task: TaskDescriptor
    current_time_minute: int = Field(ge=0)
    max_steps: int = Field(ge=1)
    steps_taken: int = Field(ge=0)
    cumulative_reward: float = 0.0
    weighted_survival_gained: float = Field(default=0.0, ge=0.0)
    optimal_weighted_survival: float = Field(default=0.0, ge=0.0)
    invalid_actions: int = Field(default=0, ge=0)
    total_incidents: int = Field(default=0, ge=0)
    resolved_incident_ids: list[str] = Field(default_factory=list)
    missed_incident_ids: list[str] = Field(default_factory=list)
    incident_outcomes: list[IncidentOutcome] = Field(default_factory=list)
    ambulances: list[AmbulanceSnapshot] = Field(default_factory=list)
    incidents: list[IncidentSnapshot] = Field(default_factory=list)
    hospitals: list[HospitalSnapshot] = Field(default_factory=list)
    decision_log: list[DecisionLogEntry] = Field(default_factory=list)
    last_reward_breakdown: RewardBreakdown = Field(default_factory=RewardBreakdown)
    task_score: float | None = Field(default=None, gt=0.0, lt=1.0)
    score_breakdown: dict[str, float] = Field(default_factory=dict)
