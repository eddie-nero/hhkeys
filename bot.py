import telebot
from environs import Env

import hhkeys_parser as hh
from Task import Task

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
            message, f'Привет. Я hhkeys_bot. Приятно познакомиться, {message.from_user.first_name}. Для начала работы отправьте ключевое слово для желаемой профессии, чтобы узнать какие ключевые навыки хотят видеть работодатели. Например: python, back-end, маникюр или грузчик :)')
        bot.register_next_step_handler(msg, askSkill)
        task.isRunning = True


def askSkill(message):
    task.keySkill = message.text
    msg = bot.reply_to(message, 'Какое количество страниц поиска по ключевому слову Вы желаете охватить? (одна страница - 50 вакансий). Максимум 40 страниц, но это долго. Скорее всего, для понимания всей картины, Вам хватит 3-4 страницы')
    bot.register_next_step_handler(msg, askPages)


def askPages(message):
    if not message.text.isdigit():
        msg = bot.reply_to(
            message, 'Количество страниц должно быть числом, введите снова')
        bot.register_next_step_handler(msg, askSkill)
        return
    task.numberOfSearchPages = int(message.text)
    msg = bot.reply_to(
        message, 'Топ-N. Сколько самых популярных ключевых навыков Вы хотите увидеть в результате?')
    bot.register_next_step_handler(msg, askTopN)


def askTopN(message):
    if not message.text.isdigit():
        msg = bot.reply_to(
            message, 'Количество ключевых навыков должно быть числом, введите снова')
        bot.register_next_step_handler(msg, askPages)
        return
    task.topN = int(message.text)
    task.isRunning = False
    output = hh.KeySkillsSearch(
        task.keySkill, task.numberOfSearchPages, task.topN)
    output.find_number_of_search_pages()
    output.collect_vacancy_hrefs()
    output.collect_keyskills_from_hrefs()
    output.make_results()
    msg = bot.reply_to(message, output.top_skills)


bot.polling(none_stop=True)
