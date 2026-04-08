from __future__ import annotations

import copy
import heapq
import math
from dataclasses import dataclass, field
from functools import lru_cache

from .models import (
    AmbulanceMode,
    AmbulanceSnapshot,
    DecisionLogEntry,
    DispatchAction,
    DispatchCandidate,
    DispatchObservation,
    DispatchState,
    HospitalSnapshot,
    IncidentOutcome,
    IncidentSnapshot,
    MaskedActionReason,
    RewardBreakdown,
    SupportLevel,
    TaskDescriptor,
    TriageLevel,
)
from .task_bank import AmbulanceConfig, HospitalConfig, IncidentConfig, RoadEdge, TaskConfig, get_task_config

FUEL_RESERVE_PCT = 15.0
FUEL_BURN_PER_MINUTE = 0.55
CORRIDOR_DISCOUNT = 0.75
CORRIDOR_COST = 0.08
INVALID_ACTION_BASE_PENALTY = 0.35
INVALID_ACTION_ESCALATION = 0.12
ACTIVE_INCIDENT_HOLDING_PENALTY = 0.03
WAIT_PENALTY_PER_MINUTE = 0.012
CRITICAL_WAIT_MULTIPLIER = 1.6
MISSED_INCIDENT_PENALTY = {
    "108": 1.5,
    "102": 0.6,
}
SERVICE_BUFFER_BY_TRIAGE = {
    "108": 8,
    "102": 11,
}
TRAFFIC_PHASE_FACTORS = {
    "moderate_morning": 1.00,
    "peak_commute": 1.18,
    "gridlock_peak": 1.34,
}
SCORE_EPSILON = 1e-4


def _clamp_score_metric(value: float) -> float:
    return max(SCORE_EPSILON, min(1.0 - SCORE_EPSILON, value))


def _normalize_exposed_reward(value: float) -> float:
    if value >= 0:
        normalized = 1.0 / (1.0 + math.exp(-min(value, 60.0)))
    else:
        exp_value = math.exp(max(value, -60.0))
        normalized = exp_value / (1.0 + exp_value)
    return round(_clamp_score_metric(normalized), 4)


def _normalize_nonnegative_exposed_metric(value: float) -> float:
    normalized = value / (1.0 + value) if value > 0 else 0.0
    return round(_clamp_score_metric(normalized), 4)


def _normalize_reward_breakdown(reward_breakdown: RewardBreakdown) -> RewardBreakdown:
    return RewardBreakdown(
        survival_gain=_normalize_nonnegative_exposed_metric(reward_breakdown.survival_gain),
        backlog_pressure_penalty=_normalize_nonnegative_exposed_metric(
            reward_breakdown.backlog_pressure_penalty
        ),
        invalid_action_penalty=_normalize_nonnegative_exposed_metric(
            reward_breakdown.invalid_action_penalty
        ),
        corridor_cost=_normalize_nonnegative_exposed_metric(reward_breakdown.corridor_cost),
        missed_incident_penalty=_normalize_nonnegative_exposed_metric(
            reward_breakdown.missed_incident_penalty
        ),
        total_reward=_normalize_exposed_reward(reward_breakdown.total_reward),
    )


@dataclass
class MutableAmbulance:
    ambulance_id: str
    label: str
    node_id: str
    support_level: str
    fuel_pct: float
    available_from_minute: int = 0
    last_assignment: str | None = None


@dataclass
class MutableHospital:
    hospital_id: str
    label: str
    node_id: str
    trauma_level: int
    bed_capacity: int
    current_load: int
    specialties: tuple[str, ...]


@dataclass
class MutableIncident:
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
    status: str = "pending"
    dispatch_minute: int | None = None
    ambulance_id: str | None = None
    hospital_id: str | None = None
    response_eta_minutes: float | None = None
    transport_eta_minutes: float | None = None
    survival_probability: float | None = None
    weighted_survival: float = 0.0
    used_green_corridor: bool = False


@dataclass
class CandidateContext:
    candidate: DispatchCandidate
    ambulance_id: str
    incident_id: str
    hospital_id: str
    use_green_corridor: bool
    scene_eta_minutes: float
    transport_eta_minutes: float
    fuel_after_pct: float


@dataclass
class SimulationSnapshot:
    task_config: TaskConfig
    current_time_minute: int
    ambulances: dict[str, MutableAmbulance]
    hospitals: dict[str, MutableHospital]
    incidents: dict[str, MutableIncident]
    decision_log: list[DecisionLogEntry] = field(default_factory=list)
    cumulative_reward: float = 0.0
    weighted_survival_gained: float = 0.0
    invalid_actions: int = 0
    green_corridor_used: int = 0
    last_reward_breakdown: RewardBreakdown = field(default_factory=RewardBreakdown)
    done_reason: str | None = None


