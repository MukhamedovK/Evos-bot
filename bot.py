import logging

from aiogram import Dispatcher, Bot, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InputFile

from geopy.geocoders import Nominatim

from config import *
from keyboard import *
from states import *
from database import *
from utils import *
from lang_context import context


logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode='html')
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await insert_user(message.from_user.id)
    lang = await set_lang(message)
    btn = await menu_btn(lang)
    await message.answer(context[lang]['choose1'], reply_markup=btn)


@dp.message_handler()
async def text_handler(message: types.Message):
    lang = await set_lang(message)
    user_id = message.from_user.id
    text = message.text
    order = await get_order_data(user_id)
    feedback = await get_feedback_data(user_id)
    
    if text == context[lang]['menu']:
        btn = await locate_btn(lang)
        await message.answer(context[lang]['locate']['send_locate'], reply_markup=btn)
        await LocateContact.location.set()


    elif text == context[lang]['my_order']['btn']:
        if not order:
            await message.answer(context[lang]['my_order']['not'])
        else:
# Я это делал по своему т.к. для того чтобы сделать как в оригинале надо было заказать что-то, но я ничего не заказывал. Извиняюсь
            data = await get_order_data(message.from_user.id)
            for i in data:
                food = i[1]
                locate = i[2]
                pay_type = i[3]
                time = i[4]
                cost = i[-1]
                await message.answer(f"<b>{context[lang]['my_order']['order']} №{data.index(i)+1}: \n</b>"
                                f"{context[lang]['my_order']['address']}: {locate}\n\n"
                                f"{food}\n\n"
                                f"{context[lang]['my_order']['time']} {time}\n"
                                f"{context[lang]['my_order']['pay']} {pay_type}\n\n"
                                f"<b>{context[lang]['my_order']['total']} </b>{cost} {context[lang]['my_order']['sum']}")


    elif text == context[lang]['feedback']['btn']:
        if not feedback:
            btn = await contact_btn(lang)
            await message.answer(context[lang]['feedback']['send_contact'], reply_markup=btn)
            await LocateContact.phone_number.set()
        else:
            btn = await back_btn(lang)
            await message.answer(context[lang]['feedback']['send_feedback'], reply_markup=btn)
            await LocateContact.feedback.set()
            

    elif text == context[lang]['settings']['btn']:
        btn = await settings_btn(message, lang)
        await message.answer(context[lang]['choose2'], reply_markup=btn)

    
    elif text == context[lang]['settings']['set_lang_btn']:
        btn = await language_btn(lang)
        await message.answer(context[lang]['settings']['choose_lang'], reply_markup=btn)
        await LocateContact.choice_lang.set()


    elif text == context[lang]['back']:
        await start_handler(message)


@dp.message_handler(state=LocateContact.choice_lang)
async def back_lang_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    if text == context['languages']['ru']:
        await update_user_lang(user_id, 'ru')
        lang = await set_lang(message)
        btn = await settings_btn(message, lang)
        await message.answer(context['set_lang']['ru'], reply_markup=btn)

    elif text == context['languages']['uz']:
        await update_user_lang(user_id, 'uz')
        lang = await set_lang(message)
        btn = await settings_btn(message, lang)
        await message.answer(context['set_lang']['uz'], reply_markup=btn)

    lang = await set_lang(message)
    btn = await settings_btn(message, lang)
    if text == context[lang]['back']:
        await message.answer(context[lang]['choose2'], reply_markup=btn)
    await state.finish()
        

@dp.message_handler(state=LocateContact.phone_number, content_types=['contact', 'text'])
async def get_contact_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    btn = await back_btn(lang)
    if message.contact:
        contact = message.contact.phone_number
        await state.update_data(contact=str(contact))
        await message.answer(context[lang]['feedback']['send_feedback'], reply_markup=btn)
        await LocateContact.feedback.set()
    elif message.text:
        if message.text == context[lang]['back']:
            await start_handler(message)
        await state.finish()


@dp.message_handler(state=LocateContact.feedback, content_types=['text'])
async def get_feedback_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    btn = await menu_btn(lang)
    user_id = message.from_user.id
    feedback = message.text
    data = await state.get_data()
    if message.text != context[lang]['back']:
        if data:
            await insert_feedback(user_id, data['contact'], feedback)
        else:
            feedback_list = await get_feedback_data(user_id)
            contact = feedback_list[0][1]
            await insert_feedback(user_id, contact, feedback)
        await message.answer(context[lang]['feedback']['thanks'], reply_markup=btn)
        await state.finish()
    else:
        await start_handler(message)
        await state.finish()


@dp.message_handler(state=LocateContact.location, content_types=['location', 'text'])
async def get_locate_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    if message.location:
        btn = await locate_yes_no_btn(lang)
        nominatim = Nominatim(user_agent='user')
        locate = message.location
        location = nominatim.reverse(query=f'{locate.latitude}, {locate.longitude}', language='ru')
        await message.answer(f"{context[lang]['locate']['confirm1']} {location} {context[lang]['locate']['confirm2']}", reply_markup=btn)
        await state.update_data(address=str(location))
        await LocateContact.locate_choice.set()

    elif message.text == context[lang]['locate']['address']:
        user, _ = await get_user_data(message.from_user.id)

        if None in user:
            await message.answer(context[lang]['empty'])
            
        else:
            btn = await my_locate_btn(message, lang)
            await message.answer(context[lang]['locate']['choose'], reply_markup=btn)
            await LocateContact.locate_choice.set()
        

    if message.text == context[lang]['back']:
        await start_handler(message)
        await state.finish()


@dp.message_handler(state=LocateContact.locate_choice)
async def location_accept_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    btn = await fast_food_category_btn(lang)
    text = message.text
    locate, _ = await get_user_data(message.from_user.id)
    location_list = []
    for i in locate:
        try:
            location_list = i.split(";")
        except:
            location_list.append(i)

    if text == context[lang]['yes']:
        user_id = message.from_user.id
        data = await state.get_data()

        await update_user_location(user_id, data['address'])
        await message.answer(context[lang]['choose3'], reply_markup=btn)
        await insert_user_food(message.from_user.id)
        await OrderList.fast_food_category.set()

    elif text == context[lang]['no']:
        btn = await locate_btn(lang)
        await message.answer(context[lang]['locate']['send_locate'], reply_markup=btn)
        await LocateContact.location.set()

    elif text in location_list:
        await message.answer(context[lang]['choose3'], reply_markup=btn)
        await state.update_data(address=str(text))
        await insert_user_food(message.from_user.id)
        await OrderList.fast_food_category.set()

    elif text == context[lang]['back']:
        btn = await locate_btn(lang)
        await message.answer(context[lang]['locate']['send_locate'], reply_markup=btn)
        await LocateContact.location.set()


