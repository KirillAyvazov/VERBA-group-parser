from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Author:
    name: str
    link_to_biography: str
    born_date: Optional[str] = None
    born_location: Optional[str] = None
    quotes: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        """Метод представления объекта класса Author в строчном виде"""
        return "\n".join([f"Имя автора: {self.name}",
                          f"Дата рождения: {self.born_date}",
                          f"Место рождения: {self.born_location}",
                          f"Биография: {self.link_to_biography}",
                          "Цитаты:", *[i_quote.text for i_quote in self.quotes]])

    def add_quote(self, quote) -> None:
        """Метод добавляет новое изречение в список цитат автора"""
        self.quotes.append(quote)

    def get_dict(self) -> Dict[str, Any]:
        """Данный метод преобразует объект класса в словарь"""
        author_dict = {i_key: i_val for i_key, i_val in self.__dict__.items()}
        author_dict["quotes"] = [i_quotes.text for i_quotes in self.quotes]
        return author_dict

@dataclass
class Quote:
    text: str
    author: Author

    def __repr__(self) -> str:
        """Метод представления объекта класса Quote в строчном виде"""
        return " ".join([self.text, f"Author: {self.author.name}"])