def descriptor_for_task(task_config: TaskConfig) -> TaskDescriptor:
    return TaskDescriptor(
        task_id=task_config.task_id,
        title=task_config.title,
        difficulty=task_config.difficulty,
        objective=task_config.objective,
    )


def create_episode(task_id: str) -> SimulationSnapshot:
    task_config = get_task_config(task_id)
    snapshot = SimulationSnapshot(
        task_config=task_config,
        current_time_minute=task_config.start_minute,
        ambulances={
            cfg.ambulance_id: MutableAmbulance(
                ambulance_id=cfg.ambulance_id,
                label=cfg.label,
                node_id=cfg.node_id,
                support_level=cfg.support_level,
                fuel_pct=cfg.fuel_pct,
                available_from_minute=cfg.available_from_minute,
            )
            for cfg in task_config.ambulances
        },
        hospitals={
            cfg.hospital_id: MutableHospital(
                hospital_id=cfg.hospital_id,
                label=cfg.label,
                node_id=cfg.node_id,
                trauma_level=cfg.trauma_level,
                bed_capacity=cfg.bed_capacity,
                current_load=cfg.current_load,
                specialties=cfg.specialties,
            )
            for cfg in task_config.hospitals
        },
        incidents={
            cfg.incident_id: MutableIncident(
                incident_id=cfg.incident_id,
                label=cfg.label,
                node_id=cfg.node_id,
                triage=cfg.triage,
                release_minute=cfg.release_minute,
                decay_rate=cfg.decay_rate,
                required_support=cfg.required_support,
                required_hospital_level=cfg.required_hospital_level,
                description=cfg.description,
                priority_weight=cfg.priority_weight,
            )
            for cfg in task_config.incidents
        },
    )
    advance_to_decision_point(snapshot)
    return snapshot


def pending_incidents(snapshot: SimulationSnapshot) -> list[MutableIncident]:
    return [incident for incident in snapshot.incidents.values() if incident.status == "pending"]


def active_incidents(snapshot: SimulationSnapshot) -> list[MutableIncident]:
    return sorted(
        [
            incident
            for incident in pending_incidents(snapshot)
            if incident.release_minute <= snapshot.current_time_minute
        ],
        key=lambda incident: (-incident.priority_weight, incident.release_minute, incident.incident_id),
    )


def available_ambulances(snapshot: SimulationSnapshot) -> list[MutableAmbulance]:
    return sorted(
        [
            ambulance
            for ambulance in snapshot.ambulances.values()
            if ambulance.available_from_minute <= snapshot.current_time_minute
        ],
        key=lambda ambulance: (ambulance.available_from_minute, ambulance.ambulance_id),
    )


