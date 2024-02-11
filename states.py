from aiogram.dispatcher.filters.state import StatesGroup, State


class LocateContact(StatesGroup):
    location = State()
    phone_number = State()
    feedback = State()
    locate_choice = State()
    choice_lang = State()

class OrderList(StatesGroup):
    fast_food_category = State()
    fast_food = State()
    go_pc_btn = State()
    delivery = State()
    pay = State()
    pay_confirm = State()

    in_lavash = State()
    in_trindvich = State()
    in_shaurma = State()
    in_burger = State()
    in_sub = State()
    in_potato = State()
    in_hot_dog = State()
    in_snake = State()
    in_garnir = State()
    in_sous = State()
    in_set = State()
    in_desert = State()
    in_hot_drink = State()
    in_cold_drink = State()
    in_combo = State()

class Button(StatesGroup):
    next_btn = State()
    prev_btn  = State()
