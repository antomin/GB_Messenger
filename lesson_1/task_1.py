"""1. Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате и проверить тип и содержание
соответствующих переменных. Затем с помощью онлайн-конвертера преобразовать строковые представление в формат Unicode и
также проверить тип и содержимое переменных."""


my_lst = ['разработка', 'сокет', 'декоратор']

for el in my_lst:
    print(el, type(el))

my_unicode_lst = [
    '\u0440\u0430\u0437\u0440\u0430\u0431\u043E\u0442\u043A\u0430',
    '\u0441\u043E\u043A\u0435\u0442',
    '\u0434\u0435\u043A\u043E\u0440\u0430\u0442\u043E\u0440'
]

for el in my_unicode_lst:
    print(el, type(el))