def build_candidate_contexts(snapshot: SimulationSnapshot) -> list[CandidateContext]:
    candidates: list[CandidateContext] = []
    incidents = active_incidents(snapshot)
    ambulances = available_ambulances(snapshot)
    if not incidents or not ambulances:
        return candidates

    for ambulance in ambulances:
        for incident in incidents:
            if not support_is_compatible(ambulance.support_level, incident.required_support):
                continue
            if _should_reserve_advanced_unit(snapshot, ambulance, incident):
                continue
            for hospital in snapshot.hospitals.values():
                if hospital.trauma_level > incident.required_hospital_level:
                    continue
                if hospital.current_load >= hospital.bed_capacity:
                    continue
                if not hospital_supports_incident(hospital, incident):
                    continue

                allow_corridor = (
                    incident.triage == "108"
                    and snapshot.green_corridor_used < snapshot.task_config.green_corridor_budget
                )
                corridor_options = [False, True] if allow_corridor else [False]

                for use_green_corridor in corridor_options:
                    scene_eta, scene_path = shortest_path_minutes(
                        snapshot.task_config.edges,
                        ambulance.node_id,
                        incident.node_id,
                        snapshot.current_time_minute,
                        snapshot.task_config.traffic_phase,
                        use_green_corridor,
                    )
                    transport_eta, transport_path = shortest_path_minutes(
                        snapshot.task_config.edges,
                        incident.node_id,
                        hospital.node_id,
                        snapshot.current_time_minute + int(math.ceil(scene_eta)),
                        snapshot.task_config.traffic_phase,
                        use_green_corridor,
                    )
                    travel_minutes = scene_eta + transport_eta
                    fuel_after = round(ambulance.fuel_pct - travel_minutes * FUEL_BURN_PER_MINUTE, 2)
                    if fuel_after < FUEL_RESERVE_PCT:
                        continue

                    wait_minutes = max(0.0, snapshot.current_time_minute - incident.release_minute)
                    effective_minutes = round(wait_minutes + scene_eta + 0.35 * transport_eta, 2)
                    predicted_survival = round(math.exp(-incident.decay_rate * effective_minutes), 4)
                    weighted_survival = round(predicted_survival * incident.priority_weight, 4)
                    route_labels = " -> ".join(
                        snapshot.task_config.node_labels[node_id]
                        for node_id in _compress_path(scene_path + transport_path[1:])
                    )
                    route_node_ids = _compress_path(scene_path + transport_path[1:])
                    corridor_text = " with green corridor" if use_green_corridor else ""
                    candidates.append(
                        CandidateContext(
                            candidate=DispatchCandidate(
                                candidate_id=(
                                    f"{ambulance.ambulance_id}|{incident.incident_id}|"
                                    f"{hospital.hospital_id}|{int(use_green_corridor)}"
                                ),
                                ambulance_id=ambulance.ambulance_id,
                                incident_id=incident.incident_id,
                                incident_triage=TriageLevel(incident.triage),
                                hospital_id=hospital.hospital_id,
                                use_green_corridor=use_green_corridor,
                                route_node_ids=route_node_ids,
                                scene_eta_minutes=round(scene_eta, 2),
                                transport_eta_minutes=round(transport_eta, 2),
                                effective_minutes=effective_minutes,
                                predicted_survival=predicted_survival,
                                weighted_survival=weighted_survival,
                                fuel_after_pct=max(0.0, fuel_after),
                                route_summary=route_labels,
                                why_it_is_valid=(
                                    f"Compatible {ambulance.support_level} unit, "
                                    f"{round(scene_eta, 1)} min scene ETA, "
                                    f"{round(transport_eta, 1)} min transport{corridor_text}."
                                ),
                            ),
                            ambulance_id=ambulance.ambulance_id,
                            incident_id=incident.incident_id,
                            hospital_id=hospital.hospital_id,
                            use_green_corridor=use_green_corridor,
                            scene_eta_minutes=scene_eta,
                            transport_eta_minutes=transport_eta,
                            fuel_after_pct=max(0.0, fuel_after),
                        )
                    )

    candidates.sort(
        key=lambda ctx: (
            -ctx.candidate.weighted_survival,
            ctx.candidate.effective_minutes,
            ctx.candidate.fuel_after_pct,
        )
    )
    return candidates


def apply_action(snapshot: SimulationSnapshot, action: DispatchAction) -> RewardBreakdown:
    candidate_context = None
    for context in build_candidate_contexts(snapshot):
        if (
            context.ambulance_id == action.ambulance_id
            and context.incident_id == action.incident_id
            and context.hospital_id == action.hospital_id
            and context.use_green_corridor == action.use_green_corridor
        ):
            candidate_context = context
            break

    if candidate_context is None:
        snapshot.invalid_actions += 1
        breakdown = RewardBreakdown(
            invalid_action_penalty=round(
                INVALID_ACTION_BASE_PENALTY + INVALID_ACTION_ESCALATION * (snapshot.invalid_actions - 1),
                4,
            ),
            backlog_pressure_penalty=compute_backlog_pressure(snapshot),
        )
        breakdown.total_reward = round(
            -breakdown.invalid_action_penalty - breakdown.backlog_pressure_penalty,
            4,
        )
        snapshot.cumulative_reward += breakdown.total_reward
        snapshot.last_reward_breakdown = breakdown
        snapshot.decision_log.append(
            DecisionLogEntry(
                minute=snapshot.current_time_minute,
                action_label="Invalid dispatch",
                explanation=(
                    f"Rejected {action.ambulance_id} -> {action.incident_id} -> {action.hospital_id}. "
                    "The choice was masked out because of availability, support, fuel, or hospital constraints. "
                    f"Reward breakdown: -{breakdown.invalid_action_penalty:.2f} invalid action, "
                    f"-{breakdown.backlog_pressure_penalty:.2f} active backlog."
                ),
                reward_delta=breakdown.total_reward,
            )
        )
        return breakdown

    return _apply_candidate(snapshot, candidate_context, action.rationale)


