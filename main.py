from parser import Parser


source_url = "https://quotes.toscrape.com/"


if __name__ == "__main__":
    parser = Parser(source_url)

    print(parser.title)

    # Пример работы с данными авторов
    for i_author in parser.get_authors():
        print(i_author)
        #print(i_author.name) - получаем имя автора
        #print(i_author.born_date) - получаем дату рождения
        #print(i_author.born_location) - получаем место рождения
        #print(i_author.link_to_biography) - получаем ссылку на биографию
        #print(i_author.quotes) - получаем список цитат
        print("\n", "-"*40, "\n")

    # Пример работы со списком цитат
    for i_quote in parser.list_quotes:
        print(i_quote)
        #author = i_quote.author - получаем автора высказывания
        #print(author.name) - получаем имя автора
        #print(author.link_to_biography) - получаем ссылку на биографию автора

    # Записываем результаты парсинга в файл
    parser.writing_file()