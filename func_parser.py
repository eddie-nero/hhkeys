from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime
import pandas as pd
import numpy as np
from tqdm import tqdm
import multiprocessing as mp


def get_html(url):
    my_headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }
    r = requests.get(url, headers=my_headers)
    if r.status_code == 200:
        return r.text


def get_links(url, n_pages):
    links = []
    for page in range(n_pages):
        target_url = url + str(page)
        soup = BeautifulSoup(get_html(target_url), 'lxml')
        for a in soup.find_all('a', href=True, attrs={'data-qa': 'vacancy-serp__vacancy-title'}):
            links.append(a['href'])
    return links


def get_skills(link):
    skills = []
    soup = BeautifulSoup(get_html(link), 'lxml')
    for key in soup.find_all('span', attrs={'data-qa': 'bloko-tag__text'}):
        skills.append(key.text)
    return skills


def make_results(keyskills, topN):
    df = pd.DataFrame(keyskills)
    top_skills = df.value_counts().head(topN).to_frame()
    top_skills.index.names = ['KeySkill']
    top_skills.columns = ['N_times']
    top_skills.reset_index(inplace=True)
    print(top_skills)


def main():
    start = datetime.now()
    keyskill = 'python'
    n_pages = 5
    topN = 5
    url = f'https://hh.ru/search/vacancy?L_is_autosearch=false&clusters=true&enable_snippets=true&text={keyskill}&page='

    all_links = get_links(url, n_pages)
    print(f'Собрано {len(all_links)} ссылок')

    num_workers = 15

    with mp.Pool(num_workers) as pool:
        all_skills = pool.map(get_skills, all_links)
    unpacked_keys = []
    for skills in all_skills:
        for key in skills:
            unpacked_keys.append(key)
    print(f'Собрано {len(unpacked_keys)} скилов')
    result = make_results(unpacked_keys, topN)

    end = datetime.now()
    print('Затрачено времени: ', end - start)


if __name__ == '__main__':
    main()