def _apply_candidate(
    snapshot: SimulationSnapshot,
    candidate_context: CandidateContext,
    rationale: str | None = None,
) -> RewardBreakdown:
    incident = snapshot.incidents[candidate_context.incident_id]
    ambulance = snapshot.ambulances[candidate_context.ambulance_id]
    hospital = snapshot.hospitals[candidate_context.hospital_id]
    origin_node_id = ambulance.node_id
    decision_minute = snapshot.current_time_minute

    incident.status = "resolved"
    incident.dispatch_minute = snapshot.current_time_minute
    incident.ambulance_id = ambulance.ambulance_id
    incident.hospital_id = hospital.hospital_id
    incident.response_eta_minutes = round(candidate_context.scene_eta_minutes, 2)
    incident.transport_eta_minutes = round(candidate_context.transport_eta_minutes, 2)
    incident.survival_probability = candidate_context.candidate.predicted_survival
    incident.weighted_survival = candidate_context.candidate.weighted_survival
    incident.used_green_corridor = candidate_context.use_green_corridor

    if candidate_context.use_green_corridor:
        snapshot.green_corridor_used += 1

    hospital.current_load += 1
    ambulance.fuel_pct = candidate_context.fuel_after_pct
    ambulance.node_id = hospital.node_id
    ambulance.last_assignment = incident.incident_id

    service_buffer = SERVICE_BUFFER_BY_TRIAGE[incident.triage]
    busy_until = snapshot.current_time_minute + int(
        math.ceil(candidate_context.scene_eta_minutes + candidate_context.transport_eta_minutes + service_buffer)
    )
    ambulance.available_from_minute = busy_until

    snapshot.weighted_survival_gained += candidate_context.candidate.weighted_survival
    breakdown = RewardBreakdown(
        survival_gain=candidate_context.candidate.weighted_survival,
        corridor_cost=CORRIDOR_COST if candidate_context.use_green_corridor else 0.0,
    )

    breakdown.missed_incident_penalty += advance_to_decision_point(snapshot)
    breakdown.backlog_pressure_penalty = compute_backlog_pressure(snapshot)
    breakdown.total_reward = round(
        breakdown.survival_gain
        - breakdown.corridor_cost
        - breakdown.backlog_pressure_penalty
        - breakdown.missed_incident_penalty,
        4,
    )

    snapshot.cumulative_reward += breakdown.total_reward
    snapshot.last_reward_breakdown = breakdown
    snapshot.decision_log.append(
        DecisionLogEntry(
            minute=decision_minute,
            action_label=(
                f"{ambulance.label} -> {incident.label} -> {hospital.label}"
                f"{' [corridor]' if candidate_context.use_green_corridor else ''}"
            ),
            explanation=_compose_decision_explanation(
                snapshot=snapshot,
                incident=incident,
                ambulance=ambulance,
                hospital=hospital,
                candidate=candidate_context.candidate,
                origin_node_id=origin_node_id,
                reward_breakdown=breakdown,
                rationale=rationale,
            ),
            reward_delta=breakdown.total_reward,
        )
    )
    return breakdown


def _compose_decision_explanation(
    snapshot: SimulationSnapshot,
    incident: MutableIncident,
    ambulance: MutableAmbulance,
    hospital: MutableHospital,
    candidate: DispatchCandidate,
    origin_node_id: str,
    reward_breakdown: RewardBreakdown,
    rationale: str | None,
) -> str:
    explanation = (
        f"Dispatched {ambulance.label} from {snapshot.task_config.node_labels[origin_node_id]} "
        f"for {incident.triage} case '{incident.label}'. {hospital.label} was valid because it has "
        f"level {hospital.trauma_level} capacity and the right specialty mix. Predicted survival "
        f"is {candidate.predicted_survival:.2f} with {candidate.scene_eta_minutes:.1f} min to scene."
    )
    explanation += (
        f" Reward breakdown: +{reward_breakdown.survival_gain:.2f} survival gain, "
        f"-{reward_breakdown.corridor_cost:.2f} corridor cost, "
        f"-{reward_breakdown.backlog_pressure_penalty:.2f} backlog pressure, "
        f"-{reward_breakdown.missed_incident_penalty:.2f} missed-incident penalty."
    )
    if rationale:
        explanation += f" Agent rationale: {rationale.strip()}"
    return explanation


