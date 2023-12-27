from unittest import TestCase

from client import process_answer, create_presence
from common.variables import RESPONSE, ERROR, ACTION, PRESENCE, USER, ACCOUNT_NAME, TIME


class TestProcessAnswer(TestCase):
    def setUp(self):
        self.answer_200 = {RESPONSE: 200}
        self.answer_400 = {RESPONSE: 400, ERROR: 'Bad request'}
        self.wrong_answer = {ERROR, 'Bad request'}

    def test_answer_200(self):
        self.assertEqual(process_answer(self.answer_200), '200 : OK')

    def test_answer_200_wrong(self):
        self.assertNotEqual(process_answer(self.answer_200), 'wrong')

    def test_answer_400(self):
        self.assertEqual(process_answer(self.answer_400), '400 : Bad request')

    def test_answer_400_wrong(self):
        self.assertNotEqual(process_answer(self.answer_400), 'wrong')

    def test_wrong_answer(self):
        self.assertRaises(ValueError, process_answer, self.wrong_answer)


class TestCreatePresence(TestCase):
    def setUp(self):
        self.time = 1.1
        self.account_name = 'TestUser'

    def test_default_presence(self):
        presence = create_presence()
        presence[TIME] = self.time
        self.assertEqual(presence, {ACTION: PRESENCE, TIME: self.time, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_presence(self):
        presence = create_presence(account_name=self.account_name)
        presence[TIME] = self.time
        self.assertEqual(presence, {ACTION: PRESENCE, TIME: self.time, USER: {ACCOUNT_NAME: self.account_name}})
