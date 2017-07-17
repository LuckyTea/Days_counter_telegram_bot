from datetime import datetime
import os
import time
import unittest
from unittest.mock import patch
import main as m


class init_db(unittest.TestCase):
    def test_init_db_succ(self):
        m.I.DB_NAME = 'test_case.db'
        self.assertEqual(m.init_db(), 1)
        os.remove('test_case.db')

    def test_init_db_fail(self):
        m.I.DB_NAME = None
        self.assertEqual(m.init_db(), 0)


class action(unittest.TestCase):
    def test_action(self):
        req = 'https://api.telegram.org/bot'
        self.assertEqual(m.action(req), '{"ok":false,"error_code":404,"description":"Not Found"}')


class echo(unittest.TestCase):
    def test_echo_standart(self):
        date = datetime.fromtimestamp(1000000).strftime('%d.%m.%Y - %H:%M:%S')
        temp = f'At {date} user ... from ... post message #...:\n...\n{"="*70}'
        self.assertEqual(m.echo(date=1000000), temp)

    def test_echo_system(self):
        date = datetime.fromtimestamp(1000000).strftime('%d.%m.%Y - %H:%M:%S')
        temp = (f'\x1b[0;31;40mAt {date} user ... from ... post message #...:\n...\n{"="*70}\x1b[0m')
        self.assertEqual(m.echo(date=1000000, warn=True), temp)

    def test_echo_all(self):
        date = datetime.fromtimestamp(1000000).strftime('%d.%m.%Y - %H:%M:%S')
        temp = (f'\x1b[0;31;40mAt {date} user msg_user from chat_id post message #msg_id:\nmsg_text\n{"="*70}\x1b[0m')
        self.assertEqual(m.echo(id='msg_id', date=1000000, user='msg_user', chat='chat_id', msg='msg_text', warn=True), temp)

if __name__ == '__main__':
    unittest.main()