def advance_to_decision_point(snapshot: SimulationSnapshot) -> float:
    missed_penalty = 0.0
    while True:
        if not pending_incidents(snapshot):
            snapshot.done_reason = "all_incidents_processed"
            return round(missed_penalty, 4)

        if active_incidents(snapshot) and build_candidate_contexts(snapshot):
            snapshot.done_reason = None
            return round(missed_penalty, 4)

        future_times: list[int] = []
        future_incident_times = [
            incident.release_minute
            for incident in pending_incidents(snapshot)
            if incident.release_minute > snapshot.current_time_minute
        ]
        future_ambulance_times = [
            ambulance.available_from_minute
            for ambulance in snapshot.ambulances.values()
            if ambulance.available_from_minute > snapshot.current_time_minute
        ]
        if future_incident_times:
            future_times.append(min(future_incident_times))
        if future_ambulance_times:
            future_times.append(min(future_ambulance_times))

        if not future_times:
            missed_penalty += mark_pending_incidents_as_missed(snapshot)
            snapshot.done_reason = "no_valid_future_dispatches"
            return round(missed_penalty, 4)

        snapshot.current_time_minute = min(future_times)


def force_finish(snapshot: SimulationSnapshot, reason: str) -> RewardBreakdown:
    breakdown = RewardBreakdown(
        missed_incident_penalty=mark_pending_incidents_as_missed(snapshot),
    )
    breakdown.total_reward = round(-breakdown.missed_incident_penalty, 4)
    if breakdown.total_reward != 0:
        snapshot.cumulative_reward += breakdown.total_reward
        snapshot.last_reward_breakdown = combine_reward_breakdowns(
            snapshot.last_reward_breakdown,
            breakdown,
        )
    snapshot.done_reason = reason
    return breakdown


def build_observation(
    snapshot: SimulationSnapshot,
    steps_taken: int,
    reward_breakdown: RewardBreakdown,
) -> DispatchObservation:
    candidates = [] if snapshot.done_reason else [context.candidate for context in build_candidate_contexts(snapshot)]
    task = descriptor_for_task(snapshot.task_config)
    done = snapshot.done_reason is not None
    score_breakdown = score_breakdown_for_snapshot(snapshot, steps_taken)
    exposed_reward_breakdown = _normalize_reward_breakdown(reward_breakdown)
    exposed_reward = exposed_reward_breakdown.total_reward

    return DispatchObservation(
        task=task,
        current_time_minute=snapshot.current_time_minute,
        max_steps=snapshot.task_config.max_steps,
        steps_taken=steps_taken,
        step_budget_remaining=max(snapshot.task_config.max_steps - steps_taken, 0),
        green_corridors_remaining=max(
            snapshot.task_config.green_corridor_budget - snapshot.green_corridor_used,
            0,
        ),
        ambulances=ambulance_snapshots(snapshot),
        incidents=incident_snapshots(snapshot),
        hospitals=hospital_snapshots(snapshot),
        available_dispatches=candidates,
        masked_actions=masked_actions(snapshot, candidates),
        decision_log=snapshot.decision_log[-4:],
        reward_breakdown=exposed_reward_breakdown,
        summary=build_summary(snapshot, candidates),
        reward=exposed_reward,
        done=done,
        metadata={
            "task_score_preview": score_breakdown["score"],
            "weighted_ratio": score_breakdown["weighted_ratio"],
            "coverage_ratio": score_breakdown["coverage_ratio"],
            "invalid_actions": snapshot.invalid_actions,
            "reward_breakdown": exposed_reward_breakdown.model_dump(),
        },
    )


def build_state(snapshot: SimulationSnapshot, steps_taken: int) -> DispatchState:
    breakdown = score_breakdown_for_snapshot(snapshot, steps_taken)
    exposed_reward_breakdown = _normalize_reward_breakdown(snapshot.last_reward_breakdown)
    return DispatchState(
        task=descriptor_for_task(snapshot.task_config),
        current_time_minute=snapshot.current_time_minute,
        max_steps=snapshot.task_config.max_steps,
        steps_taken=steps_taken,
        cumulative_reward=round(snapshot.cumulative_reward, 4),
        weighted_survival_gained=round(snapshot.weighted_survival_gained, 4),
        optimal_weighted_survival=round(optimal_weighted_survival(snapshot.task_config.task_id), 4),
        invalid_actions=snapshot.invalid_actions,
        total_incidents=len(snapshot.task_config.incidents),
        resolved_incident_ids=[incident.incident_id for incident in snapshot.incidents.values() if incident.status == "resolved"],
        missed_incident_ids=[incident.incident_id for incident in snapshot.incidents.values() if incident.status == "missed"],
        incident_outcomes=incident_outcomes(snapshot),
        ambulances=ambulance_snapshots(snapshot),
        incidents=incident_snapshots(snapshot),
        hospitals=hospital_snapshots(snapshot),
        decision_log=snapshot.decision_log,
        last_reward_breakdown=exposed_reward_breakdown,
        task_score=breakdown["score"],
        score_breakdown=breakdown,
    )


