from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from database import get_user_data
from utils import get_cost_size
from lang_context import context


async def menu_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True)

    btn.row(context[lang]['menu'])
    btn.row(context[lang]['my_order']['btn'])

    btn.add(
        KeyboardButton(context[lang]['feedback']['btn']),
        KeyboardButton(context[lang]['settings']['btn']),
    )
    return btn


async def locate_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True)
    btn.row(context[lang]['locate']['address'])
    btn.add(
        KeyboardButton(context[lang]['locate']['btn'], request_location=True),
        KeyboardButton(context[lang]['back']),
    )
    return btn


async def my_locate_btn(message: Message, lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True)
    location, _ = await get_user_data(message.from_user.id)
    locate = []
    for i in location:
        locate = i.split(";")
        
    for k in locate:
        btn.row(f"{k}")
    btn.row(context[lang]['back'])

    return btn


async def locate_yes_no_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True)
    btn.add(
        KeyboardButton(context[lang]['yes']),
        KeyboardButton(context[lang]['no'])
    )
    btn.row(context[lang]['back'])

    return btn


async def contact_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn.add(
        KeyboardButton(context[lang]['my_number'], request_contact=True),
        KeyboardButton(context[lang]['back']),
    )
    return btn


async def back_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True)
    btn.row(context[lang]['back'])

    return btn


async def settings_btn(message: Message, lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn.row(context[lang]['settings']['set_lang_btn'])
    btn.row(context[lang]['back'])

    return btn


async def language_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True)

    for i in context['languages'].values():
        btn.insert(i)

    btn.row(context[lang]['back'])

    return btn


async def fast_food_category_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    for i in context[lang]['fast_food_category'].values():
        btn.insert(i)
 
    btn.add(
        KeyboardButton(context[lang]['basket']),
        KeyboardButton(context[lang]['back'])
    )

    return btn


async def lavash_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    for i in context[lang]['fast_food_name']['lavash'].values():
        btn.insert(i)

    btn.row(context[lang]['back'])

    return btn


async def trindvich_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    for i in context[lang]['fast_food_name']['trindvich'].values():
        btn.insert(i)

    btn.row(context[lang]['back'])

    return btn


async def shaurma_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    for i in context[lang]['fast_food_name']['shaurma'].values():
        btn.insert(i)
 
    btn.row(context[lang]['back'])

    return btn


async def burger_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    for i in context[lang]['fast_food_name']['burger'].values():
        btn.insert(i)
 
    btn.row(context[lang]['back'])

    return btn


async def sub_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    for i in context[lang]['fast_food_name']['sub'].values():
        btn.insert(i)
 
    btn.row(context[lang]['back'])

    return btn


async def potato_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    for i in context[lang]['fast_food_name']['potato'].values():
        btn.insert(i)
 
    btn.row(context[lang]['back'])

    return btn


async def xot_dog_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    for i in context[lang]['fast_food_name']['xot-dog'].values():
        btn.insert(i)
 
    btn.row(context[lang]['back'])

    return btn


async def snake_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
   
    for i in context[lang]['fast_food_name']['snake'].values():
        btn.insert(i)
 
    btn.row(context[lang]['back'])

    return btn


async def garnir_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    for i in context[lang]['fast_food_name']['garnir'].values():
        btn.insert(i)
 
    btn.row(context[lang]['back'])

    return btn


async def sous_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    for i in context[lang]['fast_food_name']['sous'].values():
        btn.insert(i)
 
    btn.row(context[lang]['back'])

    return btn


async def set_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    for i in context[lang]['fast_food_name']['nabor'].values():
        btn.insert(i)
 
    btn.row(context[lang]['back'])

    return btn


async def desert_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    for i in context[lang]['fast_food_name']['desert'].values():
        btn.insert(i)
 
    btn.row(context[lang]['back'])

    return btn


async def hot_drink_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    for i in context[lang]['fast_food_name']['hot-drink'].values():
        btn.insert(i)
 
    btn.row(context[lang]['back'])

    return btn


async def cold_drink_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    for i in context[lang]['fast_food_name']['cold-drink'].values():
        btn.insert(i)
 
    btn.row(context[lang]['back'])

    return btn


async def combo_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    for i in context[lang]['fast_food_name']['combo'].values():
        btn.insert(i)
 
    btn.row(context[lang]['back'])

    return btn


async def food_size1_btn(lang):
    uzs = context[lang]['my_order']['sum']
    mini = context[lang]['food_size']['mini']
    big = context[lang]['food_size']['big']
    
    btn = InlineKeyboardMarkup(resize_keyboard=True)
    btn.add(
        InlineKeyboardButton(f"{mini.title()} 21 000 {uzs}", callback_data=f"food:{mini}:21000"),
        InlineKeyboardButton(f"{big.title()} 26 000 {uzs}", callback_data=f"food:{big}:26000")
    )
    return btn


