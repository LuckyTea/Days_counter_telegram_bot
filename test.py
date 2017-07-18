from datetime import datetime
import json
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


class get_json(unittest.TestCase):
    @patch('__main__.m.action', return_value='{"ok":"true"}')
    def test_get_json(self, action):
        req = None
        self.assertEqual(m.get_json(req), json.loads('{"ok":"true"}'))


class get_status(unittest.TestCase):
    @patch('__main__.m.get_json', return_value=json.loads('{"ok":"true"}'))
    def test_get_status_up(self, get_json):
        req = None
        self.assertEqual(m.get_status(req), "true")

    @patch('__main__.m.get_json', return_value=json.loads('{"ok":"false"}'))
    def test_get_status_down(self, get_json):
        req = None
        self.assertEqual(m.get_status(req), "false")


class echo(unittest.TestCase):
    def test_echo_standart(self):
        msg_date = datetime.fromtimestamp(1000000).strftime('%d.%m.%Y - %H:%M:%S')
        temp = f'At {msg_date} user ... from ... post message #...:\n...\n{"="*70}'
        date = 1000000
        self.assertEqual(m.echo(date=date), temp)

    def test_echo_system(self):
        msg_date = datetime.fromtimestamp(1000000).strftime('%d.%m.%Y - %H:%M:%S')
        temp = (f'\x1b[0;31;40mAt {msg_date} user ... from ... post message #...:\n...\n{"="*70}\x1b[0m')
        date = 1000000
        warn = True
        self.assertEqual(m.echo(date=date, warn=warn), temp)

    def test_echo_all(self):
        msg_date = datetime.fromtimestamp(1000000).strftime('%d.%m.%Y - %H:%M:%S')
        temp = (f'\x1b[0;31;40mAt {msg_date} user msg_user from chat_id post message #msg_id:\nmsg_text\n{"="*70}\x1b[0m')
        id = 'msg_id'
        date = 1000000
        user = 'msg_user'
        chat = 'chat_id'
        msg = 'msg_text'
        warn = True
        self.assertEqual(m.echo(id, date, user, chat, msg, warn), temp)

if __name__ == '__main__':
    unittest.main()
