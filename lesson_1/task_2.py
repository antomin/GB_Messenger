"""2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность
кодов (не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных."""


my_lst = [b'class', b'function', b'method']

for el in my_lst:
    print(type(el), el, len(el))