async def food_size2_btn(lang):
    uzs = context[lang]['my_order']['sum']
    mini = context[lang]['food_size']['mini']
    big = context[lang]['food_size']['big']
    
    btn = InlineKeyboardMarkup(resize_keyboard=True)
    btn.add(
        InlineKeyboardButton(f"{mini.title()} 23 000 {uzs}", callback_data=f"food:{mini}:23000"),
        InlineKeyboardButton(f"{big.title()} 28 000 {uzs}", callback_data=f"food:{big}:28000")
    )
    return btn


async def food_size3_btn(lang):
    uzs = context[lang]['my_order']['sum']
    mini = context[lang]['food_size']['mini']
    big = context[lang]['food_size']['big']
    
    btn = InlineKeyboardMarkup(resize_keyboard=True)
    btn.add(
        InlineKeyboardButton(f"{mini.title()} 26 000 {uzs}", callback_data=f"food:{mini}:26000"),
        InlineKeyboardButton(f"{big.title()} 31 000 {uzs}", callback_data=f"food:{big}:31000")
    )
    return btn


async def food_size4_btn(lang):
    uzs = context[lang]['my_order']['sum']
    mini = context[lang]['food_size']['mini']
    big = context[lang]['food_size']['big']
    
    btn = InlineKeyboardMarkup(resize_keyboard=True)
    btn.add(
        InlineKeyboardButton(f"{mini.title()} 24 000 {uzs}", callback_data=f"food:{mini}:24000"),
        InlineKeyboardButton(f"{big.title()} 2  9 000 {uzs}", callback_data=f"food:{big}:29000")
    )
    return btn


async def food_size5_btn(lang):
    uzs = context[lang]['my_order']['sum']
    mini = context[lang]['food_size']['mini']
    big = context[lang]['food_size']['big']
    
    btn = InlineKeyboardMarkup(resize_keyboard=True)
    btn.add(
        InlineKeyboardButton(f"{mini.title()} 22 000 {uzs}", callback_data=f"food:{mini}:22000"),
        InlineKeyboardButton(f"{big.title()} 26 000 {uzs}", callback_data=f"food:{big}:26000")
    )
    return btn


async def food_size6_btn(lang):
    uzs = context[lang]['my_order']['sum']
    mini = context[lang]['food_size']['mini']
    big = context[lang]['food_size']['big']
    
    btn = InlineKeyboardMarkup(resize_keyboard=True)
    btn.add(
        InlineKeyboardButton(f"{mini.title()} 21 000 {uzs}", callback_data=f"food:{mini}:21000"),
        InlineKeyboardButton(f"{big.title()} 24 000 {uzs}", callback_data=f"food:{big}:24000")
    )
    return btn


async def back_basket_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn.add(
        KeyboardButton(context[lang]['basket']),
        KeyboardButton(context[lang]['back'])
    )
    return btn


async def food_pc_btn(pc, lang):
    btn = InlineKeyboardMarkup()
    btn.add(
        InlineKeyboardButton("-", callback_data="prev"),
        InlineKeyboardButton(f"{pc}", callback_data="1"),
        InlineKeyboardButton("+", callback_data="next")
    )
    btn.row(InlineKeyboardButton(context[lang]['add_basket'], callback_data="add_basket"))

    return btn


async def basket_btn(message: Message, lang):
    btn = InlineKeyboardMarkup(row_width=2)
    _, _, food_name, for_callback = await get_cost_size(message)
    btn.add(
        InlineKeyboardButton(context[lang]['back'], callback_data="back"),
    )

    for i in context[lang]['basket_inline'].items():
        btn.insert(InlineKeyboardButton(i[-1], callback_data=i[0]))

    for f_name, f_callback in zip(food_name, for_callback):
        btn.row(InlineKeyboardButton(f"❌{f_name}", callback_data=f"del_food:{f_callback}"))

    return btn


async def pay_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    for i in context[lang]['pay_type'].values():
        btn.row(i)

    btn.row(context[lang]['back'])
    return btn


async def ok_no_delivery_btn(lang):
    btn = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn.add(
        KeyboardButton(context[lang]['confirm']),
        KeyboardButton(context[lang]['cancel'])
    )
    return btn


async def time_btn(btns, lang):
    btn = InlineKeyboardMarkup(row_width=2)
    btn.add(
        InlineKeyboardButton(context[lang]['back'], callback_data="tback"),
        InlineKeyboardButton(context[lang]['next'], callback_data=f"tnext")
    )

    for t in btns:
        btn.insert(InlineKeyboardButton(f"{t}", callback_data=f"times;{t}"))

    return btn

    


