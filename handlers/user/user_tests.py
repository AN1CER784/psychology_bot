from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_content_message_by_title_and_id, orm_get_amount_of_messages_by_title, \
    orm_get_first_message_by_title, orm_get_ending_of_test
from kbds.user_kb import generate_after_chapter_kb, generate_kb_for_test, get_callback_btns

user_test = Router()


@user_test.callback_query(F.data.startswith("test_"))
async def start_test(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    Переход к первому сообщению теста

    :param session:
    :param callback:
    :param state:
    :return:
    """
    await callback.answer()
    test_number = int(callback.data.split("_")[-1])
    first_message = await orm_get_first_message_by_title(session, f"test_{test_number}")
    init_message = await callback.message.edit_text(first_message.text)
    await state.update_data(init_message_id=init_message.message_id, init_message_chat_id=init_message.chat.id)
    await all_questions(callback=callback, state=state, session=session, first_init=f"answertest_{test_number}_question_1-0")


@user_test.callback_query(F.data.startswith("answertest_"))
async def all_questions(callback: CallbackQuery, state: FSMContext, session: AsyncSession, first_init=None):
    """
    Основная работа теста

    :param session:
    :param first_init:
    :param callback:
    :param state:
    :return:
    """
    await callback.answer()
    process_data = first_init.split("-") if first_init else callback.data.split("-")
    test_num = int(process_data[0].split("_")[1])
    question_index = int(process_data[0].split("_")[3])
    score = int(process_data[1])
    messages_amount = await orm_get_amount_of_messages_by_title(session, f"test_{test_num}")
    messages_amount = messages_amount - 4 if test_num == 1 else messages_amount - 5
    first_message = await orm_get_first_message_by_title(session, f"test_{test_num}")
    message = await orm_get_content_message_by_title_and_id(session, f"test_{test_num}", first_message.id + question_index)
    if first_init:
        await callback.message.answer(f"Вопрос {question_index} / {messages_amount} " + message.text,
                                      reply_markup=await generate_kb_for_test(test_num,question_index,
                                                                              score))
    elif question_index != messages_amount + 1:
        await callback.message.edit_text(f"Вопрос {question_index} / {messages_amount} " + message.text,
                                         reply_markup=await generate_kb_for_test(test_num, question_index,
                                                                                 score))
    else:
        await callback.message.edit_reply_markup(
            reply_markup=get_callback_btns(btns={"Завершить тестирование": f"end_testing-{test_num}"}))
    await state.update_data(score=score)


@user_test.callback_query(F.data.startswith("end_testing"))
async def end_test(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    Завершение теста

    :param session:
    :param callback:
    :param state:
    :return:
    """
    await callback.answer()
    data = await state.get_data()
    init_message_id, init_message_chat_id = data.get('init_message_id'), data.get('init_message_chat_id')
    await callback.message.delete()
    await callback.bot.delete_message(chat_id=init_message_chat_id, message_id=init_message_id)
    test_num = int(callback.data.split("-")[-1])
    score = data.get('score')
    ending_text = await orm_get_ending_of_test(session, test_num)
    message_text = ending_text[0].text + f"\nВаш результат: {score} баллов"
    if test_num == 1:
        if score >= 6:
            message_text += ending_text[1].text
        else:
            message_text += ending_text[2].text
    elif test_num == 2:
        if score <= 2:
            message_text += ending_text[1].text
        elif score < 6:
            message_text += ending_text[2].text
        else:
            message_text += ending_text[3].text
    await callback.message.answer(message_text)
    await callback.message.answer(
        "Если вы желаете  разобраться в ваших отношениях, обращайтесь к профессиональному семейному психологу",
        reply_markup=await generate_after_chapter_kb(test_num))