@dp.message_handler(state=OrderList.fast_food_category)
async def fast_food_category_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text

    if text == context[lang]['fast_food_category']['lavash']:
        btn = await lavash_btn(lang)
        await message.answer_photo(InputFile("img/categories/Лаваш.jpg"), reply_markup=btn)

    elif text == context[lang]['fast_food_category']['trindvich']:
        btn = await trindvich_btn(lang)
        await message.answer_photo(InputFile("img/categories/Триндвич.jpg"), reply_markup=btn)

    elif text == context[lang]['fast_food_category']['shaurma']:
        btn = await shaurma_btn(lang)
        await message.answer_photo(InputFile("img/categories/Шаурма.jpg"), reply_markup=btn)

    elif text == context[lang]['fast_food_category']['burger']:
        btn = await burger_btn(lang)
        await message.answer_photo(InputFile("img/categories/Бургеры.jpg"), reply_markup=btn)

    elif text == context[lang]['fast_food_category']['sub']:
        btn = await sub_btn(lang)
        await message.answer_photo(InputFile("img/categories/Саб.jpg"), reply_markup=btn)

    elif text == context[lang]['fast_food_category']['potato']:
        btn = await potato_btn(lang)
        await message.answer_photo(InputFile("img/categories/Картошка.jpg"), reply_markup=btn)

    elif text == context[lang]['fast_food_category']['xot-dog']:
        btn = await xot_dog_btn(lang)
        await message.answer_photo(InputFile("img/categories/Хот-Доги.jpg"), reply_markup=btn)

    elif text == context[lang]['fast_food_category']['snake']:
        btn = await snake_btn(lang)
        await message.answer_photo(InputFile("img/categories/Снэки.jpg"), reply_markup=btn)

    elif text == context[lang]['fast_food_category']['garnir']:
        btn = await garnir_btn(lang)
        await message.answer_photo(InputFile("img/categories/Гарниры.jpg"), reply_markup=btn)

    elif text == context[lang]['fast_food_category']['sous']:
        btn = await sous_btn(lang)
        await message.answer_photo(InputFile("img/categories/Соусы.jpg"), reply_markup=btn)

    elif text == context[lang]['fast_food_category']['nabor']:
        btn = await set_btn(lang)
        await message.answer_photo(InputFile("img/categories/Наборы.jpg"), reply_markup=btn)

    elif text == context[lang]['fast_food_category']['desert']:
        btn = await desert_btn(lang)
        await message.answer_photo(InputFile("img/categories/Десерты.jpg"), reply_markup=btn)

    elif text == context[lang]['fast_food_category']['hot-drink']:
        btn = await hot_drink_btn(lang)
        await message.answer_photo(InputFile("img/categories/Горячие-напитки.jpg"), reply_markup=btn)

    elif text == context[lang]['fast_food_category']['cold-drink']:
        btn = await cold_drink_btn(lang)
        await message.answer_photo(InputFile("img/categories/Холодные-напитки.jpg"), reply_markup=btn)

    elif text == context[lang]['fast_food_category']['combo']:
        btn = await combo_btn(lang)
        await message.answer_photo(InputFile("img/categories/Комбо.jpg"), reply_markup=btn)
    
    await OrderList.fast_food.set()

    if text == context[lang]['basket']:
        await basket_handler(message, state)

    elif text == context[lang]['back']:
        await delete_user_food(message.from_user.id)
        btn = await locate_btn(lang)
        await message.answer(context[lang]['locate']['send_locate'], reply_markup=btn)
        await LocateContact.location.set()


