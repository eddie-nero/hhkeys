import aiohttp
import asyncio
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import csv
from datetime import datetime
from tqdm import tqdm


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


def get_html(url):
    my_headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }
    r = requests.get(url, headers=my_headers)
    if r.status_code == 200:
        return r.text


def get_links(url, pages):
    links = []
    for page in range(pages):
        target_url = url + str(page)
        soup = BeautifulSoup(get_html(target_url), 'lxml')
        for a in soup.find_all('a', href=True, attrs={'data-qa': 'vacancy-serp__vacancy-title'}):
            links.append(a['href'])
    return links


start = datetime.now()
key_skill = 'переводчик'
num_pages = 6
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
