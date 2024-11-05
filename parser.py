from typing import Optional, List, Dict
from logging import getLogger, basicConfig
import asyncio
import os
import json

import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import aiohttp

from models import Author, Quote


basicConfig(level="WARNING", format="%(asctime)s - %(levelname)s - %(message)s")
logger = getLogger(__name__)


class Parser:
    """
        Класс - модель парсера web-сайта https://quotes.toscrape.com/
        Объект данного класса позволяет получить список авторов цитат, список цитат, а так же формирует документ
    quotes_from_great_people.md с результатами парсинга сайта

    Parameters:
        url: str - для инициализации объекта парсера, в конструктор класса необходимо передать url сайта, который нужно
            парсить

    Attributes:
        title: str - заголовок распарсенного сайта
        list_quotes: List[Quote] - список цитат полученных из распарсенного сайта
        url: str - url сайта, заданный при инициализации объекта парсера

    Methods:
        get_authors -> List[Author]
            Метод возвращает список авторов, полученных с распарсенного сайта
    """
    def __init__(self, url: str) -> None:
        """Метод инициализации атрибутов класса - составная часть конструктора класса"""
        self.__url: str = url
        self.title: Optional[str] = None
        self.list_quotes: List[Quote] = list()
        self.__list_authors: Dict[str, Author] = dict()
        self.__file_path = "result_parsing.json"

        self.__parsing()
        asyncio.run(self.__get_content())

    @property
    def url(self):
        """
            Геттер атрибута url, позволяющий получить переданный в конструктор класса url и защищающий его от случайных
        изменений
        """
        return self.__url

    def __add_author(self, author: Author) -> Author:
        """Метод добавляет объект автора в хранилище данных об авторах"""
        if author.name in self.__list_authors.keys():
            return self.__list_authors.get(author.name)

        self.__list_authors[author.name] = author
        return author

    def get_authors(self) -> List[Author]:
        """Метод предоставляет доступ к списку авторов"""
        return list(self.__list_authors.values())

    @classmethod
    def __execute_request(cls, url: str) -> Optional[str]:
        """Метод осуществляет get запрос к источнику информации по указанному url"""
        try:
            response = requests.get(url)

            if response.status_code == 200:
                return response.text

            logger.warning(f"Не удалось получить ответ от ресурса {url}, статус код {response.status_code}")

        except RequestException as ex:
            logger.exception(f"При осуществлении запроса к ресурсу {url} произошла ошибка", exc_info=ex)

    @classmethod
    def __combining_url(cls, base_url: str, prefix: str) -> str:
        """Вспомогательный метод, который позволяет корректно объединить базовую часть url с его префиксом"""
        if base_url.endswith("/"):
            sep = ""
        else:
            sep = "/"

        return sep.join([base_url, prefix])

    def __parsing(self) -> None:
        """Метод выполняет парсинг полученной из метода __execute_request html страницы"""
        html_page: str = self.__execute_request(self.url)

        if html_page:
            soup = BeautifulSoup(html_page, "html5lib")
            self.title = soup.h1.text

            blocks = soup.findAll("div", {"class": "quote"})

            for i_blocks in blocks:
                author_name = i_blocks.small.text
                quote_text = i_blocks.find("span").text
                link_to_biography = self.__combining_url(self.url, i_blocks.a.attrs["href"])

                author = Author(name=author_name, link_to_biography=link_to_biography)
                author = self.__add_author(author)

                quote = Quote(text=quote_text, author=author)
                self.list_quotes.append(quote)

                author.add_quote(quote)

    @classmethod
    async def __parsing_author_data(cls, html_page: str):
        soup = BeautifulSoup(html_page, "html5lib")
        born_date = soup.find("span", {"class": "author-born-date"}).text
        born_location = soup.find("span", {"class": "author-born-location"}).text
        return born_date, born_location


    async def __get_birth_data(self, client: aiohttp.ClientSession, author: Author) -> None:
        """Данный метод осуществляет получение даты и места рождения автора"""
        async with client.get(author.link_to_biography) as response:
            data = await response.read()
            born_date, born_location = await self.__parsing_author_data(data)
            author.born_date = born_date
            author.born_location = born_location

    async def __get_content(self) -> None:
        """Данный метод инициализирует получение данных об авторах в асинхронном режиме"""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(5)) as client:
            await asyncio.gather(*[self.__get_birth_data(client, i_author)
                                  for i_author in list(self.__list_authors.values())])

    def writing_file(self) -> None:
        """Метод записывает результаты парсинга в файл"""
        if os.path.exists(self.__file_path):
            os.remove(self.__file_path)

        result = [i_author.get_dict() for i_author in self.get_authors()]

        with open(self.__file_path, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4)