def incident_outcomes(snapshot: SimulationSnapshot) -> list[IncidentOutcome]:
    outcomes: list[IncidentOutcome] = []
    for incident in sorted(snapshot.incidents.values(), key=lambda item: item.incident_id):
        outcomes.append(
            IncidentOutcome(
                incident_id=incident.incident_id,
                triage=TriageLevel(incident.triage),
                ambulance_id=incident.ambulance_id,
                hospital_id=incident.hospital_id,
                survival_probability=round(incident.survival_probability or 0.0, 4),
                weighted_survival=round(incident.weighted_survival, 4),
                resolved=incident.status == "resolved",
                missed=incident.status == "missed",
            )
        )
    return outcomes


def ambulance_snapshots(snapshot: SimulationSnapshot) -> list[AmbulanceSnapshot]:
    result: list[AmbulanceSnapshot] = []
    for ambulance in sorted(snapshot.ambulances.values(), key=lambda item: item.ambulance_id):
        mode = (
            AmbulanceMode.AVAILABLE
            if ambulance.available_from_minute <= snapshot.current_time_minute
            else AmbulanceMode.BUSY
        )
        result.append(
            AmbulanceSnapshot(
                ambulance_id=ambulance.ambulance_id,
                label=ambulance.label,
                node_id=ambulance.node_id,
                location_name=snapshot.task_config.node_labels[ambulance.node_id],
                support_level=SupportLevel(ambulance.support_level),
                mode=mode,
                fuel_pct=round(ambulance.fuel_pct, 2),
                available_from_minute=ambulance.available_from_minute,
                last_assignment=ambulance.last_assignment,
            )
        )
    return result


def incident_snapshots(snapshot: SimulationSnapshot) -> list[IncidentSnapshot]:
    result: list[IncidentSnapshot] = []
    for incident in sorted(snapshot.incidents.values(), key=lambda item: item.incident_id):
        wait_minutes = max(0.0, snapshot.current_time_minute - incident.release_minute)
        result.append(
            IncidentSnapshot(
                incident_id=incident.incident_id,
                label=incident.label,
                node_id=incident.node_id,
                location_name=snapshot.task_config.node_labels[incident.node_id],
                triage=TriageLevel(incident.triage),
                status=incident.status,
                release_minute=incident.release_minute,
                wait_minutes=round(wait_minutes, 2),
                required_support=SupportLevel(incident.required_support),
                required_hospital_level=incident.required_hospital_level,
                decay_rate=incident.decay_rate,
                description=incident.description,
            )
        )
    return result


def hospital_snapshots(snapshot: SimulationSnapshot) -> list[HospitalSnapshot]:
    result: list[HospitalSnapshot] = []
    for hospital in sorted(snapshot.hospitals.values(), key=lambda item: item.hospital_id):
        result.append(
            HospitalSnapshot(
                hospital_id=hospital.hospital_id,
                label=hospital.label,
                node_id=hospital.node_id,
                location_name=snapshot.task_config.node_labels[hospital.node_id],
                trauma_level=hospital.trauma_level,
                bed_capacity=hospital.bed_capacity,
                current_load=hospital.current_load,
                specialties=list(hospital.specialties),
            )
        )
    return result


def masked_actions(
    snapshot: SimulationSnapshot,
    candidates: list[DispatchCandidate],
) -> list[MaskedActionReason]:
    reasons: list[MaskedActionReason] = []
    active = active_incidents(snapshot)
    candidate_ambulance_ids = {candidate.ambulance_id for candidate in candidates}

    for ambulance in sorted(snapshot.ambulances.values(), key=lambda item: item.ambulance_id):
        if ambulance.available_from_minute > snapshot.current_time_minute:
            reasons.append(
                MaskedActionReason(
                    subject_id=ambulance.ambulance_id,
                    reason=f"Busy until minute {ambulance.available_from_minute}.",
                )
            )
            continue
        if ambulance.fuel_pct < FUEL_RESERVE_PCT:
            reasons.append(
                MaskedActionReason(
                    subject_id=ambulance.ambulance_id,
                    reason=f"Fuel below reserve threshold of {FUEL_RESERVE_PCT:.0f}%.",
                )
            )
            continue
        if active and ambulance.ambulance_id not in candidate_ambulance_ids:
            reasons.append(
                MaskedActionReason(
                    subject_id=ambulance.ambulance_id,
                    reason="No valid assignment because of support mismatch, fuel reserve, or hospital constraints.",
                )
            )

    for hospital in sorted(snapshot.hospitals.values(), key=lambda item: item.hospital_id):
        if hospital.current_load >= hospital.bed_capacity:
            reasons.append(
                MaskedActionReason(
                    subject_id=hospital.hospital_id,
                    reason="Hospital is at capacity and cannot accept another transfer right now.",
                )
            )

    return reasons


