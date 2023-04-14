"""Задание на закрепление знаний по модулю yaml. Написать скрипт, автоматизирующий сохранение данных в файле
YAML-формата. Для этого:

    a. Подготовить данные для записи в виде словаря, в котором первому ключу соответствует список, второму — целое
    число, третьему — вложенный словарь, где значение каждого ключа — это целое число с юникод-символом, отсутствующим в
    кодировке ASCII (например, €);

    b. Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml. При этом обеспечить стилизацию
    файла с помощью параметра default_flow_style, а также установить возможность работы с юникодом: allow_unicode =
    True;

    c. Реализовать считывание данных из созданного файла и проверить, совпадают ли они с исходными."""

import yaml

FILE_NANE = 'task_3.yaml'
MY_DICT = {1: ['1-1', '2-2'], 2: 22, 3: {'euro': '€', 'ruble': '₽'}}


def create_file(data):
    with open(FILE_NANE, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True, default_flow_style=False)


def check_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.SafeLoader)

    print(data == MY_DICT)


create_file(MY_DICT)
check_file(FILE_NANE)
