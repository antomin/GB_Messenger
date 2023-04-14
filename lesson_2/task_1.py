"""Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных из файлов
info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV. Для этого:

    a. Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и считывание
    данных. В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров
    «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения каждого параметра поместить в
    соответствующий список. Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list,
    os_type_list. В этой же функции создать главный список для хранения данных отчета — например, main_data — и
    поместить в него названия столбцов отчета в виде списка: «Изготовитель системы», «Название ОС», «Код продукта»,
    «Тип системы». Значения для этих столбцов также оформить в виде списка и поместить в файл main_data (также для
    каждого файла);

    b. Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать получение данных
    через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;

    c. Проверить работу программы через вызов функции write_to_csv()."""

import csv
import re

FILES = ['info_1.txt', 'info_2.txt', 'info_3.txt']


def get_data(files):
    main_data = [['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']]
    os_prod_list, os_name_list, os_code_list, os_type_list = [], [], [], []

    for file_name in files:
        with open(file_name, 'r', encoding='cp1251') as file:
            data = file.read()
            os_prod_list.append(re.findall(r'(?<=Изготовитель системы:).*', data)[0].strip())
            os_name_list.append(re.findall(r'(?<=Название ОС:).*', data)[0].strip())
            os_code_list.append(re.findall(r'(?<=Код продукта:).*', data)[0].strip())
            os_type_list.append(re.findall(r'(?<=Тип системы:).*', data)[0].strip())

    for i in range(len(FILES)):
        main_data.append([os_prod_list[i], os_name_list[i], os_code_list[i], os_type_list[i]])

    return main_data


def write_to_csv(file_name):
    data = get_data(FILES)
    with open(file_name, 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)


write_to_csv('result.csv')