def build_summary(snapshot: SimulationSnapshot, candidates: list[DispatchCandidate]) -> str:
    active = active_incidents(snapshot)
    available = available_ambulances(snapshot)
    lines = [
        f"Task {snapshot.task_config.task_id} ({snapshot.task_config.difficulty}).",
        f"Minute {snapshot.current_time_minute}.",
        f"{len(active)} active incident(s), {len(available)} available ambulance(s).",
    ]
    for incident in active:
        lines.append(
            f"{incident.incident_id}: triage {incident.triage}, waiting "
            f"{max(snapshot.current_time_minute - incident.release_minute, 0)} min at "
            f"{snapshot.task_config.node_labels[incident.node_id]}."
        )
    if candidates:
        best = candidates[0]
        lines.append(
            f"Top candidate: {best.ambulance_id} -> {best.incident_id} -> {best.hospital_id} "
            f"(weighted survival {best.weighted_survival:.2f})."
        )
    else:
        lines.append("No valid dispatch candidates remain.")
    return " ".join(lines)


def score_breakdown_for_snapshot(snapshot: SimulationSnapshot, steps_taken: int) -> dict[str, float]:
    optimal = optimal_weighted_survival(snapshot.task_config.task_id)
    weighted_ratio = (
        min(snapshot.weighted_survival_gained / optimal, 1.0) if optimal > 0 else 1.0
    )
    resolved = sum(1 for incident in snapshot.incidents.values() if incident.status == "resolved")
    coverage_ratio = resolved / len(snapshot.incidents) if snapshot.incidents else 1.0
    critical_incidents = [incident for incident in snapshot.incidents.values() if incident.triage == "108"]
    critical_resolved = sum(1 for incident in critical_incidents if incident.status == "resolved")
    critical_coverage = (
        critical_resolved / len(critical_incidents) if critical_incidents else 1.0
    )
    action_hygiene = max(
        0.0,
        1.0 - (snapshot.invalid_actions / max(snapshot.task_config.max_steps, 1)),
    )
    weighted_ratio = _clamp_score_metric(weighted_ratio)
    coverage_ratio = _clamp_score_metric(coverage_ratio)
    critical_coverage = _clamp_score_metric(critical_coverage)
    action_hygiene = _clamp_score_metric(action_hygiene)
    raw_score = (
        0.60 * weighted_ratio
        + 0.15 * coverage_ratio
        + 0.15 * critical_coverage
        + 0.10 * action_hygiene
    )
    score = _clamp_score_metric(raw_score)
    return {
        "score": round(score, 4),
        "weighted_ratio": round(weighted_ratio, 4),
        "coverage_ratio": round(coverage_ratio, 4),
        "critical_coverage": round(critical_coverage, 4),
        "action_hygiene": round(action_hygiene, 4),
    }


def compute_backlog_pressure(snapshot: SimulationSnapshot) -> float:
    penalty = 0.0
    for incident in active_incidents(snapshot):
        wait_minutes = max(snapshot.current_time_minute - incident.release_minute, 0)
        urgency_multiplier = CRITICAL_WAIT_MULTIPLIER if incident.triage == "108" else 1.0
        penalty += incident.priority_weight * (
            ACTIVE_INCIDENT_HOLDING_PENALTY + WAIT_PENALTY_PER_MINUTE * wait_minutes
        ) * urgency_multiplier
    return round(penalty, 4)


def mark_pending_incidents_as_missed(snapshot: SimulationSnapshot) -> float:
    penalty = 0.0
    for incident in pending_incidents(snapshot):
        incident.status = "missed"
        penalty += MISSED_INCIDENT_PENALTY[incident.triage]
    return round(penalty, 4)


