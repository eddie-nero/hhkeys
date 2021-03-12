import telebot
import time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from environs import Env

import hhkeys_parser as hh
from Task import Task
import markups

# read envoirments variables

env = Env()
env.read_env()

# setup main variables

bot = telebot.TeleBot(env('TOKEN'))
task = Task()

# handlers


@bot.message_handler(commands=['start'])
def welcome_message(message):
    if not task.isRunning:
        msg = bot.reply_to(
            message, f'Привет. Я hhkeys_bot. Приятно познакомиться, {message.from_user.first_name}. Для начала работы отправьте ключевое слово для желаемой профессии, чтобы узнать какие ключевые навыки хотят видеть работодатели. Например: python, back-end, маникюр или грузчик :)', )
        bot.register_next_step_handler(msg, askSkill)
        task.isRunning = True
        remove_png()


def askSkill(message):
    task.keySkill = message.text
    msg = bot.reply_to(message, 'Какое количество страниц поиска по ключевому слову Вы желаете охватить? (одна страница - 50 вакансий). Максимум 40 страниц, но это долго. Скорее всего, для понимания всей картины, Вам хватит 3-4 страницы')
    bot.register_next_step_handler(msg, askPages)


def askPages(message):
    if not message.text.isdigit():
        msg = bot.reply_to(
            message, 'Количество страниц должно быть числом, введите снова')
        bot.register_next_step_handler(msg, askPages)
        return
    elif int(message.text) < 1:
        msg = bot.reply_to(
            message, 'Количество страниц должно быть числом больше 0 :)')
        bot.register_next_step_handler(msg, askPages)
        return
    task.numberOfSearchPages = int(message.text)
    msg = bot.reply_to(
        message, 'Топ-N. Сколько самых популярных ключевых навыков Вы хотите увидеть в результате?')
    bot.register_next_step_handler(msg, askTopN)


def askTopN(message):
    if not message.text.isdigit():
        msg = bot.reply_to(
            message, 'Количество ключевых навыков должно быть числом, введите снова')
        bot.register_next_step_handler(msg, askTopN)
        return
    elif int(message.text) < 1:
        msg = bot.reply_to(
            message, 'Количество ключевых навыков должно быть числом больше 0 :)')
        bot.register_next_step_handler(msg, askTopN)
        return
    bot.send_chat_action(message.chat.id, 'upload_photo')
    task.topN = int(message.text)
    output = hh.KeySkillsSearch(
        task.keySkill, task.numberOfSearchPages, task.topN)
    output.find_number_of_search_pages()
    output.collect_vacancy_hrefs()
    output.collect_keyskills_from_hrefs()
    output.make_results()
    filename = f'output_{output.key_skill}_{time.time()}.png'

    def plot(df):

        def absolute_value(val):
            a = np.round(val/100*df.iloc[:, 1].sum(), 0)
            return int(a)

        labels = df.iloc[:, 0].to_list()
        fig1, ax1 = plt.subplots()
        ax1.pie(df.iloc[:, 1], labels=labels, autopct=absolute_value)
        ax1.axis('equal')
        ax1.get_figure().savefig(filename)
    plot(output.top_skills)
    photo = open(filename, 'rb')
    bot.send_photo(message.chat.id, photo,
                   reply_markup=markups.start_markup)
    task.isRunning = False
    bot.send_message(message.chat.id, 'Чтобы начать заново, нажмите "/start"')


def remove_png():
    for file in os.listdir(path='.'):
        if file.endswith('.png'):
            os.remove(os.path.join('.', file))


bot.polling(none_stop=True)
