from math import lgamma

import os
import telebot
from telebot import types
from function import add_client, get_clients, del_client, init_db, get_orders_func, add_order_func, suc_order, add_remembers_func, start_scheduler, del_order, pay_order

init_db()

TOKEN = os.getenv("BOT_TOKEN") #"8832861775:AAGr7AUrsm8RPWDCB1lx-NA_ltymC0KtY5c"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn2 = types.KeyboardButton('посмотреть статистику')
    btn1 = types.KeyboardButton('работа с заказами')
    btn3 = types.KeyboardButton('работа с клиентами')
    markup.add(btn1, btn2, btn3)

    bot.reply_to(message, "выбирите действие:", reply_markup=markup)
    return

@bot.message_handler(func=lambda message: message.text == 'работа с заказами')
def orders_start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn4 = types.KeyboardButton('добавить заказ')
    btn8 = types.KeyboardButton('удалить заказ')
    btn5 = types.KeyboardButton('получить все заказы')
    btn6 = types.KeyboardButton('посмотреть заказы в работе')
    btn7 = types.KeyboardButton('выполнить заказ')
    btn9 = types.KeyboardButton('оплатить заказ')
    btn10 = types.KeyboardButton('назад')
    markup.add(btn4, btn8, btn5, btn6, btn7, btn9, btn10)

    bot.reply_to(message, "выбирите действие с клиентом:", reply_markup=markup)
    return

@bot.message_handler(func=lambda message: message.text == 'назад')
def back(message):
    start(message)
    return

@bot.message_handler(func=lambda message: message.text == 'работа с клиентами')
def client_start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('добавить клиента')
    btn3 = types.KeyboardButton('удалить клиента')
    btn10 = types.KeyboardButton('должники')
    btn11 = types.KeyboardButton('напомнить должнику')
    btn152 = types.KeyboardButton('назад')
    markup.add(btn1, btn3, btn10, btn11, btn152)

    bot.reply_to(message, "выбирите действие с клиентом:", reply_markup=markup)
    return
@bot.message_handler(func=lambda message: message.text == 'добавить клиента')
def add_client_bot(message):
    client_data = {}
    client_data["id_user"] = message.chat.id
    bot.reply_to(message, "введите имя(название) клиента:")
    bot.register_next_step_handler(message, lambda msg: get_name_client(msg, client_data))

def get_name_client(message, client_data):
    client_data['name'] = message.text
    bot.reply_to(message, "клиент создается...")
    result = add_client(client_data)
    bot.reply_to(message, f"номер клиента: {result}")

@bot.message_handler(func=lambda message: message.text == "посмотреть статистику")
def get_stats(message):
    total = 0
    total_clients = 0
    total_orders = 0
    result_clients = get_clients(message.chat.id)
    result_orders = get_orders_func(message.chat.id)
    max_client_total = ""
    max_total = 0
    print(result_clients)
    print(result_orders)
    if result_clients == []:
        bot.reply_to(message, "пока что клиентов не было")
        return
    if result_orders == []:
        bot.reply_to(message, "пока что заказов не было")
        return
    for i in result_clients:
        total_client_max = 0
        total_clients += 1
        for j in result_orders:
            if i[0] == j[1]:
                total_client_max += j[3]
            total += j[3]
            total_orders += 1
        if max_total < total_client_max:
            max_total = total_client_max
            max_client_total = i[2]

    mid = total / total_orders

    bot.reply_to(message, f"💰 Выручка: {total}₽\n📦 Заказов: {total_orders}(средний чек: {mid}₽)\n👥 Клиентов в базе: {total_clients}\n🏆 Топ-клиент: {max_client_total}({max_total}₽)")

