from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Test
from handlers.user.user_watch_activity import end_activity, start_activity
from kbds.user_kb import generate_kb_for_test

user_router_test = Router()


@user_router_test.callback_query(F.data == "start_test")
async def test_start(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    Start of test
    """
    activity_dict = await start_activity(callback, state, session, Test)
    message = f"Сейчас будет рассмотрен материал на тему {activity_dict['title']}\n\n{activity_dict['description']}"
    await callback.message.edit_text(
        message
    )
    callback_data = "answertest_question_0_back"
    await test_next(callback, state, session, callback_data)



@user_router_test.callback_query(F.data.startswith("answertest_question_"))
async def test_next(callback: CallbackQuery, state: FSMContext, session: AsyncSession, callback_data: str | None = None):
    await callback.answer()

    if not callback_data:
        callback_data = callback.data
    data = await state.get_data()
    messages = data.get("activity_items")
    answers = data.get("answers", {})
    parts = callback_data.split("_")
    current_index = int(parts[2])
    answer = parts[-1]

    if answer == "back":
        if current_index == -1:
            await callback.message.delete()
            await end_activity(callback, state, session)
            return
        if current_index in answers:
            del answers[current_index]
        await state.update_data(answers=answers)
        test_content = messages[current_index]
        message_data = f"<b>{test_content.question}</b>", await generate_kb_for_test(current_index)
        if current_index == 0:
            await callback.message.answer(message_data[0], reply_markup=message_data[1])
        else:
            await callback.message.edit_text(message_data[0], reply_markup=message_data[1])

        return
    if answer == "yes":
        answers[current_index] = 1
    elif answer == "no":
        answers[current_index] = 0

    await state.update_data(answers=answers)
    if current_index == len(messages):
        scores = sum(answers.values())
        complete_percentage = (scores / len(messages)) * 100
        await end_test(callback, state, session, complete_percentage)
    else:
        next_question = messages[current_index]
        await callback.message.edit_text(
            f"<b>{next_question.question}</b>",
            reply_markup=await generate_kb_for_test(current_index)
        )


async def end_test(callback: CallbackQuery, state: FSMContext, session: AsyncSession, complete_percentage: float):
    data = await state.get_data()
    activity = data.get("activity")
    if complete_percentage >= 80:
        await callback.message.edit_text(
            f"Вы прошли тест на тему {activity.title} с результатом {complete_percentage}%\n\n{activity.high_score_message}",
            reply_markup=None
        )
    elif complete_percentage >= 50:
        await callback.message.edit_text(
            f"Вы прошли тест на тему {activity.title} с результатом {complete_percentage}%\n\n{activity.medium_score_message}",
            reply_markup=None
        )
    else:
        await callback.message.edit_text(
            f"Вы прошли тест на тему {activity.title} с результатом {complete_percentage}%\n\n{activity.low_score_message}",
            reply_markup=None
        )
    await end_activity(callback, state, session)
