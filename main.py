from bs4 import BeautifulSoup
from tqdm import tqdm
import requests
import time
import pandas as pd
import numpy as np


class KeySkillsSearch:
    def __init__(self, key_skill, n_pages, top_n):
        if n_pages > 40:
            print(
                'Количество страниц не может быть более 40. Значение остается по умолчанию (2 страницы)')
            self.n_pages = 2
        self.n_pages = n_pages - 1
        self.top_n = top_n
        self.vacancy_hrefs = []
        self.key_skill = key_skill
        self.page_number = 0
        self.url = f'https://hh.ru/search/vacancy?L_is_autosearch=false&clusters=true&enable_snippets=true&text={self.key_skill}&page='
        self.my_headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
        }

    def find_number_of_search_pages(self):
        r = requests.get(self.url, headers=self.my_headers)
        soup = BeautifulSoup(r.text, 'lxml')
        try:
            self.number_of_search_pages = soup.find_all(
                'span',
                class_='pager-item-not-in-short-range')[-1].find('a').text
        except Exception:
            self.number_of_search_pages = '1'
        self.total_vacancies = soup.find('h1', class_='bloko-header-1').text
        print('Найдено', self.total_vacancies, 'на',
              self.number_of_search_pages, 'странице(-ах)')

    def collect_vacancy_hrefs(self):
        next_page = self.url + str(self.page_number)
        time.sleep(2)
        response = requests.get(next_page, headers=self.my_headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            for a in soup.find_all('a', href=True, attrs={'data-qa': 'vacancy-serp__vacancy-title'}):
                self.vacancy_hrefs.append(a['href'])
            print(f'Собрано ссылок: {len(self.vacancy_hrefs)}')
        if self.number_of_search_pages == '1':
            return
        if self.page_number < self.n_pages:
            self.page_number += 1
            self.collect_vacancy_hrefs()

    def collect_keyskills_from_hrefs(self):
        self.key_skills_filename = f'keyskills_{self.key_skill}_{time.time()}'
        with open(f'{self.key_skills_filename}.txt', 'w', encoding='UTF-8') as outfile:
            print('Начинаем извлечение скиллов')
            for vacancy in tqdm(self.vacancy_hrefs, colour='yellow', ncols=100, unit='req'):
                try:
                    request = requests.get(vacancy, headers=self.my_headers)
                except:
                    time.sleep(5)
                    request = requests.get(vacancy, headers=self.my_headers)
                vac_soup = BeautifulSoup(request.content, 'lxml')
                for key in vac_soup.find_all('span', attrs={'data-qa': 'bloko-tag__text'}):
                    outfile.write(key.text)
                    outfile.write('\n')

    def make_results(self):
        df = pd.read_csv(f'{self.key_skills_filename}.txt',
                         sep='\n', header=None)
        top_skills = df.value_counts().head(self.top_n).to_frame()
        top_skills.index.names = ['Ключевой навык']
        top_skills.columns = ['Число повторений']
        print('*'*30)
        print(f'ТОП-{self.top_n} ключевых навыков по Вашему запросу:')
        print(top_skills)


user_input = input(
    'Введите ключевое слово для желаемой профессии, чтобы узнать какие ключевые навыки хотят видеть работодатели\n')
num_pages_for_parse = int(input(
    'Какое количество страниц поиска по ключевому слову Вы желаете охватить?\n(одна страница - 50 вакансий)\n'))
top = int(input(
    'Топ-N. Сколько самых популярных ключевых навыков Вы хотите увидеть в результате?\n'))

main = KeySkillsSearch(user_input, num_pages_for_parse, top)
main.find_number_of_search_pages()
main.collect_vacancy_hrefs()
main.collect_keyskills_from_hrefs()
main.make_results()
