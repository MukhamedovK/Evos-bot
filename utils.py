from aiogram.types import Message
import datetime

from lang_context import context

num_stickers = {
        '0':"0️⃣",
        '1':"1️⃣",
        '2':"2️⃣",
        '3':"3️⃣",
        '4':"4️⃣",
        '5':"5️⃣",
        '6':"6️⃣",
        '7':"7️⃣",
        '8':"8️⃣",
        '9':"9️⃣",
    }

async def set_lang(message: Message):
    from database import get_user_data
    _, lang = await get_user_data(message.from_user.id)
    for i in lang:
        pass
    return i

async def get_cost_size(message: Message):
    from database import get_food_data
    from utils import set_lang

    lang = await set_lang(message)
    result = await get_food_data(message.from_user.id)
    data = result.items()

    food_name = []
    uz_food_name = []
    values = []
    for item in data:
        name = item[0]
        cost = item[1].split(";")

        values.append(cost)
        food_name.append(name)
        if lang == 'uz':
            uz_name = context['uz']['fast_food_name_btn'][name]
            uz_food_name.append(uz_name)


    results = []
    for k in values:
        new = []
        for st in k:
            em = st.split(':')
            new.append(em)
        results.append(new)


    pc = []
    size = []
    cost = []
    lens = []
    for i in results:
        for j in i:
            if len(j) == 3:
                pc.append(int(j[0]))
                size.append(j[1])
                cost.append(int(j[-1]))
            else:
                pc.append(int(j[0]))
                size.append("")
                cost.append(int(j[-1]))
        lens.append(len(i))

    a = 0
    new_food_name = []
    food_name_size = []
    food_name_callback = []
    
    if lang == 'ru':
        for _, names in enumerate(food_name):
            if a < len(lens):
                for _ in range(lens[a]):
                    new_food_name.append(names)
                    food_name_size.append(names)
                    food_name_callback.append(names)
                a+=1
    elif lang == 'uz':
        for _, names in enumerate(uz_food_name):
            if a < len(lens):
                for _ in range(lens[a]):
                    new_food_name.append(names)
                    food_name_size.append(names)
                a+=1

        b = 0
        for _, names in enumerate(food_name):
            if b < len(lens):
                for _ in range(lens[b]):
                    food_name_callback.append(names)
                b+=1
                

    for up in range(0, len(new_food_name)):
        num = ""
        for pcs in list(str(pc[up])):
            num += num_stickers[pcs]

        new_food_name[up] = f"{num}✖️{new_food_name[up]} {size[up]}"
        food_name_size[up] = f"{food_name_size[up]} {size[up]}"
        food_name_callback[up] = f"{food_name_callback[up]} {size[up]}"

        cost[up] = cost[up]*pc[up]

    all_cost = 0
    for costs in cost:
        all_cost+=costs

    return all_cost, new_food_name, food_name_size, food_name_callback


def cost_formatter(cost):
    format_cost = f'{cost:,}'.replace(',', ' ')
    
    return format_cost


def delivery_time():
    times = []
    full_time = datetime.datetime.now()
    minute = full_time.minute

    if minute <= 30:
        if full_time.minute % 30 != 0:
            minutes = 30 - minute
        else: minutes = 0
    elif minute > 30:
        if full_time.minute % 60 != 0:
            minutes = 60 - minute
        else: minutes = 0

    h1_later = full_time + datetime.timedelta(hours=1, minutes=minutes)
    default_time = h1_later.strftime("%H:%M")

    times.append(h1_later.strftime("%H:%M"))
    while h1_later.strftime("%H") != '02':
        h1_later = h1_later + datetime.timedelta(minutes=30)
        time = h1_later.strftime("%H:%M")
        times.append(time)
        
    return times, default_time


def db_data_converter(data):
    values = []
    f_data = data.split(";")
    values.append(f_data)
    result = []
    for k in values:
        for st in k:
            em = st.split(':')
            result.append(em)

    return result


def db_symbol_converter(food_name):
    if " " in food_name:
        food_name = "_".join(food_name.split(" "))
    else: food_name = food_name

    if "-" in food_name:
        food_name = "__".join(food_name.split("-"))
    else: food_name = food_name

    if "," in food_name:
        food_name = "___".join(food_name.split(","))
    else: food_name = food_name
    
    return food_name


async def time_btn_menu(message: Message):
    from keyboard import time_btn
    from utils import set_lang

    lang = await set_lang(message)

    time, _ = delivery_time()
    in_menu = 4

    floor_btn = []
    for i in range(0, len(time), in_menu):
        floor_btn.append(time[i:i+in_menu])

    time_page = []
    for btns in floor_btn:
        menu = await time_btn(btns, lang)
        time_page.append(menu)

    return time_page


