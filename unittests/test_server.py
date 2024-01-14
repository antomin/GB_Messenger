from unittest import TestCase

from common.variables import ACCOUNT_NAME, ACTION, ERROR, PRESENCE, RESPONSE, TIME, USER
from server import process_client_message


class ProcessClientMessage(TestCase):
    def setUp(self):
        self.dict_ok = {RESPONSE: 200}
        self.dict_error = {RESPONSE: 400, ERROR: "Bad request"}
        self.message = {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: "Guest"}}

    def test_correct_answer(self):
        self.assertEqual(process_client_message(self.message), self.dict_ok)

    def test_wrong_action(self):
        self.message[ACTION] = "wrong"
        self.assertEqual(process_client_message(self.message), self.dict_error)

    def test_no_action(self):
        del self.message[ACTION]
        self.assertEqual(process_client_message(self.message), self.dict_error)

    def test_no_time(self):
        del self.message[TIME]
        self.assertEqual(process_client_message(self.message), self.dict_error)

    def test_no_user(self):
        del self.message[USER]
        self.assertEqual(process_client_message(self.message), self.dict_error)
