class IncorrectDataReceivedError(Exception):
    def __str__(self):
        return "Некорректное сообщение от удалённого компьютера"


class NonDictInputError(Exception):
    def __str__(self):
        return "Ожидается объект класса <dict>"


class ReqFieldMissingError(Exception):
    def __init__(self, missing_fields: list):
        self.missing_fields = missing_fields

    def __str__(self):
        return f'Отсутствуют обязательные поля: <{", ".join(self.missing_fields)}>'
