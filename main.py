from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import time
import pandas as pd
import numpy as np
import re


user_request = str(input('Enter keyword\n'))
url = 'https://hh.ru/search/vacancy'

my_headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}

prefs = {"profile.managed_default_content_settings.images": 2,
         "profile.default_content_setting_values.notifications": 2,
         "profile.managed_default_content_settings.stylesheets": 2,
         "profile.managed_default_content_settings.cookies": 2,
         "profile.managed_default_content_settings.javascript": 1,
         "profile.managed_default_content_settings.plugins": 1,
         "profile.managed_default_content_settings.popups": 2,
         "profile.managed_default_content_settings.geolocation": 2,
         "profile.managed_default_content_settings.media_stream": 2,
         }

chrome_options = Options()
chrome_options.add_argument('--incognito')
chrome_options.add_argument('--headless')
chrome_options.add_argument(
    '--user-agent=""Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36""')
chrome_options.add_experimental_option('prefs', prefs)
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

chromedriver = Path('chromedriver', 'chromedriver.exe')

driver = webdriver.Chrome(executable_path=chromedriver, options=chrome_options)
driver.get(url)

element = driver.find_element(
    By.XPATH, '/html/body/div[5]/div[2]/div/div[1]/div/div/form/div/div[1]/div/input')

element.clear()
element.send_keys(user_request)
element.send_keys(Keys.ENTER)

soup = BeautifulSoup(driver.page_source, 'lxml')
num_of_vacs = soup.find('h1', class_='bloko-header-1').text
next_base_url = f'https://ryazan.hh.ru/search/vacancy?L_is_autosearch=false&clusters=true&enable_snippets=true&text={user_request}&page='
number_of_search_pages = driver.find_element(
    By.XPATH, '/html/body/div[6]/div/div[1]/div[2]/div/div[3]/div/div[2]/div/div[8]/div/span[3]/a').text
print('Найдено', num_of_vacs, 'на', number_of_search_pages, 'страницах')

vacancy_hrefs = []

for vac_page in range(1, 3):
    for a in soup.find_all('a', href=True, attrs={'data-qa': 'vacancy-serp__vacancy-title'}):
        vacancy_hrefs.append(a['href'])
    try:
        r = requests.get(f'{next_base_url}{vac_page}', headers=my_headers)
    except:
        time.sleep(5)
        r = requests.get(f'{next_base_url}{vac_page}', headers=my_headers)
    soup = BeautifulSoup(r.content, 'lxml')
print('Всего ссылок на вакансии:', len(vacancy_hrefs))
print('Начинаем вытаскивать скилы')

key_skills = []
key_skills_filename = f'keyskills_{user_request}_{time.time()}'
with open(f'{key_skills_filename}.txt', 'w', encoding='UTF-8') as outfile:
    for vacancy in vacancy_hrefs:
        try:
            req = requests.get(vacancy, headers=my_headers)
        except:
            time.sleep(5)
            req = requests.get(vacancy, headers=my_headers)
        vac_soup = BeautifulSoup(req.content, 'lxml')
        for key in vac_soup.find_all('span', attrs={'data-qa': 'bloko-tag__text'}):
            outfile.write(key.text)
            outfile.write('\n')

key_series = pd.read_csv(f'{key_skills_filename}.txt', sep='\n', header=None)
top_20_skills = key_series.value_counts().head(20).to_frame()
top_20_skills.index.names = ['Ключевой навык']
top_20_skills.columns = ['Число повторений']
print('*'*30)
print('ТОП-20 ключевых навыков по Вашему запросу:')
print(top_20_skills)
