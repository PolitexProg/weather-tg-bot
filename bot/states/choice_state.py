from aiogram.fsm.state import State, StatesGroup


class ChoiceState(StatesGroup):
    choosing_city = State()
    choosing_country = State()
    choosing_source = State()
