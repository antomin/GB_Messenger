"""3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе."""


my_lst = ['attribute', 'класс', 'функция', 'type']
error_lst = []

for el in my_lst:
    try:
        bytes(el, 'ascii')
    except UnicodeEncodeError:
        error_lst.append(el)

print(*error_lst)