@dp.message_handler(state=OrderList.fast_food)
async def fast_food_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    btn = await back_basket_btn(lang)
    pc_btn = await food_pc_btn(1, lang)
    cost_btn1 = await food_size1_btn(lang)
    cost_btn2 = await food_size1_btn(lang)
    cost_btn3 = await food_size1_btn(lang)
    cost_btn4 = await food_size1_btn(lang)
    cost_btn5 = await food_size5_btn(lang)
    cost_btn6 = await food_size6_btn(lang)

    if text == context[lang]['fast_food_name']['lavash']['spice_meat']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/lavash/Лаваш-острый-с-говядиной.jpg"),
        caption=context[lang]['Лаваш острый с говядиной'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Лаваш острый с говядиной")
        await OrderList.in_lavash.set()


    elif text == context[lang]['fast_food_name']['lavash']['spice_chick']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/lavash/Лаваш-острый-с-курицей.jpg"),
        caption=context[lang]['Лаваш острый с курицей'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Лаваш острый с курицей")
        await OrderList.in_lavash.set()


    elif text == context[lang]['fast_food_name']['lavash']['fit']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/lavash/Фиттер.jpg"),
        caption=context[lang]['Фиттер'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Фиттер")
        await OrderList.in_lavash.set()


    elif text == context[lang]['fast_food_name']['lavash']['chick']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/lavash/Лаваш-с-курицей.jpg"), reply_markup=cost_btn1)
        await state.update_data(food="Лаваш с курицей")
        await OrderList.in_lavash.set()

    
    elif text == context[lang]['fast_food_name']['lavash']['meat']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/lavash/Лаваш-с-говядиной.jpg"), reply_markup=cost_btn2)
        await state.update_data(food="Лаваш с говядиной")
        await OrderList.in_lavash.set()


    elif text == context[lang]['fast_food_name']['lavash']['cheese_meat']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/lavash/Лаваш-с-говядиной-и-сыром.jpg"), reply_markup=cost_btn3)
        await state.update_data(food="Лаваш с говядиной и сыром")
        await OrderList.in_lavash.set()


    elif text == context[lang]['fast_food_name']['lavash']['cheese_chick']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/lavash/Лаваш-с-курицей-и-сыром.jpg"), reply_markup=cost_btn4)
        await state.update_data(food="Лаваш с курицей и сыром")
        await OrderList.in_lavash.set()


    elif text == context[lang]['fast_food_name']['trindvich']['chick']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/trindvich/Триндвич-с-курицей.jpg"),
        caption=context[lang]['Триндвич с курицей'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Триндвич с курицей")
        await OrderList.in_trindvich.set()


    elif text == context[lang]['fast_food_name']['trindvich']['meat']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/trindvich/Триндвич-с-говядиной.jpg"),
        caption=context[lang]['Триндвич с говядиной'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Триндвич с говядиной")
        await OrderList.in_trindvich.set()

    
    elif text == context[lang]['fast_food_name']['shaurma']['spice_meat']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        btn = await shaurma_btn(lang)
        await message.answer_photo(InputFile("img/fast_foods/shaurma/Шаурма-острая-с-говядиной.jpg"), reply_markup=cost_btn5)
        await state.update_data(food="Шаурма острая c говядиной")
        await OrderList.in_shaurma.set()


    elif text == context[lang]['fast_food_name']['shaurma']['chick']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        btn = await shaurma_btn(lang)
        await message.answer_photo(InputFile("img/fast_foods/shaurma/Шаурма-с-курицей.jpg"), reply_markup=cost_btn6)
        await state.update_data(food="Шаурма c курицей")
        await OrderList.in_shaurma.set()


    elif text == context[lang]['fast_food_name']['shaurma']['spice_chick']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        btn = await shaurma_btn(lang)
        await message.answer_photo(InputFile("img/fast_foods/shaurma/Шаурма-острая-c-курицей.jpg"), reply_markup=cost_btn6)
        await state.update_data(food="Шаурма острая c курицей")
        await OrderList.in_shaurma.set()


    elif text == context[lang]['fast_food_name']['shaurma']['meat']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        btn = await shaurma_btn(lang)
        await message.answer_photo(InputFile("img/fast_foods/shaurma/Шаурма-с-говядиной.jpg"), reply_markup=cost_btn5)
        await state.update_data(food="Шаурма c говядиной")
        await OrderList.in_shaurma.set()


    elif text == context[lang]['fast_food_name']['burger']['gum']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/burger/Гамбургер.jpg"),
        caption=context[lang]['Гамбургер'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Гамбургер")
        await OrderList.in_burger.set()


    elif text == context[lang]['fast_food_name']['burger']['double']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/burger/Даблбургер.jpg"),
        caption=context[lang]['Даблбургер'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Даблбургер")
        await OrderList.in_burger.set()


    elif text == context[lang]['fast_food_name']['burger']['cheese']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/burger/Чизбургер.jpg"),
        caption=context[lang]['Чизбургер'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Чизбургер")
        await OrderList.in_burger.set()


    elif text == context[lang]['fast_food_name']['burger']['doublecheese']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/burger/Даблчизбургер.jpg"),
        caption=context[lang]['Даблчизбургер'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Даблчизбургер")
        await OrderList.in_burger.set()


    elif text == context[lang]['fast_food_name']['sub']['chick']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/sub/Саб-с-курицей.jpg"),
        caption=context[lang]['Саб с курицей'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Саб с курицей")
        await OrderList.in_sub.set()


    elif text == context[lang]['fast_food_name']['sub']['cheese_chick']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/sub/Саб-с-курицей-и-сыром.jpg"),
        caption=context[lang]['Саб с курицей и сыром'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Саб с курицей и сыром")
        await OrderList.in_sub.set()


    elif text == context[lang]['fast_food_name']['sub']['cheese_meat']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/sub/Саб-с-говядиной-и-сыром.jpg"),
        caption=context[lang]['Саб с говядиной и сыром'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Саб с говядиной и сыром")
        await OrderList.in_sub.set()


    elif text == context[lang]['fast_food_name']['sub']['meat']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/sub/Саб-с-говядиной.jpg"),
        caption=context[lang]['Саб с говядиной'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Саб с говядиной")
        await OrderList.in_sub.set()


    elif text == context[lang]['fast_food_name']['potato']['village']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/potato/По-деревенски.jpg"),
        caption=context[lang]['Картофель по-деревенски'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Картофель по-деревенски")
        await OrderList.in_potato.set()


    elif text == context[lang]['fast_food_name']['potato']['free']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/potato/Фри.jpg"),
        caption=context[lang]['Картофель Фри'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Картофель Фри")
        await OrderList.in_potato.set()


    elif text == context[lang]['fast_food_name']['potato']['nuggets4']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/potato/Наггетсы-4.jpg"),
        caption=context[lang]['Наггетсы, 4 шт'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Наггетсы, 4 шт")
        await OrderList.in_potato.set()


    elif text == context[lang]['fast_food_name']['potato']['nuggets8']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/potato/Наггетсы-8.jpg"),
        caption=context[lang]['Наггетсы, 8 шт'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Наггетсы, 8 шт")
        await OrderList.in_potato.set()


    elif text == context[lang]['fast_food_name']['xot-dog']['classic']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/hot-dog/Классика.jpg"),
        caption=context[lang]['Хот-дог'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Хот-дог")
        await OrderList.in_hot_dog.set()


    elif text == context[lang]['fast_food_name']['xot-dog']['double']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/hot-dog/Дабл.jpg"),
        caption=context[lang]['ДаблХот-дог'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="ДаблХот-дог")
        await OrderList.in_hot_dog.set()


    elif text == context[lang]['fast_food_name']['xot-dog']['kids']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/hot-dog/Детский.jpg"),
        caption=context[lang]['Хот-дог детский'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Хот-дог детский")
        await OrderList.in_hot_dog.set()


    elif text == context[lang]['fast_food_name']['xot-dog']['mini']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/hot-dog/Мини.jpg"),
        caption=context[lang]['Хот-дог Мини'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Хот-дог Мини")
        await OrderList.in_hot_dog.set()


    elif text == context[lang]['fast_food_name']['snake']['smile']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/snake/Смайлики.jpg"),
        caption=context[lang]['Смайлики'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Смайлики")
        await OrderList.in_snake.set()


    elif text == context[lang]['fast_food_name']['snake']['strips']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/snake/Стрипсы.jpg"),
        caption=context[lang]['Стрипсы'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Стрипсы")
        await OrderList.in_snake.set()


    elif text == context[lang]['fast_food_name']['garnir']['ris']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/garnir/Рис.jpg"),
        caption=context[lang]['Рис'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Рис")
        await OrderList.in_garnir.set()


    elif text == context[lang]['fast_food_name']['garnir']['lepeshka']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/garnir/Лепешка.jpg"),
        caption=context[lang]['Лепешка'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Лепешка")
        await OrderList.in_garnir.set()


    elif text == context[lang]['fast_food_name']['garnir']['salat']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/garnir/Салат.jpg"),
        caption=context[lang]['Салат'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Салат")
        await OrderList.in_garnir.set()


    elif text == context[lang]['fast_food_name']['garnir']['sezar']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/garnir/Салат-Цезарь.jpg"),
        caption=context[lang]['Салат Цезарь'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Салат Цезарь")
        await OrderList.in_garnir.set()


    elif text == context[lang]['fast_food_name']['garnir']['grecheskiy']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/garnir/Салат-Греческий.jpg"),
        caption=context[lang]['Салат Греческий'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Салат Греческий")
        await OrderList.in_garnir.set()


    elif text == context[lang]['fast_food_name']['sous']['sezar']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/sous/Соус-Цезарь.jpg"),
        caption=context[lang]['Соус Цезарь'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Соус Цезарь")
        await OrderList.in_sous.set()


    elif text == context[lang]['fast_food_name']['sous']['grecheskiy']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/sous/Соус-Греческий.jpg"),
        caption=context[lang]['Соус Греческий'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Соус Греческий")
        await OrderList.in_sous.set()


    elif text == context[lang]['fast_food_name']['sous']['chili']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/sous/Чили-соус.jpg"),
        caption=context[lang]['Чили соус'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Чили соус")
        await OrderList.in_sous.set()


    elif text == context[lang]['fast_food_name']['sous']['ketchup']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/sous/Кетчуп.jpg"),
        caption=context[lang]['Кетчуп'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Кетчуп")
        await OrderList.in_sous.set()


    elif text == context[lang]['fast_food_name']['sous']['chesnok']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/sous/Чесночный-соус.jpg"),
        caption=context[lang]['Чесночный соус'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Чесночный соус")
        await OrderList.in_sous.set()


    elif text == context[lang]['fast_food_name']['sous']['cheese']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/sous/Сырный-соус.jpg"),
        caption=context[lang]['Сырный соус'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Сырный соус")
        await OrderList.in_sous.set()


    elif text == context[lang]['fast_food_name']['sous']['barbequ']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/sous/Барбекю-соус.jpg"),
        caption=context[lang]['Барбекю соус'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Барбекю соус")
        await OrderList.in_sous.set()


    elif text == context[lang]['fast_food_name']['sous']['maynez']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/sous/Майонез.jpg"),
        caption=context[lang]['Майонез'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Майонез")
        await OrderList.in_sous.set()


    elif text == context[lang]['fast_food_name']['nabor']['plus']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/set/Комбо-Плюс.jpg"),
        caption=context[lang]['Комбо Плюс'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Комбо Плюс")
        await OrderList.in_set.set()


    elif text == context[lang]['fast_food_name']['nabor']['meat']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/set/Донар-с-говядиной.jpg"),
        caption=context[lang]['Донар с говядиной'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Донар с говядиной")
        await OrderList.in_set.set()


    elif text == context[lang]['fast_food_name']['nabor']['fit']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/set/ФитКомбо.jpg"),
        caption=context[lang]['ФитКомбо'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="ФитКомбо")
        await OrderList.in_set.set()


    elif text == context[lang]['fast_food_name']['nabor']['chick']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/set/Донар-c-курицей.jpg"),
        caption=context[lang]['Донар c курицей'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Донар c курицей")
        await OrderList.in_set.set()


    elif text == context[lang]['fast_food_name']['nabor']['kids']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/set/Детское-комбо.jpg"),
        caption=context[lang]['Детское комбо'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Детское комбо")
        await OrderList.in_set.set()



    elif text == context[lang]['fast_food_name']['nabor']['box_chick']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/set/Донар-бокс-с-курицей.jpg"),
        caption=context[lang]['Донар-бокс c курицей'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Донар-бокс c курицей")
        await OrderList.in_set.set()


    elif text == context[lang]['fast_food_name']['nabor']['box_meat']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/set/Донар-бокс-с-говядиной.jpg"),
        caption=context[lang]['Донар-бокс c говядиной'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Донар-бокс c говядиной")
        await OrderList.in_set.set()


    elif text == context[lang]['fast_food_name']['desert']['caramel']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/desert/Донат-карамельный.jpg"),
        caption=context[lang]['Донат карамельный'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Донат карамельный")
        await OrderList.in_desert.set()


    elif text == context[lang]['fast_food_name']['desert']['medovik']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/desert/Медовик.jpg"),
        caption=context[lang]['Медовик'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Медовик")
        await OrderList.in_desert.set()


    elif text == context[lang]['fast_food_name']['desert']['cheesecake']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/desert/Чизкейк.jpg"),
        caption=context[lang]['Чизкейк'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Чизкейк")
        await OrderList.in_desert.set()


    elif text == context[lang]['fast_food_name']['desert']['berry']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/desert/Донат-ягодный.jpg"),
        caption=context[lang]['Донат ягодный'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Донат ягодный")
        await OrderList.in_desert.set()


    elif text == context[lang]['fast_food_name']['hot-drink']['glase']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/hot-drink/Кофе-Глясе.jpg"),
        caption=context[lang]['Кофе Глясе'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Кофе Глясе")
        await OrderList.in_hot_drink.set()


    elif text == context[lang]['fast_food_name']['hot-drink']['green_lemon']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/hot-drink/tea_green.jpg"),
        caption=context[lang]['Чай зеленый с лимоном'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Чай зеленый с лимоном")
        await OrderList.in_hot_drink.set()


    elif text == context[lang]['fast_food_name']['hot-drink']['latte']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/hot-drink/Латте.jpg"),
        caption=context[lang]['Латте'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Латте")
        await OrderList.in_hot_drink.set()


    elif text == context[lang]['fast_food_name']['hot-drink']['black_lemon']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/hot-drink/tea_black.jpg"),
        caption=context[lang]['Чай черный с лимоном'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Чай черный с лимоном")
        await OrderList.in_hot_drink.set()


    elif text == context[lang]['fast_food_name']['hot-drink']['black']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/hot-drink/tea.jpg"),
        caption=context[lang]['Чай черный'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Чай черный")
        await OrderList.in_hot_drink.set()


    elif text == context[lang]['fast_food_name']['hot-drink']['green']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/hot-drink/tea.jpg"),
        caption=context[lang]['Чай зеленый'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Чай зеленый")
        await OrderList.in_hot_drink.set()


    elif text == context[lang]['fast_food_name']['hot-drink']['capuccino']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/hot-drink/Капучино.jpg"),
        caption=context[lang]['Капучино'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Капучино")
        await OrderList.in_hot_drink.set()


    elif text == context[lang]['fast_food_name']['hot-drink']['amerikano']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/hot-drink/Американо.jpg"),
        caption=context[lang]['Американо'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Американо")
        await OrderList.in_hot_drink.set()


    elif text == context[lang]['fast_food_name']['cold-drink']['juice']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/cold-drink/Сок-Яблочный.jpg"),
        caption=context[lang]['Сок Яблочный без сахара, 0,33л'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Сок Яблочный без сахара, 0,33л")
        await OrderList.in_cold_drink.set()


    elif text == context[lang]['fast_food_name']['cold-drink']['water']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/cold-drink/Вода.jpg"),
        caption=context[lang]['Вода без газа 0,5л'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Вода без газа 0,5л")
        await OrderList.in_cold_drink.set()


    elif text == context[lang]['fast_food_name']['cold-drink']['bliss']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/cold-drink/Сок.jpg"),
        caption=context[lang]['Сок Блисс'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Сок Блисс")
        await OrderList.in_cold_drink.set()


    elif text == context[lang]['fast_food_name']['cold-drink']['pepsi05']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/cold-drink/Пепси05.jpg"),
        caption=context[lang]['Пепси, бутылка 0,5л'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Пепси, бутылка 0,5л")
        await OrderList.in_cold_drink.set()


    elif text == context[lang]['fast_food_name']['cold-drink']['pepsi15']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/cold-drink/Пепси15.jpg"),
        caption=context[lang]['Пепси, бутылка 1,5л'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Пепси, бутылка 1,5л")
        await OrderList.in_cold_drink.set()


    elif text == context[lang]['fast_food_name']['cold-drink']['pepsi04']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/cold-drink/Пепси04.jpg"),
        caption=context[lang]['Пепси, стакан 0,4л'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Пепси, стакан 0,4л")
        await OrderList.in_cold_drink.set()


    elif text == context[lang]['fast_food_name']['cold-drink']['moxito']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/cold-drink/Мохито.jpg"),
        caption=context[lang]['Мохито'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Мохито")
        await OrderList.in_cold_drink.set()


    elif text == context[lang]['fast_food_name']['cold-drink']['pina']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/cold-drink/Пина-колада.jpg"),
        caption=context[lang]['Пина колада'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Пина колада")
        await OrderList.in_cold_drink.set()


    elif text == context[lang]['fast_food_name']['combo']['student']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/combo/Студент-Комбо.jpg"),
        caption=context[lang]['Студент Комбо'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Студент Комбо")
        await OrderList.in_combo.set()


    elif text == context[lang]['fast_food_name']['combo']['sport']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/combo/Спорт-Комбо.jpg"),
        caption=context[lang]['Спорт Комбо'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Спорт Комбо")
        await OrderList.in_combo.set()


    elif text == context[lang]['fast_food_name']['combo']['m1']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/combo/М-Комбо1.jpg"),
        caption=context[lang]['М-Комбо №1'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="М-Комбо №1")
        await OrderList.in_combo.set()


    elif text == context[lang]['fast_food_name']['combo']['m2']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/combo/М-Комбо2.jpg"),
        caption=context[lang]['М-Комбо №2'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="М-Комбо №2")
        await OrderList.in_combo.set()


    elif text == context[lang]['fast_food_name']['combo']['s1']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/combo/S-Комбо1.jpg"),
        caption=context[lang]['S-Комбо №1'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="S-Комбо №1")
        await OrderList.in_combo.set()


    elif text == context[lang]['fast_food_name']['combo']['s2']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/combo/S-Комбо2.jpg"),
        caption=context[lang]['S-Комбо №2'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="S-Комбо №2")
        await OrderList.in_combo.set()


    elif text == context[lang]['fast_food_name']['combo']['s3']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/combo/S-Комбо3.jpg"),
        caption=context[lang]['S-Комбо №3'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="S-Комбо №3")
        await OrderList.in_combo.set()


    elif text == context[lang]['fast_food_name']['combo']['s4']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/combo/S-Комбо4.jpg"),
        caption=context[lang]['S-Комбо №4'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="S-Комбо №4")
        await OrderList.in_combo.set()


    elif text == context[lang]['fast_food_name']['combo']['double1']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/combo/Дабл-Комбо1.jpg"),
        caption=context[lang]['Дабл-Комбо №1'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Дабл-Комбо №1")
        await OrderList.in_combo.set()


    elif text == context[lang]['fast_food_name']['combo']['double2']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/combo/Дабл-Комбо2.jpg"),
        caption=context[lang]['Дабл-Комбо №2'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Дабл-Комбо №2")
        await OrderList.in_combo.set()


    elif text == context[lang]['fast_food_name']['combo']['double3']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/combo/Дабл-Комбо3.jpg"),
        caption=context[lang]['Дабл-Комбо №3'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Дабл-Комбо №3")
        await OrderList.in_combo.set()


    elif text == context[lang]['fast_food_name']['combo']['double4']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/combo/Дабл-Комбо4.jpg"),
        caption=context[lang]['Дабл-Комбо №4'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Дабл-Комбо №4")
        await OrderList.in_combo.set()


    elif text == context[lang]['fast_food_name']['combo']['family1']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/combo/Семейный-Комбо1.jpg"),
        caption=context[lang]['Семейный-Комбо №1'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Семейный-Комбо №1")
        await OrderList.in_combo.set()


    elif text == context[lang]['fast_food_name']['combo']['family2']:
        await message.answer(context[lang]['choose1'], reply_markup=btn)
        await message.answer_photo(InputFile("img/fast_foods/combo/Семейный-Комбо2.jpg"),
        caption=context[lang]['Семейный-Комбо №2'], reply_markup=pc_btn)
        await state.update_data(pc=1)
        await state.update_data(food="Семейный-Комбо №2")
        await OrderList.in_combo.set()


    if text == context[lang]['back']:
        btn = await fast_food_category_btn(lang)
        await message.answer(context[lang]['choose3'], reply_markup=btn)
        await OrderList.fast_food_category.set()



@dp.message_handler(state=OrderList.in_lavash)
async def in_lavash_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    if text == context[lang]['back']:
        btn = await lavash_btn(lang)
        await message.answer_photo(InputFile("img/categories/Лаваш.jpg"), reply_markup=btn)
        await OrderList.fast_food.set()
    elif text == context[lang]['basket']:
        await basket_handler(message, state)


@dp.message_handler(state=OrderList.in_trindvich)
async def in_trindvich_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    if text == context[lang]['back']:
        btn = await trindvich_btn(lang)
        await message.answer_photo(InputFile("img/categories/Триндвич.jpg"), reply_markup=btn)
        await OrderList.fast_food.set()
    elif text == context[lang]['basket']:
        await basket_handler(message, state)


@dp.message_handler(state=OrderList.in_shaurma)
async def in_shaurma_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    if text == context[lang]['back']:
        btn = await shaurma_btn(lang)
        await message.answer_photo(InputFile("img/categories/Шаурма.jpg"), reply_markup=btn)
        await OrderList.fast_food.set()
    elif text == context[lang]['basket']:
        await basket_handler(message, state)


@dp.message_handler(state=OrderList.in_burger)
async def in_burger_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    if text == context[lang]['back']:
        btn = await burger_btn(lang)
        await message.answer_photo(InputFile("img/categories/Бургеры.jpg"), reply_markup=btn)
        await OrderList.fast_food.set()
    elif text == context[lang]['basket']:
        await basket_handler(message, state)


@dp.message_handler(state=OrderList.in_sub)
async def in_sub_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    if text == context[lang]['back']:
        btn = await sub_btn(lang)
        await message.answer_photo(InputFile("img/categories/Саб.jpg"), reply_markup=btn)
        await OrderList.fast_food.set()
    elif text == context[lang]['basket']:
        await basket_handler(message, state)


@dp.message_handler(state=OrderList.in_potato)
async def in_potato_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    if text == context[lang]['back']:
        btn = await potato_btn(lang)
        await message.answer_photo(InputFile("img/categories/Картошка.jpg"), reply_markup=btn)
        await OrderList.fast_food.set()
    elif text == context[lang]['basket']:
        await basket_handler(message, state)


@dp.message_handler(state=OrderList.in_hot_dog)
async def in_xot_dog_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    if text == context[lang]['back']:
        btn = await xot_dog_btn(lang)
        await message.answer_photo(InputFile("img/categories/Хот-Доги.jpg"), reply_markup=btn)
        await OrderList.fast_food.set()
    elif text == context[lang]['basket']:
        await basket_handler(message, state)


@dp.message_handler(state=OrderList.in_snake)
async def in_snake_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    if text == context[lang]['back']:
        btn = await snake_btn(lang)
        await message.answer_photo(InputFile("img/categories/Снэки.jpg"), reply_markup=btn)
        await OrderList.fast_food.set()
    elif text == context[lang]['basket']:
        await basket_handler(message, state)


@dp.message_handler(state=OrderList.in_garnir)
async def in_garnir_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    if text == context[lang]['back']:
        btn = await garnir_btn(lang)
        await message.answer_photo(InputFile("img/categories/Гарниры.jpg"), reply_markup=btn)
        await OrderList.fast_food.set()
    elif text == context[lang]['basket']:
        await basket_handler(message, state)


@dp.message_handler(state=OrderList.in_sous)
async def in_sous_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    if text == context[lang]['back']:
        btn = await sous_btn(lang)
        await message.answer_photo(InputFile("img/categories/Соусы.jpg"), reply_markup=btn)
        await OrderList.fast_food.set()
    elif text == context[lang]['basket']:
        await basket_handler(message, state)


@dp.message_handler(state=OrderList.in_set)
async def in_set_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    if text == context[lang]['back']:
        btn = await set_btn(lang)
        await message.answer_photo(InputFile("img/categories/Наборы.jpg"), reply_markup=btn)
        await OrderList.fast_food.set()
    elif text == context[lang]['basket']:
        await basket_handler(message, state)


@dp.message_handler(state=OrderList.in_desert)
async def in_desert_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    if text == context[lang]['back']:
        btn = await desert_btn(lang)
        await message.answer_photo(InputFile("img/categories/Десерты.jpg"), reply_markup=btn)
        await OrderList.fast_food.set()
    elif text == context[lang]['basket']:
        await basket_handler(message, state)


@dp.message_handler(state=OrderList.in_hot_drink)
async def in_hot_drink_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    if text == context[lang]['back']:
        btn = await hot_drink_btn(lang)
        await message.answer_photo(InputFile("img/categories/Горячие-напитки.jpg"), reply_markup=btn)
        await OrderList.fast_food.set()
    elif text == context[lang]['basket']:
        await basket_handler(message, state)


@dp.message_handler(state=OrderList.in_cold_drink)
async def in_cold_drink_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    if text == context[lang]['back']:
        btn = await cold_drink_btn(lang)
        await message.answer_photo(InputFile("img/categories/Холодные-напитки.jpg"), reply_markup=btn)
        await OrderList.fast_food.set()
    elif text == context[lang]['basket']:
        await basket_handler(message, state)


@dp.message_handler(state=OrderList.in_combo)
async def in_combo_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    if text == context[lang]['back']:
        btn = await combo_btn(lang)
        await message.answer_photo(InputFile("img/categories/Комбо.jpg"), reply_markup=btn)
        await OrderList.fast_food.set()
    elif text == context[lang]['basket']:
        await basket_handler(message, state)


@dp.message_handler(state=OrderList.go_pc_btn)
async def go_pc_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    if text == context[lang]['back']:
        btn = await fast_food_category_btn(lang)
        await message.answer(context[lang]['choose3'], reply_markup=btn)
        await OrderList.fast_food_category.set()
    elif text == context[lang]['basket']:
        await basket_handler(message, state)



@dp.callback_query_handler(state=[OrderList.in_lavash, OrderList.in_shaurma], text_contains="food")
async def cost_food_handler(call: types.CallbackQuery, state: FSMContext):
    lang = await set_lang(call)
    cost_size = call.data.split(":")[1:]
    cost_size = ":".join(cost_size)
    btn = await food_pc_btn(1, lang)
    await state.update_data(cost_size=cost_size, pc=1)
    await call.message.edit_reply_markup(reply_markup=btn)
    await OrderList.go_pc_btn.set()


@dp.callback_query_handler(state=[OrderList.in_lavash, OrderList.in_trindvich, OrderList.in_burger,
    OrderList.in_cold_drink, OrderList.in_combo, OrderList.in_desert, OrderList.in_garnir, OrderList.in_hot_dog,
    OrderList.in_hot_drink, OrderList.in_potato, OrderList.in_set, OrderList.in_shaurma, OrderList.in_snake,
    OrderList.in_sous, OrderList.in_sub, OrderList.go_pc_btn], text="next")
async def plus_pc_handler(call: types.CallbackQuery, state: FSMContext):
    lang = await set_lang(call)
    data = await state.get_data()
    pc = data['pc']
    if pc < 100:
        pc = data['pc'] + 1
        await state.update_data(pc=pc)
        btn = await food_pc_btn(pc, lang)
        await call.message.edit_reply_markup(reply_markup=btn)
    await call.answer(f"{pc} {context[lang]['pc']}")


@dp.callback_query_handler(state=[OrderList.in_lavash, OrderList.in_trindvich, OrderList.in_burger,
    OrderList.in_cold_drink, OrderList.in_combo, OrderList.in_desert, OrderList.in_garnir, OrderList.in_hot_dog,
    OrderList.in_hot_drink, OrderList.in_potato, OrderList.in_set, OrderList.in_shaurma, OrderList.in_snake,
    OrderList.in_sous, OrderList.in_sub, OrderList.go_pc_btn], text="prev")
async def minus_pc_handler(call: types.CallbackQuery, state: FSMContext):
    lang = await set_lang(call)
    data = await state.get_data()
    pc = data['pc']
    if pc > 1:
        pc = data['pc'] - 1
        await state.update_data(pc=pc)
        btn = await food_pc_btn(pc, lang)
        await call.message.edit_reply_markup(reply_markup=btn)
    await call.answer(f"{pc} {context[lang]['pc']}")


@dp.callback_query_handler(state=[OrderList.in_lavash, OrderList.in_trindvich, OrderList.in_burger,
    OrderList.in_cold_drink, OrderList.in_combo, OrderList.in_desert, OrderList.in_garnir, OrderList.in_hot_dog,
    OrderList.in_hot_drink, OrderList.in_potato, OrderList.in_set, OrderList.in_shaurma, OrderList.in_snake,
    OrderList.in_sous, OrderList.in_sub, OrderList.go_pc_btn], text="add_basket")
async def add_basket_handler(call: types.CallbackQuery, state: FSMContext):
    lang = await set_lang(call)
    data = await state.get_data()
    address = data['address']
    btn = await fast_food_category_btn(lang)
    user_id = call.from_user.id
    try:
        await update_fast_food(data['food'], f"{data['pc']}:{data['cost_size']}", user_id)
    except:
        cost = context[lang][data['food']].split(":")[-1]
        cost = cost.split(" ")[:-1]
        cost = "".join(cost)
        await update_fast_food(data['food'], f"{data['pc']}:{cost}", user_id)
    await call.answer(f"{context[lang]['food_add']}")
    await state.reset_data()
    await state.update_data(address=str(address))
    await call.message.answer(context[lang]['choose3'], reply_markup=btn)
    await OrderList.fast_food_category.set()


@dp.message_handler()
async def basket_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    btn = await fast_food_category_btn(lang)
    in_btn = await basket_btn(message, lang)
    cost, name, _, _ = await get_cost_size(message)
    result = await get_food_data(message.from_user.id)

    await message.answer(context[lang]['choose3'], reply_markup=btn)
    if not result:
        await message.answer(f"{context[lang]['empty_basket']}")
    else:
        delivery_cost = 10000
        all_cost = delivery_cost + cost

        format_delivery_cost = cost_formatter(delivery_cost)
        format_cost = cost_formatter(cost)
        format_all_cost = cost_formatter(all_cost)

        names = "\n".join(name)

        text = f"""{context[lang]['in_basket']}\n{names}
{context[lang]['product']} {format_cost} {context[lang]['my_order']['sum']}
{context[lang]['delivery']} {format_delivery_cost} {context[lang]['my_order']['sum']}
{context[lang]['my_order']['total']} {format_all_cost} {context[lang]['my_order']['sum']}"""

        await message.answer(text, reply_markup=in_btn)
        await state.update_data(name=names, product=format_cost, delivery=format_delivery_cost, cost=format_all_cost)

    await OrderList.fast_food_category.set()


@dp.callback_query_handler(text="back", state=OrderList.fast_food_category)
async def back_basket_handler(call: types.CallbackQuery):
    lang = await set_lang(call)
    btn = await fast_food_category_btn(lang)
    await call.message.delete()
    await call.message.answer(context[lang]['choose3'], reply_markup=btn)


@dp.callback_query_handler(text="clear", state=OrderList.fast_food_category)
async def clear_basket_handler(call: types.CallbackQuery):
    lang = await set_lang(call)
    await delete_user_food(call.from_user.id)
    await insert_user_food(call.from_user.id)
    btn = await fast_food_category_btn(lang)
    await call.message.delete()
    await call.message.answer(context[lang]['choose3'], reply_markup=btn)


@dp.callback_query_handler(text="run", state=OrderList.fast_food_category)
async def run_delivery_handler(call: types.CallbackQuery):
    lang = await set_lang(call)
    btn = await contact_btn(lang)
    await call.message.answer(context[lang]['run'], reply_markup=btn)
    await OrderList.delivery.set()


now_page = 0
@dp.callback_query_handler(text="time", state=OrderList.fast_food_category)
async def time_delivery_handler(call: types.CallbackQuery):
    global now_page
    now_page = 0
    btn_list = await time_btn_menu(call)
    btn = btn_list[now_page]
    await call.message.edit_reply_markup(reply_markup=btn)
    await OrderList.fast_food_category.set()


@dp.callback_query_handler(text_contains="tnext", state=OrderList.fast_food_category)
async def next_time_menu(call: types.CallbackQuery):
    global now_page
    btn_list = await time_btn_menu(call)

    if now_page < len(btn_list) - 1:
        now_page+=1
        btn = btn_list[now_page]
        await call.message.edit_reply_markup(reply_markup=btn)
    await OrderList.fast_food_category.set()


@dp.callback_query_handler(text="tback", state=OrderList.fast_food_category)
async def back_time_handler(call: types.CallbackQuery):
    lang = await set_lang(call)
    btn = await basket_btn(call, lang)
    await call.message.edit_reply_markup(reply_markup=btn)
    await OrderList.fast_food_category.set()


@dp.callback_query_handler(text_contains="times", state=OrderList.fast_food_category)
async def set_time_handler(call: types.CallbackQuery, state: FSMContext):
    lang = await set_lang(call)
    time = call.data.split(";")[-1]
    await state.update_data(time=time)
    btn = await basket_btn(call, lang)
    await call.message.edit_reply_markup(reply_markup=btn)
    await OrderList.fast_food_category.set()


@dp.callback_query_handler(text_contains="del_food", state=OrderList.fast_food_category)
async def del_food_handler(call: types.CallbackQuery, state: FSMContext):
    lang = await set_lang(call)
    sizes = ["биг", "мини", "mini", "big"]
    
    food = call.data.split(":")[-1].strip() # .strip() для того, чтобы убрать лишние пробелы из str (могут появится в utils.py)
    food_list = food.split(" ")

    if food_list[-1] in sizes:
        food_name = " ".join(food.split(" ")[:-1])
        food_size = food.split(" ")[-1]
        await delete_fast_food(fast_food=food_name, size=food_size, user_id=call.from_user.id)
    else:
        await delete_fast_food(fast_food=food, user_id=call.from_user.id)

    result = await get_food_data(call.from_user.id)
    in_btn = await basket_btn(call, lang)
    cost, name, _, _ = await get_cost_size(call)

    if not result:
        await call.message.edit_text(f"{context[lang]['empty_basket']}")
    else:
        delivery_cost = 10000
        all_cost = delivery_cost + cost

        format_delivery_cost = cost_formatter(delivery_cost)
        format_cost = cost_formatter(cost)
        format_all_cost = cost_formatter(all_cost)

        names = "\n".join(name)

        text = f"""{context[lang]['in_basket']}\n{names}
{context[lang]['product']} {format_cost} {context[lang]['my_order']['sum']}
{context[lang]['delivery']} {format_delivery_cost} {context[lang]['my_order']['sum']}
{context[lang]['my_order']['total']} {format_all_cost} {context[lang]['my_order']['sum']}"""

        await call.message.edit_text(text, reply_markup=in_btn)
        await state.update_data(name=names, product=format_cost, delivery=format_delivery_cost, cost=format_all_cost)

    await OrderList.fast_food_category.set()
    

@dp.message_handler(state=OrderList.delivery, content_types=['contact', 'text'])
async def delivery_btn_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    if text == context[lang]['back']:
        await basket_handler(message, state)
        await OrderList.fast_food_category.set()

    elif message.contact or text.startswith('+998') and text.split("+")[-1].isdigit()==True and len(text) == 13:
        btn = await pay_btn(lang)

        if message.text:
            contact = message.text
        elif message.contact:
            contact = message.contact.phone_number

        await message.answer(f"{context[lang]['choose_pay_type']}", reply_markup=btn)
        await state.update_data(contact=contact)
        await OrderList.pay.set()
    else:
        await message.answer(f"{context[lang]['err_number']}")
        await OrderList.delivery.set()


@dp.message_handler(state=OrderList.pay, content_types=['text'])
async def pay_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    data = await state.get_data()
    btn = await ok_no_delivery_btn(lang)
    if text in context[lang]['pay_type'].values():
        await state.update_data(pay=text)
        await message.answer(f"<b>{context[lang]['my_order']['order']}: \n</b>"
                             f"{context[lang]['my_order']['address']}: {data['address']}\n\n"
                             f"{data['name']}\n\n"
                             f"{context[lang]['my_order']['pay']} {text}\n\n"
                             f"<b>{context[lang]['product']} </b> {data['product']} {context[lang]['my_order']['sum']}\n"
                             f"<b>{context[lang]['delivery']} </b> {data['delivery']} {context[lang]['my_order']['sum']}\n"
                             f"<b>{context[lang]['my_order']['total']} </b> {data['cost']} {context[lang]['my_order']['sum']}", reply_markup=btn)
        await OrderList.pay_confirm.set()

    elif text == context[lang]['back']:
        btn = await contact_btn(lang)
        await message.answer(context[lang]['run'], reply_markup=btn)
        await OrderList.delivery.set()


@dp.message_handler(content_types=['text'], state=OrderList.pay_confirm)
async def pay_confirm_handler(message: types.Message, state: FSMContext):
    lang = await set_lang(message)
    text = message.text
    data = await state.get_data()
    if text == context[lang]['confirm']:
        try:
            await insert_order(message.from_user.id, data['name'], data['address'], data['pay'], data['time'], data['cost'])
        except:
            _, time = delivery_time()
            await insert_order(message.from_user.id, data['name'], data['address'], data['pay'], time, data['cost'])
        await message.answer(f"<b>{context[lang]['my_order']['order']} {context[lang]['my_order']['complete']}</b>")
        await delete_user_food(message.from_user.id)

    elif text == context[lang]['cancel']:
        await delete_user_food(message.from_user.id)
    await start_handler(message)
    await state.finish()



if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=create_tables)