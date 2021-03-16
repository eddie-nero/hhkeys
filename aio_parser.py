import aiohttp
import asyncio
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import time


class WebScraper(object):
    def __init__(self, urls):
        self.urls = urls
        # Global Place To Store The Data:
        self.all_data = []
        self.master_dict = {}
        # Run The Scraper:
        asyncio.run(self.main())

    async def fetch(self, session, url):
        try:
            async with session.get(url) as response:
                # 1. Extracting the Text:
                text = await response.text()
                # 2. Extracting the <title> </title> Tag:
                skills = await self.extract_key_skills(text)
                return text, url, skills
        except Exception as e:
            print(str(e))

    async def extract_key_skills(self, text):
        skills = []
        try:
            soup = BeautifulSoup(text, 'lxml')
            for key in soup.find_all('span', attrs={'data-qa': 'bloko-tag__text'}):
                skills.append(key.text)
            return skills
        except Exception as e:
            print(str(e))

    def return_skills_list(self):
        all_skills = []
        for url in self.master_dict.keys():
            all_skills.extend(self.master_dict[url]['Skills'])
        return all_skills

    async def main(self):
        tasks = []
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"}
        async with aiohttp.ClientSession(headers=headers) as session:
            for url in self.urls:
                tasks.append(self.fetch(session, url))
            htmls = await asyncio.gather(*tasks)
            self.all_data.extend(htmls)
            # Storing the raw HTML data.
            for html in htmls:
                if html is not None:
                    url = html[1]
                    self.master_dict[url] = {
                        'Skills': html[2]
                    }
                else:
                    continue


class LinkCollector(object):
    def __init__(self, keyskill, pages, top_n):
        self.my_headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
        }
        self.keyskill = keyskill
        self.base_url = f'https://hh.ru/search/vacancy?L_is_autosearch=false&clusters=true&enable_snippets=true&text={self.keyskill}&page='
        self.num_pages = pages
        self.top_n = top_n

    def get_html(self, url):
        r = requests.get(url, headers=self.my_headers)
        if r.status_code == 200:
            return r.text

    def get_links(self):
        url = self.base_url
        pages = self.num_pages
        links = []
        for page in range(pages):
            target_url = url + str(page)
            soup = BeautifulSoup(self.get_html(target_url), 'lxml')
            for a in soup.find_all('a', href=True, attrs={'data-qa': 'vacancy-serp__vacancy-title'}):
                links.append(a['href'])
        return links


def make_results(all_skills, top_n):
    df = pd.DataFrame(all_skills)
    top_skills = df.value_counts().head(top_n).to_frame()
    top_skills.index.names = ['KeySkill']
    top_skills.columns = ['N-times']
    top_skills.reset_index(inplace=True)
    return top_skills


def plot(df):

    def absolute_value(val):
        a = np.round(val/100*df.iloc[:, 1].sum(), 0)
        return int(a)
    filename = f'output_{time.time()}.png'
    labels = df.iloc[:, 0].to_list()
    fig1, ax1 = plt.subplots()
    ax1.pie(df.iloc[:, 1], labels=labels, autopct=absolute_value)
    ax1.axis('equal')
    ax1.get_figure().savefig(filename)
    return filename


if __name__ == '__main__':
    start = datetime.now()
    key_skill = 'переводчик'
    num_pages = 1
    base_url = f'https://hh.ru/search/vacancy?L_is_autosearch=false&clusters=true&enable_snippets=true&text={key_skill}&page='
    top_n = 10
    all_links = get_links(base_url, num_pages)
    scraper = WebScraper(all_links)
    all_skills = []
    for url in scraper.master_dict.keys():
        all_skills.extend(scraper.master_dict[url]['Skills'])
    df = pd.DataFrame(all_skills)
    top_skills = df.value_counts().head(top_n).to_frame()
    top_skills.index.names = ['KeySkill']
    top_skills.columns = ['N-times']
    top_skills.reset_index(inplace=True)
    print(top_skills)
    end = datetime.now()
    print(f'Времени затрачено: {end - start}')
