"""Formatting helpers for compatibility reports."""
from __future__ import annotations

from typing import Iterable

from .compatibility import CompatibilityReport, categorize_need
from .localization import translate
from .questions import NeedKey, need_title


def _tone_key(score: float) -> str:
    if score >= 75:
        return "tone_high"
    if score >= 55:
        return "tone_medium"
    return "tone_low"


def format_need_lines(report: CompatibilityReport, lang: str) -> Iterable[str]:
    for need in report.needs:
        status_key = categorize_need(need.score)
        status = translate(lang, status_key)
        yield translate(lang, "need_block", need=need_title(need.need, lang), status=status)


def format_outcome(report: CompatibilityReport, lang: str) -> str:
    probabilities = report.outcome_probabilities
    ordered = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)
    if not ordered:
        return ""
    primary_key, primary_prob = ordered[0]
    secondary_key, secondary_prob = ordered[1] if len(ordered) > 1 else (ordered[0][0], ordered[0][1])
    return translate(
        lang,
        "outcome_summary",
        primary=translate(lang, f"outcome_{primary_key}"),
        prob=f"{primary_prob}",
        secondary=translate(lang, f"outcome_{secondary_key}"),
        secondary_prob=f"{secondary_prob}",
    )


def render_report(report: CompatibilityReport, lang: str) -> str:
    tone_key = _tone_key(report.overall_score)
    summary = translate(
        lang,
        "report_summary",
        score=f"{report.overall_score}",
        tone=translate(lang, tone_key),
    )
    lines = [
        translate(
            lang,
            "report_header",
            name_a=report.participant_a.name,
            name_b=report.participant_b.name,
        ),
        summary,
        format_outcome(report, lang),
        *format_need_lines(report, lang),
        translate(lang, "ask_feedback"),
        translate(lang, "call_assistant"),
    ]
    return "\n".join(filter(None, lines))
