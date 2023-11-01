"""6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет»,
«декоратор». Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести его
содержимое."""


my_lst = ['сетевое программирование', 'сокет', 'декоратор']

with open('task_6.txt', 'w',  encoding='utf-8') as file:
    for line in my_lst:
        file.write(line + '\n')

with open('task_6.txt', 'r', encoding='utf-8') as file:
    for line in file:
        print(line, end='')
