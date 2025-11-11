"""Question bank for the compatibility test."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Literal, Tuple

NeedKey = Literal[
    "acceptance",
    "care",
    "safety",
    "passion",
    "support",
    "recognition",
]

Orientation = Literal["receive", "give"]
Audience = Literal["all", "teen", "adult"]


@dataclass(frozen=True)
class Question:
    """Single question configuration."""

    id: str
    need: NeedKey
    orientation: Orientation
    audience: Audience
    text: Dict[str, str]
    example: Dict[str, str]


NEED_TITLES: Dict[str, Dict[str, str]] = {
    "acceptance": {"ru": "Принятие", "en": "Acceptance"},
    "care": {"ru": "Забота", "en": "Care"},
    "safety": {"ru": "Безопасность", "en": "Safety"},
    "passion": {"ru": "Страсть и энергия", "en": "Spark & Energy"},
    "support": {"ru": "Материальная поддержка", "en": "Support & Resources"},
    "recognition": {"ru": "Признание", "en": "Recognition"},
}


def _q(
    qid: str,
    need: NeedKey,
    orientation: Orientation,
    audience: Audience,
    ru: Tuple[str, str],
    en: Tuple[str, str],
) -> Question:
    return Question(
        id=qid,
        need=need,
        orientation=orientation,
        audience=audience,
        text={"ru": ru[0], "en": en[0]},
        example={"ru": ru[1], "en": en[1]},
    )


QUESTION_BANK: List[Question] = [
    _q(
        "acceptance_receive",
        "acceptance",
        "receive",
        "all",
        (
            "Мне важно, чтобы друг принимал мои странности и не пытался меня менять.",
            "Если можно говорить о своём хобби без осуждения — ставь 5.",
        ),
        (
            "I want my friend to accept my quirks without trying to fix me.",
            "If you can geek out about your hobby without judgement, rate it 5.",
        ),
    ),
    _q(
        "acceptance_give",
        "acceptance",
        "give",
        "all",
        (
            "Легко ли тебе поддерживать привычки друга, даже если они кажутся странными?",
            "Если ты спокойно реагируешь на коллекцию резиновых уток — это 5.",
        ),
        (
            "Is it easy for you to support a friend's habits, even the odd ones?",
            "If rubber-duck collections don't scare you — that's a 5.",
        ),
    ),
    _q(
        "care_receive",
        "care",
        "receive",
        "all",
        (
            "Насколько важно, чтобы друг замечал, когда тебе нужна забота?",
            "Например, написал «как ты?» без напоминаний — ставь выше.",
        ),
        (
            "How important is it that a friend notices when you need care?",
            "Texting you ‘how are you?’ without prompts — score it higher.",
        ),
    ),
    _q(
        "care_give",
        "care",
        "give",
        "all",
        (
            "Как легко тебе делать тёплые мелочи для друга?",
            "Если сам(а) приносишь чай, когда он устал — ставь 4-5.",
        ),
        (
            "How easy is it for you to do caring little things?",
            "Bringing tea when they look tired — that's a 4-5.",
        ),
    ),
    _q(
        "safety_receive",
        "safety",
        "receive",
        "all",
        (
            "Насколько тебе важно чувствовать защиту и поддержку от друга?",
            "Если ждёшь, что он встанет на твою сторону — ставь высоко.",
        ),
        (
            "How much do you need a friend to keep you safe and backed up?",
            "If you expect them to stand up for you — score it high.",
        ),
    ),
    _q(
        "safety_give",
        "safety",
        "give",
        "all",
        (
            "Готов(а) ли ты вступиться за друга, даже если немного страшно?",
            "Если звонишь вместе в важные места без паники — ставь 4-5.",
        ),
        (
            "Will you stand up for a friend even if it's a bit scary?",
            "Calling the office together without panic — mark it 4-5.",
        ),
    ),
    _q(
        "passion_receive_minor",
        "passion",
        "receive",
        "teen",
        (
            "Насколько тебе важны совместные яркие эмоции и приключения с другом?",
            "Если мечтаешь о совместных квестах и путешествиях — ставь высоко.",
        ),
        (
            "How much do you crave fun adventures and bright emotions with a friend?",
            "If you dream about shared quests or trips — rate it high.",
        ),
    ),
    _q(
        "passion_receive_adult",
        "passion",
        "receive",
        "adult",
        (
            "Насколько тебе важно, чтобы в отношениях было много драйва и яркости?",
            "Если любишь неожиданные свидания и смелые планы — ставь выше.",
        ),
        (
            "How important is lively energy and spark in your relationship?",
            "If surprise dates and bold plans are your jam — score it high.",
        ),
    ),
    _q(
        "passion_give",
        "passion",
        "give",
        "all",
        (
            "Легко ли тебе предлагать активные идеи и заряжать другого энергией?",
            "Если сам(а) зовёшь на приключения и шутки — ставь 4-5.",
        ),
        (
            "Is it easy for you to spark energy and pitch fun ideas?",
            "If you initiate adventures and jokes — go with 4-5.",
        ),
    ),
    _q(
        "support_receive",
        "support",
        "receive",
        "all",
        (
            "Насколько важно, чтобы друг делился ресурсами и возможностями?",
            "Если ждёшь, что он помнит про любимый кофе — ставь выше.",
        ),
        (
            "How important is it that a friend shares resources and opportunities?",
            "If you love when they remember your fave coffee — rate it higher.",
        ),
    ),
    _q(
        "support_give",
        "support",
        "give",
        "all",
        (
            "Готов(а) ли ты делиться своими ресурсами, контактами и временем?",
            "Если ловишь себя на подарках без повода — ставь 4-5.",
        ),
        (
            "Are you ready to share resources, contacts and time?",
            "If surprise gifts happen regularly — that's a 4-5.",
        ),
    ),
    _q(
        "recognition_receive",
        "recognition",
        "receive",
        "all",
        (
            "Насколько важно слышать искреннюю гордость и похвалу от друга?",
            "Если ждёшь, что расскажут другим о твоих успехах — ставь высоко.",
        ),
        (
            "How much do you need genuine pride and praise from a friend?",
            "If you want them to brag about your wins — rate it high.",
        ),
    ),
    _q(
        "recognition_give",
        "recognition",
        "give",
        "all",
        (
            "Легко ли тебе восхищаться другом и говорить об этом вслух?",
            "Если постоянно хвалишь и поддерживаешь — ставь 4-5.",
        ),
        (
            "Is it easy to admire your friend out loud?",
            "If you cheerlead them regularly — give it 4-5.",
        ),
    ),
]


def iter_questions(age_group: Literal["minor", "adult"], lang: str) -> Iterable[Question]:
    """Yield questions filtered by age group while respecting order."""

    for question in QUESTION_BANK:
        if question.audience == "all":
            yield question
        elif question.audience == "teen" and age_group == "minor":
            yield question
        elif question.audience == "adult" and age_group == "adult":
            yield question


def need_title(need: NeedKey, lang: str) -> str:
    lang_map = NEED_TITLES.get(need, {})
    return lang_map.get(lang) or lang_map.get("en") or need
