"""4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в
байтовое и выполнить обратное преобразование (используя методы encode и decode)."""

my_lst = ['разработка', 'администрирование', 'protocol', 'standard']
result_lst = [el.encode('utf-8').decode('utf-8') for el in my_lst]

print(*result_lst)
