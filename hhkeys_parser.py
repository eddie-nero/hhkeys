from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime
import pandas as pd
import numpy as np
import multiprocessing as mp


class KeySkillsSearch:
    def __init__(self, key_skill, n_pages, top_n):
        if n_pages > 40:
            print(
                'Количество страниц не может быть более 40. Значение остается по умолчанию (2 страницы)')
            self.n_pages = 2
        self.n_pages = n_pages - 1
        self.top_n = top_n
        self.vacancy_hrefs = mp.Manager().list()
        self.key_skills = mp.Manager().list()
        self.key_skill = key_skill
        self.page_number = 0
        self.url = f'https://hh.ru/search/vacancy?L_is_autosearch=false&clusters=true&enable_snippets=true&text={self.key_skill}&page='

    def get_html(self, url):
        url = url + str(self.page_number)
        my_headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
        }
        r = requests.get(url, headers=my_headers)
        if r.status_code == 200:
            return r.text

    def find_number_of_search_pages(self):
        soup = BeautifulSoup(self.get_html(self.url), 'lxml')
        try:
            self.number_of_search_pages = soup.find_all(
                'span',
                class_='pager-item-not-in-short-range')[-1].find('a').text
        except Exception:
            self.number_of_search_pages = '1'
        self.total_vacancies = soup.find('h1', class_='bloko-header-1').text
        print('Найдено', self.total_vacancies, 'на',
              self.number_of_search_pages, 'странице(-ах)')
        if int(self.number_of_search_pages) > int(self.n_pages):
            self.number_of_search_pages = self.n_pages

    def collect_vacancy_hrefs(self, page_number):
        self.page_number = page_number
        soup = BeautifulSoup(self.get_html(self.url), 'lxml')
        for a in soup.find_all('a', href=True, attrs={'data-qa': 'vacancy-serp__vacancy-title'}):
            self.vacancy_hrefs.append(a['href'])
        if self.number_of_search_pages == '1':
            return

    def collect_keyskills_from_hrefs(self, href):
        time.sleep(2)
        try:
            vac_html = self.get_html(href)
        except:
            time.sleep(5)
            vac_html = self.get_html(href)
        if vac_html == None:
            return
        vac_soup = BeautifulSoup(vac_html, 'lxml')
        for key in vac_soup.find_all('span', attrs={'data-qa': 'bloko-tag__text'}):
            self.key_skills.append(key.text)

    def make_results(self):
        reallist = list(self.key_skills)
        df = pd.DataFrame(reallist)
        self.top_skills = df.value_counts().head(self.top_n).to_frame()
        self.top_skills.index.names = ['KeySkill']
        self.top_skills.columns = ['N_times']
        self.top_skills.reset_index(inplace=True)
        print(self.top_skills)

    def run():
        user_input = input(
            'Для начала работы отправьте ключевое слово для желаемой \nпрофессии, чтобы узнать какие ключевые навыки хотят видеть работодатели. \nНапример: python, back-end, маникюр или грузчик :)\n')
        n_pages = int(input(
            'Какое количество страниц поиска по ключевому слову Вы желаете охватить? (одна страница - 50 вакансий)\n'))
        top_n = int(input(
            'Топ-N. Сколько самых популярных ключевых навыков Вы хотите увидеть в результате?\n'))
        start = datetime.now()
        main = KeySkillsSearch(user_input, n_pages, top_n)
        main.find_number_of_search_pages()
        with mp.Pool(processes=12) as pool:
            pool.map(main.collect_vacancy_hrefs, range(
                int(main.number_of_search_pages) + 1))
        with mp.Pool(processes=12) as pool:
            pool.map(main.collect_keyskills_from_hrefs,
                     main.vacancy_hrefs)
        main.make_results()
        end = datetime.now()
        total_time = end - start
        print(total_time)


if __name__ == '__main__':
    KeySkillsSearch.run()
