from aiogram.fsm.state import State, StatesGroup


class ProfileState(StatesGroup):
    """FSM states for user profile management."""
    hobbies = State()
    city = State()
    name = State()
    age = State()