@bot.message_handler(func=lambda message: message.text == 'удалить клиента')
def del_client_bot(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    result = get_clients(message.chat.id)
    if result == []:
        bot.reply_to(message, "пока что клиентов не было")
        return
    for i in result:
        btn = types.KeyboardButton(i[2])
        markup.add(btn)
    bot.reply_to(message, "выбирите клиента:", reply_markup=markup)
    bot.register_next_step_handler(message, del_client_id)

def del_client_id(message):
    name = message.text
    result = del_client(name, message.chat.id)
    bot.reply_to(message, f"{result}")
    start(message)

@bot.message_handler(func=lambda message: message.text == "получить все заказы")
def get_orders(message):
    result = get_orders_func(message.chat.id)
    if result == []:
        bot.reply_to(message, "заказов пока нет")
        return
    text = "список заказов:\n----------\n"
    for i in result:
        text += f"id: {i[0]}\nclient id: {i[1]}\norder: {i[2]}\nprice: {i[3]}\nstatus: {i[4]}\n----------\n"
    bot.reply_to(message, text)
    start(message)

@bot.message_handler(func=lambda message: message.text == "посмотреть заказы в работе")
def get_orders_now(message):
    result = get_orders_func(message.chat.id)
    if result == []:
        bot.reply_to(message, "заказов пока нет")
        return
    text = "список заказов:\n----------\n"
    for i in result:
        if i[4] != 'success':
            text += f"id: {i[0]}\nclient id: {i[1]}\norder: {i[2]}\nprice: {i[3]}\nstatus: {i[4]}\n----------\n"
    bot.reply_to(message, text)
    start(message)

@bot.message_handler(func=lambda message: message.text == "должники")
def get_orders_now(message):
    result = get_orders_func(message.chat.id)
    if result == []:
        bot.reply_to(message, "заказов пока нет")
        return
    text = "список заказов:\n----------\n"
    for i in result:
        if i[4] != 'payed' and i[4] != 'now':
            text += f"id: {i[0]}\nclient id: {i[1]}\norder: {i[2]}\nprice: {i[3]}\nstatus: {i[4]}\n----------\n"
    bot.reply_to(message, text)
    start(message)

@bot.message_handler(func=lambda message: message.text == "добавить заказ")
def add_order(message):
    order_data = {}
    order_data["id_user"] = message.chat.id
    bot.reply_to(message, "введите id клиента:")
    bot.register_next_step_handler(message, lambda msg: add_order_order(msg, order_data))

def add_order_order(message, order_data):
    order_data["client_id"] = message.text
    bot.reply_to(message, "введите заказ клиента:")
    bot.register_next_step_handler(message, lambda msg: add_order_price(msg, order_data))

def add_order_price(message, order_data):
    order_data["order"] = message.text
    bot.reply_to(message, "введите стоимость заказа:")
    bot.register_next_step_handler(message, lambda msg: add_order_response(msg, order_data))

def add_order_response(message, order_data):
    order_data["price"] = message.text
    bot.reply_to(message, "через сколько дней вам напомнить?")
    bot.register_next_step_handler(message, lambda msg: last_order_create(msg, order_data))

def last_order_create(message, order_data):
    order_data['time'] = message.text
    bot.reply_to(message, "заказ создается...")
    result = add_order_func(order_data)
    order_data['order'] = result
    result_remember = add_remembers_func(order_data)
    bot.reply_to(message, f"{result}")

@bot.message_handler(func=lambda message: message.text == 'оплатить заказ')
def payed_order_bot(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    result = get_orders_func(message.chat.id)
    if result == []:
        bot.reply_to(message, "пока что заказов не было")
        return
    text = "список заказов:\n----------\n"
    for i in result:
        text += f"id: {i[0]}\nclient id: {i[1]}\norder: {i[2]}\n----------\n"
        btn = types.KeyboardButton(i[0])
        markup.add(btn)
    bot.reply_to(message, text)
    bot.reply_to(message, "выбирите заказ:", reply_markup=markup)
    bot.register_next_step_handler(message, success_order_id)

def payed_order_id(message):
    name = message.text
    result = pay_order(name, message.chat.id)
    bot.reply_to(message, f"{result}")
    start(message)

@bot.message_handler(func=lambda message: message.text == 'выполнить заказ')
def success_order_bot(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    result = get_orders_func(message.chat.id)
    if result == []:
        bot.reply_to(message, "пока что заказов не было")
        return
    text = "список заказов:\n----------\n"
    for i in result:
        text += f"id: {i[0]}\nclient id: {i[1]}\norder: {i[2]}\n----------\n"
        btn = types.KeyboardButton(i[0])
        markup.add(btn)
    bot.reply_to(message, text)
    bot.reply_to(message, "выбирите заказ:", reply_markup=markup)
    bot.register_next_step_handler(message, success_order_id)

def success_order_id(message):
    name = message.text
    result = suc_order(name, message.chat.id)
    bot.reply_to(message, f"{result}")
    start(message)

@bot.message_handler(func=lambda message: message.text == 'напомнить должнику')
def payed_dol__order_bot(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    result = get_orders_func(message.chat.id)
    if result == []:
        bot.reply_to(message, "пока что заказов не было")
        return
    text = "список заказов:\n----------\n"
    for i in result:
        if i[4] != 'payed' and i[4] != 'now':
            text += f"id: {i[0]}\nclient id: {i[1]}\norder: {i[2]}\nprice: {i[3]}\nstatus: {i[4]}\n----------\n"
            btn = types.KeyboardButton(i[0])
            markup.add(btn)
    bot.reply_to(message, text)
    bot.reply_to(message, "выбирите заказ:", reply_markup=markup)
    bot.register_next_step_handler(message, payed_dol_bot)

def payed_dol_bot(message):
    client_name = ""
    client_id = 0
    order = ""
    price = 0
    name = message.text
    result = get_orders_func(message.chat.id)
    if result == []:
        bot.reply_to(message, "пока что заказов не было")
        return
    for i in result:
        if int(i[0]) == int(name):
            client_id = i[1]
            order = i[2]
            price = i[3]
    result = get_clients(message.chat.id)
    for client in result:
        if int(client[0]) == int(client_id):
            client_name = client[2]
    bot.reply_to(message, f"Привет, {client_name}! Напоминаю, что по заказу {order} осталась сумма {price}. Когда сможешь оплатить?")
    start(message)


@bot.message_handler(func=lambda message: message.text == 'удалить заказ')
def del_order_bot(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    result = get_orders_func(message.chat.id)
    if result == []:
        bot.reply_to(message, "пока что заказов не было")
        return
    for i in result:
        btn = types.KeyboardButton(i[0])
        markup.add(btn)
    text = "список заказов:\n----------\n"
    for i in result:
        text += f"id: {i[0]}\nclient id: {i[1]}\norder: {i[2]}\nprice: {i[3]}\nstatus: {i[4]}\n----------\n"
    bot.reply_to(message, text)
    bot.reply_to(message, "выбирите заказ:", reply_markup=markup)
    bot.register_next_step_handler(message, del_order_id)

def del_order_id(message):
    name = message.text
    result = del_order(name)
    bot.reply_to(message, f"{result}")
    start(message)

scheduler = start_scheduler()

if __name__ == '__main__':
    bot.infinity_polling()
