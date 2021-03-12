from telebot import types

start_markup = types.ReplyKeyboardMarkup(
    row_width=2, resize_keyboard=True, one_time_keyboard=True)
start_markup_btn1 = types.KeyboardButton('/start')
start_markup.add(start_markup_btn1)
