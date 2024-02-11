import sqlite3 as sql

from aiogram.types import Message
from utils import db_data_converter, db_symbol_converter

async def connect_to_sql():
    con = sql.connect("evos_food.db")
    cur = con.cursor()
    return con, cur


async def create_tables(dp):
    con, cur = await connect_to_sql()

    cur.execute("""CREATE TABLE IF NOT EXISTS Zakaz(
                user_id INTEGER,
                my_order TEXT,
                location TEXT,
                pay_type VARCHAR(20),
                time VARCHAR(10),
                cost INTEGER

    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS User(
                user_id INTEGER PRIMARY KEY,
                location TEXT,
                language VARCHAR(10) DEFAULT ru
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Feedbacks(
                user_id INTEGER,
                contact VARCHAR(30),
                feedback TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS fast_foods(
                user_id INTEGER,
                Лаваш_с_курицей TEXT,
                Лаваш_с_говядиной_и_сыром TEXT,
                Лаваш_острый_с_говядиной TEXT,
                Лаваш_острый_с_курицей TEXT,
                Лаваш_с_курицей_и_сыром TEXT,
                Фиттер TEXT,
                Лаваш_с_говядиной TEXT,

                Триндвич_с_курицей TEXT,
                Триндвич_с_говядиной TEXT,

                Шаурма_острая_c_говядиной TEXT,
                Шаурма_c_курицей TEXT,
                Шаурма_острая_c_курицей TEXT,
                Шаурма_c_говядиной TEXT,

                Гамбургер TEXT,
                Даблбургер TEXT,
                Чизбургер TEXT,
                Даблчизбургер TEXT,

                Саб_с_курицей TEXT,
                Саб_с_курицей_и_сыром TEXT,
                Саб_с_говядиной_и_сыром TEXT,
                Саб_с_говядиной TEXT,

                Картофель_по__деревенски TEXT,
                Картофель_Фри TEXT,
                Наггетсы____4_шт TEXT,
                Наггетсы____8_шт TEXT,

                Хот__дог TEXT,
                ДаблХот__дог TEXT,
                Хот__дог_детский TEXT,
                Хот__дог_Мини TEXT,

                Смайлики TEXT,
                Стрипсы TEXT,

                Рис TEXT,
                Лепешка TEXT,
                Салат TEXT,
                Салат_Цезарь TEXT,
                Салат_Греческий TEXT,

                Соус_Цезарь TEXT,
                Соус_Греческий TEXT,
                Чили_соус TEXT,
                Кетчуп TEXT,
                Чесночный_соус TEXT,
                Сырный_соус TEXT,
                Барбекю_соус TEXT,
                Майонез TEXT,

                Комбо_Плюс TEXT,
                Донар_с_говядиной TEXT,
                ФитКомбо TEXT,
                Донар_c_курицей TEXT,
                Детское_комбо TEXT,
                Донар__бокс_c_курицей TEXT,
                Донар__бокс_с_говядиной TEXT,

                Донат_карамельный TEXT,
                Медовик TEXT,
                Чизкейк TEXT,
                Донат_ягодный TEXT,

                Кофе_Глясе TEXT,
                Чай_зеленый_с_лимоном TEXT,
                Латте TEXT,
                Чай_черный_с_лимоном TEXT,
                Чай_черный TEXT,
                Чай_зеленый TEXT,
                Капучино TEXT,
                Американо TEXT,

                Сок_Яблочный_без_сахара____0___33л TEXT,
                Вода_без_газа_0___5л TEXT,
                Сок_Блисс TEXT,
                Пепси____бутылка_0___5л TEXT,
                Пепси____бутылка_1___5л TEXT,
                Пепси____стакан_0___4л TEXT,
                Мохито TEXT,
                Пина_колада TEXT,

                Студент_Комбо TEXT,
                Спорт_Комбо TEXT,
                М__Комбо_№1 TEXT,
                М__Комбо_№2 TEXT,
                S__Комбо_№1 TEXT,
                S__Комбо_№2 TEXT,
                S__Комбо_№3 TEXT,
                S__Комбо_№4 TEXT,
                Дабл__Комбо_№1 TEXT,
                Дабл__Комбо_№2 TEXT,
                Дабл__Комбо_№3 TEXT,
                Дабл__Комбо_№4 TEXT,
                Семейный__Комбо_№1 TEXT,
                Семейный__Комбо_№2 TEXT
    )""")

    con.commit()
    con.close()


