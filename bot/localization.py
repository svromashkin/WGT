"""Utility helpers for localized phrases used by the Telegram bot."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping

SUPPORTED_LANGUAGES = ("ru", "en")


@dataclass(frozen=True)
class LocalePack:
    code: str
    title: str
    messages: Mapping[str, str]


_LANGUAGE_PACKS: Dict[str, LocalePack] = {
    "ru": LocalePack(
        code="ru",
        title="Русский",
        messages={
            "language_prompt": "Выбери язык, на котором тебе удобнее общаться:",
            "age_prompt": "Сколько тебе лет? (Нужно для корректного теста)",
            "age_minor": "Младше 18",
            "age_adult": "18 и старше",
            "consent": (
                "Этот тест не является строгим руководством к действию. "
                "Он помогает задуматься и бережно улучшить отношения. Продолжим?"
            ),
            "consent_yes": "Да, поехали!",
            "consent_no": "Пока нет",
            "ask_name": "Как тебя зовут? Можно псевдоним.",
            "start_new_or_join": "Привет! Ты хочешь начать новый тест или присоединиться к партнёру?",
            "start_new": "Начать новый тест",
            "join_existing": "У меня есть код",
            "request_partner_code": "Введи код, который отправил(а) друг/подруга.",
            "invalid_code": "Упс, такого кода нет. Проверь цифры и попробуй снова.",
            "intro": (
                "Отлично! Сейчас ты оценишь, что тебе важно получать и легко ли дарить другим. "
                "Оцени каждый пункт от 1 (совсем не про меня) до 5 (очень про меня)."
            ),
            "question_receive": "Насколько тебе важно получать это от друга?",
            "question_give": "Насколько легко тебе дарить это другу?",
            "scale_hint": "1 — совсем не важно, 3 — что-то среднее, 5 — важно до мурашек!",
            "thanks_first": (
                "Спасибо! Ты герой. Передай этот код другу: <code>{code}</code>. "
                "Как только он пройдёт тест, вернёмся с отчётом и шутками."
            ),
            "already_waiting": "Мы уже ждём второго участника. Напомни другу про код: <code>{code}</code>.",
            "partner_joined": "Отлично! Второй участник готов. Держитесь, сейчас будет серия вопросов.",
            "report_header": "🌈 Итоги для {name_a} и {name_b}",
            "report_summary": "Средняя совместимость: {score}% — {tone}",
            "tone_high": "похоже, вы друг другу в радость!",
            "tone_medium": "много потенциала, но стоит обсудить ожидания",
            "tone_low": "есть серьёзные зоны роста, зато теперь вы знаете, где подтянуть суперсилы",
            "outcome_long_happy": "Долго и счастливо",
            "outcome_short_happy": "Недолго, но ярко",
            "outcome_short_unhappy": "Недолго и нервно",
            "outcome_long_unhappy": "Долго и сложно",
            "outcome_summary": "Прогноз: {primary} (вероятность {prob}%). Альтернатива: {secondary} ({secondary_prob}%).",
            "need_block": "{need}: {status}",
            "need_status_great": "супер! вы закрываете друг друга почти без усилий",
            "need_status_good": "в целом хорошо, но полезно обсудить детали",
            "need_status_watch": "нужно внимание: договоритесь, кто и как поддерживает",
            "need_status_risk": "зона риска: стоит придумать план действий и страховочный юмор",
            "ask_feedback": "Как вам отчёт? Нажми /feedback, чтобы оставить отзыв и прокачать модель.",
            "call_assistant": "Нужен совет прямо сейчас? Жми /companion — ассистент уже заварил чай.",
            "waiting_partner": "Ждём второго участника. Как только присоединится — продолжим.",
            "feedback_prompt": "Расскажи, что понравилось и что стоит улучшить. Я передам команде.",
            "feedback_thanks": "Спасибо за отзыв! Он поможет сделать тест ещё точнее.",
            "companion_intro": (
                "Я ассистент модели «Нам хорошо вместе». Расскажи, что волнует, и я подскажу."),
            "companion_out_of_scope": (
                "Кажется, вопрос не про совместимость. Давай вернёмся к теме отношений,"
                " а за другими ответами — к профильным специалистам."),
            "companion_bad_language": (
                "Понимаю эмоции, но давай без грубостей. Лучше сфокусируемся на том, как поддержать друг друга."),
            "companion_no_session": "Сначала пройдите тест вдвоём, а затем возвращайтесь за советом через /companion.",
            "companion_ack": "Понял! Вот что могу подсказать:"
        },
    ),
    "en": LocalePack(
        code="en",
        title="English",
        messages={
            "language_prompt": "Pick the language you feel comfy with:",
            "age_prompt": "How old are you? (We tailor questions by age)",
            "age_minor": "Under 18",
            "age_adult": "18 and older",
            "consent": (
                "This test is not a strict life manual. It helps you reflect and care for relationships. Ready to continue?"
            ),
            "consent_yes": "Yes, let's go!",
            "consent_no": "Not now",
            "ask_name": "What's your name or nickname?",
            "start_new_or_join": "Hi! Do you want to start a new test or join with a partner code?",
            "start_new": "Start a new test",
            "join_existing": "I have a code",
            "request_partner_code": "Enter the code your friend shared.",
            "invalid_code": "Oops, that code is unknown. Double-check the digits and try again.",
            "intro": (
                "Great! You will rate what matters to receive and how easy it is to give. "
                "Score each statement from 1 (not me) to 5 (totally me)."
            ),
            "question_receive": "How important is it for you to receive this?",
            "question_give": "How easy is it for you to give this?",
            "scale_hint": "1 — not important, 3 — somewhere in the middle, 5 — mega important!",
            "thanks_first": (
                "Thanks! You're awesome. Share this code with your partner: <code>{code}</code>. "
                "Once they finish, you'll both get the report and some friendly sarcasm."
            ),
            "already_waiting": "We're already waiting for the partner. Remind them of the code: <code>{code}</code>.",
            "partner_joined": "Sweet! Partner joined. Brace yourselves for the question marathon.",
            "report_header": "🌈 Results for {name_a} & {name_b}",
            "report_summary": "Average compatibility: {score}% — {tone}",
            "tone_high": "looks like you spark joy for each other!",
            "tone_medium": "lots of potential — just align your expectations",
            "tone_low": "serious growth zone, but hey, now you know where to boost your superpowers",
            "outcome_long_happy": "Long & happy",
            "outcome_short_happy": "Short but happy",
            "outcome_short_unhappy": "Short and bumpy",
            "outcome_long_unhappy": "Long and tough",
            "outcome_summary": "Forecast: {primary} (probability {prob}%). Backup plan: {secondary} ({secondary_prob}%).",
            "need_block": "{need}: {status}",
            "need_status_great": "awesome! you cover each other with almost zero effort",
            "need_status_good": "mostly good — a quick chat will keep it smooth",
            "need_status_watch": "needs attention: plan how you support each other",
            "need_status_risk": "risk zone: design a plan and keep humor handy",
            "ask_feedback": "How was the report? Type /feedback to share thoughts and sharpen the model.",
            "call_assistant": "Need advice now? Use /companion — the assistant already brewed tea.",
            "waiting_partner": "Waiting for the partner. We'll resume as soon as they join.",
            "feedback_prompt": "Tell us what you liked and what needs polish. We'll pass it to the team.",
            "feedback_thanks": "Thanks! Your feedback helps us improve the test.",
            "companion_intro": "I'm the companion AI for 'We Feel Good Together'. Share your concern and I'll help.",
            "companion_out_of_scope": (
                "That seems off-topic. Let's stick to compatibility, and for everything else please reach out to the right experts."
            ),
            "companion_bad_language": (
                "I feel the emotion, yet let's keep it polite. Focusing on mutual support works better!"
            ),
            "companion_no_session": "Please complete the joint test first, then return via /companion for advice.",
            "companion_ack": "Got it! Here's my take:"
        },
    ),
}


def available_languages() -> Mapping[str, LocalePack]:
    """Return dictionary of supported language packs."""

    return _LANGUAGE_PACKS


def translate(lang: str, key: str, **kwargs: str) -> str:
    """Return localized message by key with optional formatting."""

    lang = lang if lang in _LANGUAGE_PACKS else "ru"
    template = _LANGUAGE_PACKS[lang].messages.get(key)
    if template is None:
        template = _LANGUAGE_PACKS["en"].messages.get(key, key)
    return template.format(**kwargs)
