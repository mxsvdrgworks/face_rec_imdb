import json
import os
import time        
import aiohttp
import asyncio
import requests
from pprint import pprint
from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent
from parser.parser_webdriver import ParseWebDriver
from config import Imdb


class ParseImdb:
    """
    class which is dedicated to produce 
    """
    def __init__(self) -> None:
        self.driver = None
        self.webdriver_path = ParseWebDriver().produce_webdriver_values()
        
    def set_webdrivers_options(self) -> None:
        """
        Method which is dedicated to create options of the webdriver
        Input:  None
        Output: we developed options to this
        """
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless")
        self.options.add_argument(f"user-agent={UserAgent().random}")

    def set_webdriver(self) -> None:
        """
        Method which is dedicated to create webdriver in all cases
        Input:  None
        Output: we created webdriver with randomized options
        """
        self.set_webdrivers_options()
        self.driver = webdriver.Chrome(self.webdriver_path, options=self.options)

    def remove_webdriver(self) -> None:
        """
        Method which is dedicated to create webdriver in all cases
        Input:  None
        Output: we created webdriver
        """
        self.driver.close()
        self.driver.quit()

    @staticmethod
    async def check_number(number:int) -> str:
        """
        Static method which is dedicated to check numbers
        Input:  number = number of values which was previously created
        Output: we returned number as a string
        """
        return str(number) if isinstance(number, int) or isinstance(number, float) \
                or not isinstance(number, str) else number

    async def produce_html_values(self, session:object, link:str) -> str:
        """
        Method which is dedicated to work with html values
        Input:  session = session which was previously developed
                link = link value which is required to work with
        Output: html value which is dedic
        """
        async with session.get(link, headers={'user-agent': UserAgent().random,}) as r:
            if r.status == 200:
                return await r.text()
            return link

    async def produce_html_response(self, link:str) -> str:
        r = requests.get(link)
        if r.status_code == 200:
            return r.text
        return link

    async def produce_html_parsing(self, html:str, value_link:str) -> dict:
        """
        Method which is dedicated to produce values of the actor/actress differentiating from it
        Input:  html = html which was previously parsed from it
                value_link = link value which was previously parsed
        Output: we successfully parsed values from the page as a dictionary
        """
        value_dict = {'link': value_link}
        if len(html) < 1000:
            return value_dict
        try:
            soup = BeautifulSoup(html, 'html.parser')
            soup = soup.find("script", type="application/ld+json")
            value_dict = json.loads(soup.text)
        except Exception as e:
            print(e)
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        return value_dict

    @staticmethod
    async def produce_value_links(number:str) -> str:
        """
        Static method which is dedicated to produce values
        Input:  number = number which is requited to work with
        Output: we created link value for developing new values of it
        """
        def produce_number(number):
            if len(number) >= 7:
                return number
            number = ''.join(['0' for _ in range(7 - len(number))]) + number
            return number
        number = produce_number(number)
        return '/'.join([Imdb.link, Imdb.link_name, f'{Imdb.link_name_add}{number}'])

    async def produce_main(self, numbers:list) -> list:
        """
        Method which is dedicated to produce values of the actors and get all of their information
        Input:  numbers = numbers of IDs of the Kinopoisk which possibly could be used as a parsing
        Output: we created lists of the dictionaries and developed the database for it
        """
        numbers = [asyncio.create_task(self.check_number(number)) for number in numbers]
        numbers = await asyncio.gather(*numbers)

        tasks = [asyncio.create_task(self.produce_value_links(number)) for number in numbers]
        links = await asyncio.gather(*tasks)
        semaphore = asyncio.Semaphore(Imdb.semaphore)
        async with semaphore:
            async with aiohttp.ClientSession(trust_env=True) as session:
                tasks = [asyncio.create_task(self.produce_html_values(session, link)) for link in links]
                htmls = await asyncio.gather(*tasks)
        tasks = [asyncio.create_task(self.produce_html_parsing(html, link)) for html, link in zip(htmls, links)]
        return await asyncio.gather(*tasks)