async def insert_order(user_id, my_order, location, pay_type, time, cost):
    con, cur = await connect_to_sql()

    cur.execute("INSERT INTO Zakaz VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, my_order, location, pay_type, time, cost))

    con.commit()


async def insert_user(user_id):
    con, cur = await connect_to_sql()
    try:
        cur.execute("INSERT INTO User (user_id) VALUES (?)",
                    (user_id,))
    except:
        pass

    con.commit()


async def update_user_location(user_id, location):
    con, cur = await connect_to_sql()

    data = cur.execute("SELECT location FROM User WHERE user_id = ?", (user_id,)).fetchone()

    if None in data:
        cur.execute(f"UPDATE User SET location = ? WHERE user_id = ?", (location, user_id))
    else:
        if location in data[0]:
            pass
        else:
            cur.execute("UPDATE User SET location = location || ';' || ? WHERE user_id = ?", (location, user_id))

    con.commit()


async def update_user_lang(user_id, lang):
    con, cur = await connect_to_sql()

    cur.execute(f"UPDATE User SET language = ? WHERE user_id = ?", (lang, user_id))

    con.commit()


async def insert_feedback(user_id, contact, feedback):
    con, cur = await connect_to_sql()

    cur.execute("INSERT INTO Feedbacks VALUES (?, ?, ?)", (user_id, contact, feedback))

    con.commit()


async def insert_user_food(user_id):
    con, cur = await connect_to_sql()

    cur.execute("INSERT INTO fast_foods (user_id) VALUES (?)", (user_id,))

    con.commit()


async def delete_user_food(user_id):
    con, cur = await connect_to_sql()

    cur.execute("DELETE FROM fast_foods WHERE user_id = ?", (user_id,))

    con.commit()


async def update_fast_food(fast_food, pc, user_id):
    con, cur = await connect_to_sql()

    fast_food = db_symbol_converter(fast_food)
    
    select_query = f"SELECT {fast_food} FROM fast_foods WHERE user_id = ?"
    data = cur.execute(select_query, (user_id,)).fetchone()[0]
    
    if data:
        pc1 = pc.split(":")
        result = db_data_converter(data)
                
        for lists in result:
            if lists.count(pc1[-1]) == 1:
                sum_pc = int(pc1[0])+int(lists[0])
                old_pc = ":".join(lists)
                lists.pop(0)
                lists.insert(0, str(sum_pc))
                new_pc = ":".join(lists)

                update_food = f"UPDATE fast_foods SET {fast_food} = REPLACE({fast_food}, '{old_pc}', '{new_pc}') WHERE user_id = ?"
                cur.execute(update_food, (user_id,))

            elif len(result) == 1:
                update_query = f"UPDATE fast_foods SET {fast_food} = {fast_food} || ';' || ? WHERE user_id = ?"
                cur.execute(update_query, (pc, user_id))

    else:
        cur.execute(f"UPDATE fast_foods SET {fast_food} = ? WHERE user_id = ?", (pc, user_id))

    con.commit()


async def get_order_data(user_id):
    con, cur = await connect_to_sql()

    info = cur.execute(
        "SELECT * FROM Zakaz WHERE user_id = ?", (user_id,)).fetchall()

    return info


async def get_user_data(user_id):
    con, cur = await connect_to_sql()

    location = cur.execute("SELECT location FROM User WHERE user_id = ?",
                       (user_id,)).fetchone()
    
    language = cur.execute("SELECT language FROM User WHERE user_id = ?",
                       (user_id,)).fetchone()

    return location, language



async def get_feedback_data(user_id):
    con, cur = await connect_to_sql()

    info = cur.execute("SELECT * FROM Feedbacks WHERE user_id = ?",
                       (user_id,)).fetchall()

    return info


async def get_food_data(user_id):
    con, cur = await connect_to_sql()
    
    cur.execute("SELECT * FROM fast_foods LIMIT 1")
    columns = [desc[0] for desc in cur.description]
    
    food_name = []
    new_food_name = []
    for i in columns:
        info = cur.execute(f"SELECT COUNT(*) FROM fast_foods WHERE {i} IS NOT NULL AND user_id = ?", (user_id,)).fetchone()[0]

        if info > 0:
            food_name.append(i)

    if food_name:
        food_name.pop(0)

    up_sym = ["___", "__", "_"]
    for k in food_name:
        for a in up_sym:
            if a in k:
                if a == "___":
                    new = ",".join(k.split("___"))
                elif a == "__":
                    new = "-".join(k.split("__"))
                elif a == "_":
                    new = " ".join(k.split("_"))
                k = new
        new_food_name.append(k)

    cost = []
    for j in food_name[0:]:
        food_info = cur.execute(f"SELECT {j} FROM fast_foods WHERE user_id = ?", (user_id,)).fetchone()[0]
        cost.append(food_info)
    foods = {}
    for m, n in zip(new_food_name, cost):
        if n:
            foods[m] = n

    return foods



async def delete_fast_food(fast_food, user_id, size=None):
    con, cur = await connect_to_sql()

    fast_food = db_symbol_converter(fast_food)

    select_query = f"SELECT {fast_food} FROM fast_foods WHERE user_id = ?"
    data = cur.execute(select_query, (user_id,)).fetchone()[0]

    result = db_data_converter(data)
    if size:
        for list_data in result:
            if list_data[1] == size:
                food = ":".join(list_data)
                delete_food = f"UPDATE fast_foods SET {fast_food} = REPLACE({fast_food}, ?, '') WHERE user_id = ?"
                cur.execute(delete_food, (food, user_id))

        if len(result) == 2:
            delete_food = f"UPDATE fast_foods SET {fast_food} = REPLACE({fast_food}, ?, '') WHERE user_id = ?"
            cur.execute(delete_food, (';', user_id))
    else:
        delete_food = f"UPDATE fast_foods SET {fast_food} = REPLACE({fast_food}, ?, '') WHERE user_id = ?"
        cur.execute(delete_food, (data, user_id))

    con.commit()