import telebot
import os
from environs import Env
from datetime import datetime

import aio_parser as hh
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
    start = datetime.now()
    links = hh.LinkCollector(
        task.keySkill,
        task.numberOfSearchPages,
        task.topN).get_links()
    scraper = hh.WebScraper(links)
    skills = scraper.return_skills_list()
    skills_dataframe = hh.make_results(skills, task.topN)
    make_photo = hh.plot(skills_dataframe)
    photo = open(make_photo, 'rb')
    bot.send_photo(message.chat.id, photo,
                   reply_markup=markups.start_markup)
    end = datetime.now()
    total = end - start
    task.isRunning = False
    bot.send_message(
        message.chat.id, f'Задача выполнена за {total}. Чтобы начать заново, нажмите "/start"')


def remove_png():
    for file in os.listdir(path='.'):
        if file.endswith('.png'):
            os.remove(os.path.join('.', file))


bot.polling(none_stop=True)
