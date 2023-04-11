"""5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтовового в строковый тип на
кириллице."""

import subprocess

sites = ['yandex.ru', 'youtube.com']

for site in sites:
    response = subprocess.Popen(['ping', '-c', '5', site], stdout=subprocess.PIPE)
    for line in response.stdout:
        print(line.decode('utf-8'), end='')
