from aiogram.fsm.state import State, StatesGroup


class AdminMenuStates(StatesGroup):
    waiting_add_user_data = State()
    waiting_add_key_name_data = State()
    waiting_add_key_secret_data = State()
    waiting_delete_user_data = State()
    waiting_delete_key_data = State()
    waiting_view_user_data = State()
    waiting_view_key_data = State()
