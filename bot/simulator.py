"""Command-line simulator for testing the compatibility flow without Telegram."""
from __future__ import annotations

import argparse
from typing import Dict, Iterable, List

from .assistant import AssistantContext, build_response
from .compatibility import ParticipantProfile, build_report
from .localization import available_languages, translate
from .questions import QUESTION_BANK, NeedKey, Question, iter_questions, need_title
from .reporting import render_report


def _list_languages() -> str:
    packs = available_languages()
    return ", ".join(f"{code} ({pack.title})" for code, pack in packs.items())


def _resolve_language(arg_lang: str | None) -> str:
    packs = available_languages()
    if arg_lang and arg_lang in packs:
        return arg_lang
    if arg_lang:
        print(
            f"[!] Язык '{arg_lang}' не поддерживается. Доступны: {_list_languages()}. "
            "Используем 'ru'."
        )
    return "ru"


def _prompt(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return ""


def _prompt_age(participant: str, lang: str) -> str:
    while True:
        raw = _prompt(
            translate(
                lang,
                "age_prompt",
            )
            + f"\n[{participant}] > "
        ).strip()
        if not raw:
            print(translate(lang, "age_adult"))
            return "adult"
        if raw.lower() in {"adult", "взрослый", "старше", "18", translate(lang, "age_adult").lower()}:
            return "adult"
        if raw.lower() in {"minor", "подросток", "младше", "<18", translate(lang, "age_minor").lower()}:
            return "minor"
        try:
            value = int(raw)
        except ValueError:
            print("Введите возраст числом или выберите вариант 'adult/minor'.")
            continue
        return "minor" if value < 18 else "adult"


def _prompt_name(participant: str, lang: str) -> str:
    name = _prompt(translate(lang, "ask_name") + f"\n[{participant}] > ").strip()
    return name or participant


def _ask_score(question: Question, lang: str) -> int:
    orientation_key = "question_receive" if question.orientation == "receive" else "question_give"
    text = question.text.get(lang) or question.text.get("en") or ""
    example = question.example.get(lang) or question.example.get("en") or ""
    while True:
        raw = _prompt(
            f"\n{translate(lang, orientation_key)}\n{text}\n{example}\n"
            f"{translate(lang, 'scale_hint')}\nОценка (1-5) > "
        ).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Пожалуйста, введите число от 1 до 5.")
            continue
        if 1 <= value <= 5:
            return value
        print("Число должно быть между 1 и 5.")


def _collect_answers(participant: str, lang: str, age_group: str) -> Dict[NeedKey, Dict[str, int]]:
    print("\n" + translate(lang, "intro"))
    answers: Dict[NeedKey, Dict[str, int]] = {}
    for question in iter_questions(age_group, lang):
        answers.setdefault(question.need, {})[question.orientation] = _ask_score(question, lang)
    return answers


def _gather_needs() -> List[NeedKey]:
    needs: List[NeedKey] = []
    for question in QUESTION_BANK:
        if question.need not in needs:
            needs.append(question.need)
    return needs


def _print_report(report_text: str) -> None:
    print("\n" + "=" * 60)
    print(report_text)
    print("=" * 60 + "\n")


def _run_companion(report, lang: str) -> None:
    context = AssistantContext(report=report, language=lang)
    print(translate(lang, "companion_intro"))
    while True:
        question = _prompt("Вопрос ассистенту (Enter чтобы выйти) > ").strip()
        if not question:
            break
        response = build_response(context, question)
        if response["type"] == "bad_language":
            print(translate(lang, "companion_bad_language"))
            continue
        if response["type"] == "out_of_scope":
            print(translate(lang, "companion_out_of_scope"))
            continue
        print(translate(lang, "companion_ack"))
        low = need_title(response["low_need"], lang)
        high = need_title(response["high_need"], lang)
        print(f"🔧 Зона роста: {low}")
        print(response["tip"])
        print(f"🎉 Суперсила: {high}")
        print(response["celebrate"])
        snippet = response.get("knowledge_snippet")
        if snippet:
            print("\n📚 Из базы знаний:\n" + snippet + "...")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the compatibility test without Telegram")
    parser.add_argument(
        "--language",
        "-l",
        default="ru",
        help=f"Язык интерфейса ({_list_languages()})",
    )
    parser.add_argument(
        "--skip-companion",
        action="store_true",
        help="Не запускать чат с ассистентом после отчёта",
    )
    args = parser.parse_args()

    lang = _resolve_language(args.language)
    print(f"Выбран язык: {lang}")

    name_a = _prompt_name("Участник A", lang)
    age_a = _prompt_age(name_a, lang)
    answers_a = _collect_answers(name_a, lang, age_a)
    profile_a = ParticipantProfile(name=name_a, answers=answers_a)

    print("\nТеперь второй участник.")
    name_b = _prompt_name("Участник B", lang)
    age_b = _prompt_age(name_b, lang)
    answers_b = _collect_answers(name_b, lang, age_b)
    profile_b = ParticipantProfile(name=name_b, answers=answers_b)

    needs = _gather_needs()
    report = build_report(profile_a, profile_b, needs)
    report_text = render_report(report, lang)
    _print_report(report_text)

    if not args.skip_companion:
        _run_companion(report, lang)


if __name__ == "__main__":
    main()
