from datetime import datetime
import json
import os
import sqlite3
import time
import unittest
from unittest.mock import patch
import main as m


class init_db(unittest.TestCase):
    def setUp(self):
        m.I.__init__()
        m.I.DB_NAME = 'test_case.db'

    def test_init_db_succ(self):
        self.assertEqual(m.init_db(), 1)

    def test_init_db_table_already_exist(self):
        connect = sqlite3.connect(m.I.DB_NAME)
        c = connect.cursor()
        c.execute('''CREATE TABLE MAIN
                 (ID      INT PRIMARY KEY   NOT NULL,
                 CHAT_ID              INT   NOT NULL,
                 NAME                TEXT   NOT NULL,
                 TIME                 INT   NOT NULL);''')
        c.execute("INSERT INTO MAIN (ID, CHAT_ID, NAME, TIME) VALUES (1, 2, 'Test Value 1', 4)")
        c.execute("INSERT INTO MAIN (ID, CHAT_ID, NAME, TIME) VALUES (5, 6, 'Test Value 2', 8)")
        connect.commit()
        connect.close()
        self.assertEqual(m.init_db(), 1)
        self.assertEqual(m.I.LAST_PRECIOUS, 2)

    def test_init_db_cant_create(self):
        m.I.DB_NAME = '//'
        self.assertEqual(m.init_db(), 0)
        self.assertEqual(m.I.LAST_PRECIOUS, 0)

    def tearDown(self):
        try:
            os.remove('test_case.db')
        except FileNotFoundError:
            ...


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
    def setUp(self):
        m.req = None

    @patch('__main__.m.get_json', return_value=json.loads('{"ok":"true"}'))
    def test_get_status_up(self, get_json):
        self.assertEqual(m.get_status(m.req), "true")

    @patch('__main__.m.get_json', return_value=json.loads('{"ok":"false"}'))
    def test_get_status_down(self, get_json):
        self.assertEqual(m.get_status(m.req), "false")


class echo(unittest.TestCase):
    def setUp(self):
        m.msg_date = datetime.fromtimestamp(946674000).strftime('%d.%m.%Y - %H:%M:%S')
        m.date = 946674000

    def test_echo_standart(self):
        temp = f'At {m.msg_date} user ... from ... post message #...:\n...\n{"="*70}'
        self.assertEqual(m.echo(date=m.date), temp)

    def test_echo_system(self):
        temp = (f'\x1b[0;31;40mAt {m.msg_date} user ... from ... post message #...:\n...\n{"="*70}\x1b[0m')
        warn = True
        self.assertEqual(m.echo(date=m.date, warn=warn), temp)

    def test_echo_all(self):
        temp = (f'\x1b[0;31;40mAt {m.msg_date} user msg_user from chat_id post message #msg_id:\nmsg_text\n{"="*70}\x1b[0m')
        id = 'msg_id'
        user = 'msg_user'
        chat = 'chat_id'
        msg = 'msg_text'
        warn = True
        self.assertEqual(m.echo(id, m.date, user, chat, msg, warn), temp)

if __name__ == '__main__':
    unittest.main()
