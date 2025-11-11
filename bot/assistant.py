"""Rule-based companion assistant that uses the knowledge base and report."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

from .compatibility import CompatibilityReport, NeedCompatibility
from .questions import NeedKey, need_title

BAD_WORDS = {
    "ru": ["чёрт", "блин", "грязь", "***", "дурак", "свол"],
    "en": ["damn", "stupid", "idiot", "f***"],
}

RELATIONSHIP_KEYWORDS = {
    "ru": ["отнош", "друг", "пара", "конфликт", "люб", "команда", "совмест"],
    "en": ["relation", "friend", "team", "conflict", "love", "pair", "compat"],
}

NEED_TIPS: Dict[NeedKey, Dict[str, str]] = {
    "acceptance": {
        "ru": "Проговаривайте свои особенности заранее и спрашивайте, что поддерживает другого.",
        "en": "Share your quirks openly and ask what makes the other feel welcomed.",
    },
    "care": {
        "ru": "Помните о маленьких жестах: сообщения, напитки, помощь в рутине.",
        "en": "Lean on small gestures: check-ins, warm drinks, help with routine chores.",
    },
    "safety": {
        "ru": "Договаривайтесь, кто и в каких ситуациях поддерживает и защищает.",
        "en": "Align on who protects whom in tricky moments and how you signal for help.",
    },
    "passion": {
        "ru": "Планируйте совместные активности, где один заряжает, а второй вдохновляется.",
        "en": "Plan shared adventures so one sparks ideas and the other fuels the vibe.",
    },
    "support": {
        "ru": "Открыто говорите о ресурсах и договоритесь, чем удобно делиться.",
        "en": "Talk openly about resources and what you are happy to share.",
    },
    "recognition": {
        "ru": "Не копите похвалу — отмечайте успехи друг друга и прогресс.",
        "en": "Don't store compliments — celebrate wins and progress out loud.",
    },
}

KNOWLEDGE_PATH = Path(__file__).resolve().parent.parent / "description of the psychological compatibility model.txt"


@dataclass
class AssistantContext:
    report: CompatibilityReport
    language: str


def _load_knowledge() -> str:
    try:
        return KNOWLEDGE_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


KNOWLEDGE_TEXT = _load_knowledge()


def _contains_bad_language(message: str, lang: str) -> bool:
    low = message.lower()
    for word in BAD_WORDS.get(lang, []):
        if word and word in low:
            return True
    return False


def _in_scope(message: str, lang: str) -> bool:
    low = message.lower()
    keywords = RELATIONSHIP_KEYWORDS.get(lang, [])
    return any(word in low for word in keywords)


def _need_order(needs: Iterable[NeedCompatibility]) -> List[NeedCompatibility]:
    return sorted(needs, key=lambda item: item.score)


def build_response(context: AssistantContext, question: str) -> Dict[str, str]:
    lang = context.language if context.language in NEED_TIPS["acceptance"] else "en"
    if _contains_bad_language(question, lang):
        return {"type": "bad_language"}
    if not _in_scope(question, lang):
        return {"type": "out_of_scope"}

    ordered = _need_order(context.report.needs)
    low_focus = ordered[0]
    high_focus = ordered[-1]

    tip = NEED_TIPS.get(low_focus.need, {}).get(lang) or NEED_TIPS[low_focus.need]["en"]
    celebrate = NEED_TIPS.get(high_focus.need, {}).get(lang) or NEED_TIPS[high_focus.need]["en"]

    reference = KNOWLEDGE_TEXT[:400].strip()

    return {
        "type": "advice",
        "low_need": low_focus.need,
        "high_need": high_focus.need,
        "tip": tip,
        "celebrate": celebrate,
        "knowledge_snippet": reference,
    }
