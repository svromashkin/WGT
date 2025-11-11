"""Compatibility scoring logic."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Tuple

from .questions import NeedKey, Orientation


@dataclass
class ParticipantProfile:
    name: str
    answers: Dict[str, Dict[Orientation, int]]  # need -> orientation -> value (1..5)


@dataclass
class NeedCompatibility:
    need: NeedKey
    score: float  # 0..1
    alignment_a: float  # match for A receiving from B
    alignment_b: float  # match for B receiving from A


@dataclass
class CompatibilityReport:
    participant_a: ParticipantProfile
    participant_b: ParticipantProfile
    needs: Tuple[NeedCompatibility, ...]
    overall_score: float  # percent 0..100
    outcome_probabilities: Dict[str, float]


def _match(receive: int, give: int) -> float:
    """Return normalized compatibility between 0 and 1."""

    # max difference is 4 (1..5 scale)
    diff = abs(receive - give)
    return max(0.0, 1.0 - diff / 4.0)


def _need_score(a: ParticipantProfile, b: ParticipantProfile, need: NeedKey) -> NeedCompatibility:
    answers_a = a.answers.get(need, {})
    answers_b = b.answers.get(need, {})
    receive_a = answers_a.get("receive")
    give_a = answers_a.get("give")
    receive_b = answers_b.get("receive")
    give_b = answers_b.get("give")

    alignment_a = _match(receive_a or 0, give_b or 0) if receive_a and give_b else 0.0
    alignment_b = _match(receive_b or 0, give_a or 0) if receive_b and give_a else 0.0

    if receive_a is None or give_b is None or receive_b is None or give_a is None:
        score = (alignment_a + alignment_b) / max(1, int(alignment_a > 0) + int(alignment_b > 0))
    else:
        score = (alignment_a + alignment_b) / 2

    return NeedCompatibility(need=need, score=score, alignment_a=alignment_a, alignment_b=alignment_b)


def _normalize(probabilities: Dict[str, float]) -> Dict[str, float]:
    total = sum(probabilities.values()) or 1.0
    return {key: round(value / total * 100, 1) for key, value in probabilities.items()}


def _outcome_probabilities(needs: Iterable[NeedCompatibility], overall_score: float) -> Dict[str, float]:
    harmony = overall_score / 100
    gaps = [1 - need.score for need in needs]
    avg_gap = sum(gaps) / len(gaps) if gaps else 0.0

    long_happy = max(0.0, harmony * (1 - avg_gap) + 0.1)
    short_happy = max(0.0, harmony * avg_gap + (1 - harmony) * (1 - avg_gap) * 0.6)
    long_unhappy = max(0.0, (1 - harmony) * avg_gap * 0.8)
    short_unhappy = max(0.0, (1 - harmony) * (0.4 + avg_gap))

    return _normalize(
        {
            "long_happy": long_happy,
            "short_happy": short_happy,
            "short_unhappy": short_unhappy,
            "long_unhappy": long_unhappy,
        }
    )


def build_report(participant_a: ParticipantProfile, participant_b: ParticipantProfile, needs: Iterable[NeedKey]) -> CompatibilityReport:
    need_results = tuple(_need_score(participant_a, participant_b, need) for need in needs)
    overall = sum(need.score for need in need_results) / len(need_results) if need_results else 0.0
    probabilities = _outcome_probabilities(need_results, overall * 100)

    return CompatibilityReport(
        participant_a=participant_a,
        participant_b=participant_b,
        needs=need_results,
        overall_score=round(overall * 100, 1),
        outcome_probabilities=probabilities,
    )


def categorize_need(score: float) -> str:
    if score >= 0.75:
        return "need_status_great"
    if score >= 0.6:
        return "need_status_good"
    if score >= 0.45:
        return "need_status_watch"
    return "need_status_risk"