def combine_reward_breakdowns(
    first: RewardBreakdown,
    second: RewardBreakdown,
) -> RewardBreakdown:
    return RewardBreakdown(
        survival_gain=round(first.survival_gain + second.survival_gain, 4),
        backlog_pressure_penalty=round(
            first.backlog_pressure_penalty + second.backlog_pressure_penalty,
            4,
        ),
        invalid_action_penalty=round(
            first.invalid_action_penalty + second.invalid_action_penalty,
            4,
        ),
        corridor_cost=round(first.corridor_cost + second.corridor_cost, 4),
        missed_incident_penalty=round(
            first.missed_incident_penalty + second.missed_incident_penalty,
            4,
        ),
        total_reward=round(first.total_reward + second.total_reward, 4),
    )


@lru_cache(maxsize=None)
def optimal_weighted_survival(task_id: str) -> float:
    task_config = get_task_config(task_id)
    if task_config.reference_optimal_weighted_survival is not None:
        return round(task_config.reference_optimal_weighted_survival, 4)
    snapshot = create_episode(task_id)
    return round(_oracle(snapshot), 4)


def _oracle(snapshot: SimulationSnapshot) -> float:
    if snapshot.done_reason is not None:
        return snapshot.weighted_survival_gained

    candidates = build_candidate_contexts(snapshot)
    if not candidates:
        terminal_snapshot = copy.deepcopy(snapshot)
        force_finish(terminal_snapshot, "oracle_no_valid_dispatch")
        return terminal_snapshot.weighted_survival_gained

    best = snapshot.weighted_survival_gained
    for candidate in candidates:
        branch = copy.deepcopy(snapshot)
        _apply_candidate(branch, candidate, rationale=None)
        best = max(best, _oracle(branch))
    return best


def shortest_path_minutes(
    edges: tuple[RoadEdge, ...],
    start: str,
    end: str,
    current_time_minute: int,
    traffic_phase: str,
    use_green_corridor: bool,
) -> tuple[float, list[str]]:
    if start == end:
        return 0.0, [start]

    graph: dict[str, list[RoadEdge]] = {}
    for edge in edges:
        graph.setdefault(edge.start, []).append(edge)

    queue: list[tuple[float, str, list[str]]] = [(0.0, start, [start])]
    visited: dict[str, float] = {start: 0.0}

    while queue:
        minutes, node, path = heapq.heappop(queue)
        if node == end:
            return round(minutes, 2), path
        if minutes > visited.get(node, float("inf")):
            continue
        for edge in graph.get(node, []):
            edge_minutes = _edge_minutes(
                edge=edge,
                current_time_minute=current_time_minute,
                traffic_phase=traffic_phase,
                use_green_corridor=use_green_corridor,
            )
            total = minutes + edge_minutes
            if total < visited.get(edge.end, float("inf")):
                visited[edge.end] = total
                heapq.heappush(queue, (total, edge.end, path + [edge.end]))

    raise ValueError(f"No route found from {start} to {end}")


def _edge_minutes(
    edge: RoadEdge,
    current_time_minute: int,
    traffic_phase: str,
    use_green_corridor: bool,
) -> float:
    phase_factor = TRAFFIC_PHASE_FACTORS.get(traffic_phase, 1.0)
    time_pressure_factor = 1.0 + min(current_time_minute, 20) * 0.01
    corridor_factor = CORRIDOR_DISCOUNT if use_green_corridor else 1.0
    return edge.base_minutes * edge.congestion_multiplier * phase_factor * time_pressure_factor * corridor_factor


def support_is_compatible(ambulance_support: str, required_support: str) -> bool:
    if required_support == "advanced":
        return ambulance_support == "advanced"
    if required_support == "maternal":
        return ambulance_support in {"maternal", "advanced"}
    return True


def hospital_supports_incident(hospital: MutableHospital, incident: MutableIncident) -> bool:
    specialty = "maternity" if incident.required_support == "maternal" else "cardiac" if "CARDIAC" in incident.incident_id else "trauma"
    return specialty in hospital.specialties


def _should_reserve_advanced_unit(
    snapshot: SimulationSnapshot,
    ambulance: MutableAmbulance,
    incident: MutableIncident,
) -> bool:
    if ambulance.support_level != "advanced" or incident.required_support != "maternal":
        return False

    active_critical_incidents = [
        candidate_incident
        for candidate_incident in active_incidents(snapshot)
        if candidate_incident.triage == "108"
    ]
    if not active_critical_incidents:
        return False

    maternal_units_available = [
        unit
        for unit in available_ambulances(snapshot)
        if unit.support_level == "maternal"
    ]
    return bool(maternal_units_available)


def _compress_path(path: list[str]) -> list[str]:
    compressed: list[str] = []
    for node in path:
        if not compressed or compressed[-1] != node:
            compressed.append(node)
    return compressed
