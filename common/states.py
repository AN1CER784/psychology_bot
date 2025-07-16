from aiogram.fsm.state import StatesGroup, State


class Activities(StatesGroup):
    topic_name = State()
    topic_description = State()
    test_name = State()
    test_description = State()
    test_high_score_message = State()
    test_medium_score_message = State()
    test_low_score_message = State()


class TopicFlow(StatesGroup):
    choosing_topic = State()
    input_title = State()
    input_content = State()


class TestFlow(StatesGroup):
    choosing_test = State()
    input_question = State()