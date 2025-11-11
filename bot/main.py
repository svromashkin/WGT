"""Telegram bot entry point."""
from __future__ import annotations

import asyncio
import logging
from typing import Dict, List

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from .assistant import AssistantContext, build_response
from .compatibility import CompatibilityReport, ParticipantProfile, build_report
from .config import Config
from .localization import available_languages, translate
from .questions import QUESTION_BANK, NeedKey, iter_questions
from .reporting import render_report
from .storage import SessionRepository


class Onboarding(StatesGroup):
    choosing_language = State()
    choosing_path = State()
    choosing_age = State()
    confirming = State()
    entering_name = State()
    entering_code = State()


class TestFlow(StatesGroup):
    answering = State()


class CompanionFlow(StatesGroup):
    chatting = State()


class FeedbackFlow(StatesGroup):
    collecting = State()


def _language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for pack in available_languages().values():
        builder.button(text=pack.title, callback_data=f"lang:{pack.code}")
    builder.adjust(2)
    return builder.as_markup()


def _start_keyboard(lang: str) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=translate(lang, "start_new"))
    builder.button(text=translate(lang, "join_existing"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def _age_keyboard(lang: str) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=translate(lang, "age_minor"))
    builder.button(text=translate(lang, "age_adult"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def _consent_keyboard(lang: str) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=translate(lang, "consent_yes"))
    builder.button(text=translate(lang, "consent_no"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def _score_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for score in range(1, 6):
        builder.button(text=str(score), callback_data=f"score:{score}")
    builder.adjust(5)
    return builder.as_markup()


def _partner_wait_keyboard(lang: str) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=translate(lang, "start_new"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


async def _send_question(message: Message, lang: str, question_id: str, age_group: str) -> None:
    question = next(q for q in QUESTION_BANK if q.id == question_id)
    text = "\n\n".join(
        (
            question.text.get(lang, question.text["en"]),
            translate(lang, "scale_hint"),
            question.example.get(lang, question.example["en"]),
        )
    )
    await message.answer(text, reply_markup=_score_keyboard())


async def _complete_session(
    bot: Bot,
    repo: SessionRepository,
    active_reports: Dict[str, CompatibilityReport],
    session_id: str,
    lang: str,
) -> None:
    participants = repo.get_participants(session_id)
    if 1 not in participants or 2 not in participants:
        return
    answers = repo.load_answers(session_id)
    needs: List[NeedKey] = []
    for q in QUESTION_BANK:
        if q.need not in needs:
            needs.append(q.need)
    profile_a = ParticipantProfile(
        name=participants[1].name,
        answers=answers.get(1, {}),
    )
    profile_b = ParticipantProfile(
        name=participants[2].name,
        answers=answers.get(2, {}),
    )
    report = build_report(profile_a, profile_b, needs)
    text = render_report(report, lang)
    await bot.send_message(participants[1].telegram_id, text)
    await bot.send_message(participants[2].telegram_id, text)
    active_reports[session_id] = report


def _map_age_selection(lang: str, text: str) -> str:
    if text == translate(lang, "age_minor"):
        return "minor"
    if text == translate(lang, "age_adult"):
        return "adult"
    return "adult"


def _map_path_selection(lang: str, text: str) -> str:
    if text == translate(lang, "start_new"):
        return "start"
    if text == translate(lang, "join_existing"):
        return "join"
    return "start"


def build_router(repo: SessionRepository, active_reports: Dict[str, CompatibilityReport]) -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    bot_router = dp

    @bot_router.message(CommandStart())
    async def handle_start(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer("Choose language / Выбери язык", reply_markup=_language_keyboard())
        await state.set_state(Onboarding.choosing_language)

    @bot_router.callback_query(Onboarding.choosing_language, F.data.startswith("lang:"))
    async def handle_language(callback: CallbackQuery, state: FSMContext) -> None:
        lang = callback.data.split(":", 1)[1]
        await state.update_data(language=lang)
        await callback.message.answer(translate(lang, "start_new_or_join"), reply_markup=_start_keyboard(lang))
        await callback.answer()
        await state.set_state(Onboarding.choosing_path)

    @bot_router.message(Onboarding.choosing_path)
    async def handle_path(message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        lang = data.get("language", "ru")
        choice = _map_path_selection(lang, message.text or "")
        if choice == "start":
            await message.answer(translate(lang, "age_prompt"), reply_markup=_age_keyboard(lang))
            await state.set_state(Onboarding.choosing_age)
        else:
            await message.answer(translate(lang, "request_partner_code"), reply_markup=ReplyKeyboardRemove())
            await state.set_state(Onboarding.entering_code)

    @bot_router.message(Onboarding.choosing_age)
    async def handle_age(message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        lang = data.get("language", "ru")
        age_group = _map_age_selection(lang, message.text or "")
        await state.update_data(age_group=age_group)
        await message.answer(translate(lang, "consent"), reply_markup=_consent_keyboard(lang))
        await state.set_state(Onboarding.confirming)

    @bot_router.message(Onboarding.confirming)
    async def handle_consent(message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        lang = data.get("language", "ru")
        if message.text != translate(lang, "consent_yes"):
            await message.answer(translate(lang, "consent_no"))
            await state.clear()
            return
        await message.answer(translate(lang, "ask_name"), reply_markup=ReplyKeyboardRemove())
        await state.set_state(Onboarding.entering_name)

    @bot_router.message(Onboarding.entering_name)
    async def handle_name(message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        lang = data.get("language", "ru")
        name = message.text.strip() if message.text else "Гость"
        age_group = data.get("age_group", "adult")
        if data.get("joining"):
            code = data.get("code")
            session_id = repo.join_session(code, message.from_user.id, name)
            if not session_id:
                await message.answer(translate(lang, "invalid_code"))
                await state.clear()
                return
            await state.update_data(participant_index=2, session_id=session_id, name=name, joining=False)
        else:
            session_id, code = repo.start_session(lang, age_group, message.from_user.id, name)
            await state.update_data(participant_index=1, session_id=session_id, name=name, code=code, joining=False)

        questions = [q.id for q in iter_questions(age_group, lang)]
        await state.update_data(question_list=questions, question_index=0)
        await message.answer(translate(lang, "intro"))
        await _send_question(message, lang, questions[0], age_group)
        await state.set_state(TestFlow.answering)

    @bot_router.message(Onboarding.entering_code)
    async def handle_partner_code(message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        lang = data.get("language", "ru")
        code = (message.text or "").strip()
        session = repo.get_session_by_code(code)
        if not session:
            await message.answer(translate(lang, "invalid_code"))
            return
        session_lang = session["language"]
        age_group = session["age_group"]
        await state.update_data(
            session_id=session["id"],
            language=session_lang,
            age_group=age_group,
            code=code,
            joining=True,
        )
        await message.answer(translate(session_lang, "ask_name"))
        await state.set_state(Onboarding.entering_name)

    @bot_router.callback_query(TestFlow.answering, F.data.startswith("score:"))
    async def handle_score(callback: CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        lang = data.get("language", "ru")
        age_group = data.get("age_group", "adult")
        session_id = data.get("session_id")
        participant_index = data.get("participant_index", 1)
        question_list: List[str] = data.get("question_list", [])
        index = data.get("question_index", 0)
        score = int(callback.data.split(":", 1)[1])
        question = next(q for q in QUESTION_BANK if q.id == question_list[index])
        repo.store_answer(session_id, participant_index, question.need, question.orientation, score)
        index += 1
        if index >= len(question_list):
            repo.mark_finished(session_id, participant_index)
            await state.update_data(question_index=index)
            await callback.answer()
            if participant_index == 1:
                code = data.get("code") or repo.get_code(session_id)
                await callback.message.answer(
                    translate(lang, "thanks_first", code=code), reply_markup=_partner_wait_keyboard(lang)
                )
                await state.clear()
            else:
                await callback.message.answer(translate(lang, "partner_joined"))
                await state.clear()
                if repo.is_ready_for_report(session_id):
                    await _complete_session(callback.bot, repo, active_reports, session_id, lang)
            return
        await state.update_data(question_index=index)
        await callback.answer()
        await _send_question(callback.message, lang, question_list[index], age_group)

    @bot_router.message(TestFlow.answering)
    async def block_text(message: Message) -> None:
        await message.answer("Please use the buttons to answer.")

    @bot_router.message(Command("feedback"))
    async def feedback_command(message: Message, state: FSMContext) -> None:
        session = repo.get_session_by_participant(message.from_user.id)
        if not session:
            await message.answer("Complete a session first to leave feedback.")
            return
        await state.set_state(FeedbackFlow.collecting)
        await state.update_data(session_id=session["id"], language=session["language"])
        await message.answer(translate(session["language"], "feedback_prompt"))

    @bot_router.message(FeedbackFlow.collecting)
    async def handle_feedback(message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        session_id = data.get("session_id")
        lang = data.get("language", "ru")
        repo.store_feedback(session_id, message.text or "")
        await message.answer(translate(lang, "feedback_thanks"))
        await state.clear()

    @bot_router.message(Command("companion"))
    async def companion_entry(message: Message, state: FSMContext) -> None:
        session = repo.get_session_by_participant(message.from_user.id)
        if not session or session["id"] not in active_reports:
            await message.answer(translate("ru", "companion_no_session"))
            return
        await state.set_state(CompanionFlow.chatting)
        await state.update_data(session_id=session["id"], language=session["language"])
        await message.answer(translate(session["language"], "companion_intro"))

    @bot_router.message(CompanionFlow.chatting)
    async def companion_chat(message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        session_id = data.get("session_id")
        lang = data.get("language", "ru")
        report = active_reports.get(session_id)
        if not report:
            await message.answer(translate(lang, "companion_no_session"))
            await state.clear()
            return
        result = build_response(AssistantContext(report=report, language=lang), message.text or "")
        if result["type"] == "bad_language":
            await message.answer(translate(lang, "companion_bad_language"))
            return
        if result["type"] == "out_of_scope":
            await message.answer(translate(lang, "companion_out_of_scope"))
            return
        from .questions import need_title

        response_text = "\n".join(
            (
                translate(lang, "companion_ack"),
                f"• {need_title(result['low_need'], lang)}: {result['tip']}",
                f"• {need_title(result['high_need'], lang)}: {result['celebrate']}",
                "",
                result["knowledge_snippet"],
            )
        )
        await message.answer(response_text)

    return dp


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    config = Config.load()
    repo = SessionRepository(config.storage_path)
    active_reports: Dict[str, CompatibilityReport] = {}
    dp = build_router(repo, active_reports)
    bot = Bot(config.bot_token, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
