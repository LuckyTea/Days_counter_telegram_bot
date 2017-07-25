import datetime
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

    def tearDown(self):
        try:
            os.remove('test_case.db')
        except FileNotFoundError:
            ...

    def test_init_db_succ(self):
        self.assertEqual(m.init_db(), 1)

    def test_init_db_table_already_exist(self):
        connect = sqlite3.connect(m.I.DB_NAME)
        c = connect.cursor()
        c.execute('''CREATE TABLE MAIN
                 (ID      INT PRIMARY KEY   NOT NULL,
                 CHAT_ID              INT   NOT NULL,
                 NAME                TEXT   NOT NULL,
                 TIME                TEXT   NOT NULL);''')
        c.execute("INSERT INTO MAIN (ID, CHAT_ID, NAME, TIME) VALUES (1, 2, 'Test Value 1', '01.01.1970')")
        c.execute("INSERT INTO MAIN (ID, CHAT_ID, NAME, TIME) VALUES (5, 6, 'Test Value 2', '02.02.1970')")
        connect.commit()
        connect.close()
        self.assertEqual(m.init_db(), 1)
        self.assertEqual(m.I.LAST_PRECIOUS, 2)

    @patch('__main__.m.echo', return_value=...)
    def test_init_db_cant_create(self, no_print):
        m.I.DB_NAME = '//'
        self.assertEqual(m.init_db(), 0)
        self.assertEqual(m.I.LAST_PRECIOUS, 0)


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


@patch('__main__.m.echo', return_value='')
class handle_msg(unittest.TestCase):
    def setUp(self):
        m.I.__init__()

    def generate_msg(edit=False, wtf=False, sticker=False, case='Show must go on!'):
        msg = json.loads('''
            {"ok": "True",
            "result": [{
                "update_id": 0,
                "message": {
                    "message_id": 41,
                    "from": {
                        "id": 24101991,
                        "first_name": "Freddie",
                        "last_name": "Mercury",
                        "username": "MrBadGuy",
                        "language_code": "en-US"\
                    },
                    "chat": {
                        "id": 24101991,
                        "first_name": "Freddie",
                        "last_name": "Mercury",
                        "username": "MrBadGuy",
                        "type": "private"
                    },
                    "date": 688251600,
                    "text": ""
                },
                "edited_message": {
                    "message_id": 41,
                    "from": {
                        "id": 24101991,
                        "first_name": "Freddie",
                        "last_name": "Mercury",
                        "username": "MrBadGuy",
                        "language_code": "en-US"\
                    },
                    "chat": {
                        "id": 24101991,
                        "first_name": "Freddie",
                        "last_name": "Mercury",
                        "username": "MrBadGuy",
                        "type": "private"
                    },
                    "date": 688251600,
                    "text": ""}
                }
            ]}''')
        if edit:
            del msg['result'][0]['message']
            msg['result'][0]['edited_message']['text'] = case
        elif wtf:
            del msg['result'][0]['message']['text']
        elif sticker:
            del msg['result'][0]['message']['text']
            msg['result'][0]['message']['sticker'] = {'emoji': case}
        else:
            msg['result'][0]['message']['text'] = case
        return msg

    def test_handle_msg_parse_edited_message(self, no_print):
        self.assertEqual(m.handle_msg(handle_msg.generate_msg(edit=True, case='test msg'), 0), 1)
        self.assertEqual(m.I.LAST_ID, 1)

    def test_handle_msg_parse_standart_message(self, no_print):
        self.assertEqual(m.handle_msg(handle_msg.generate_msg(case='test msg'), 0), 1)
        self.assertEqual(m.I.LAST_ID, 1)

    def test_handle_msg_parse_sticker_message(self, no_print):
        self.assertEqual(m.handle_msg(handle_msg.generate_msg(sticker=True, case='🏁'), 0), 1)
        self.assertEqual(m.I.LAST_ID, 1)

    def test_handle_msg_parse_wtf_message(self, no_print):
        self.assertEqual(m.handle_msg(handle_msg.generate_msg(wtf=True, case='test msg'), 0), 1)
        self.assertEqual(m.I.LAST_ID, 1)

    @patch('__main__.m.get_updates', return_value='')
    @patch('__main__.m.send_msg', return_value='')
    def test_handle_msg_call_bot_stop(self, get_updates, send_msg, no_print):
        m.I.OWNER_ID = 24101991
        self.assertEqual(m.handle_msg(handle_msg.generate_msg(case='/bot_stop'), 0), 0)
        self.assertEqual(m.I.LAST_ID, 1)

    @patch('__main__.m.counting_start', return_value='counting_start')
    def test_handle_msg_call_counting_start_succ(self, counting_start, no_print):
        self.assertEqual(m.handle_msg(handle_msg.generate_msg(case='!bot start counting for smth'), 0), 'counting_start')
        self.assertEqual(m.I.LAST_ID, 1)

    @patch('__main__.m.send_msg', return_value='send_msg')
    def test_handle_msg_call_counting_start_msg_too_long(self, counting_start, no_print):
        self.assertEqual(m.handle_msg(handle_msg.generate_msg(case=f'!bot start counting for {"smth"*100}'), 0), 'send_msg')
        self.assertEqual(m.I.LAST_ID, 1)

    @patch('__main__.m.counting_show', return_value='counting_show')
    def test_handle_msg_call_counting_show(self, counting_show, no_print):
        self.assertEqual(m.handle_msg(handle_msg.generate_msg(case='!bot show smt'), 0), 'counting_show')
        self.assertEqual(m.I.LAST_ID, 1)

    @patch('__main__.m.counting_reset', return_value='counting_reset')
    def test_handle_msg_call_counting_reset(self, counting_reset, no_print):
        self.assertEqual(m.handle_msg(handle_msg.generate_msg(case='!bot reset smth'), 0), 'counting_reset')
        self.assertEqual(m.I.LAST_ID, 1)

    @patch('__main__.m.counting_delete', return_value='counting_delete')
    def test_handle_msg_call_counting_delete(self, counting_delete, no_print):
        self.assertEqual(m.handle_msg(handle_msg.generate_msg(case='!bot delete smth'), 0), 'counting_delete')
        self.assertEqual(m.I.LAST_ID, 1)

    @patch('__main__.m.send_help', return_value='send_help')
    def test_handle_msg_call_help(self, send_help, no_print):
        self.assertEqual(m.handle_msg(handle_msg.generate_msg(case='!bot help'), 0), 'send_help')
        self.assertEqual(m.I.LAST_ID, 1)


@patch('__main__.m.print', return_value=...)
class echo(unittest.TestCase):
    def setUp(self):
        m.msg_date = datetime.datetime.fromtimestamp(946674000).strftime('%d.%m.%Y - %H:%M:%S')
        m.date = 946674000

    def test_echo_standart(self, no_print):
        temp = f'At {m.msg_date} user ... from ... post message #...:\n...\n{"="*70}'
        self.assertEqual(m.echo(date=m.date), temp)

    def test_echo_system(self, no_print):
        temp = (f'\x1b[0;31;40mAt {m.msg_date} user ... from ... post message #...:\n...\n{"="*70}\x1b[0m')
        warn = True
        self.assertEqual(m.echo(date=m.date, warn=warn), temp)

    def test_echo_all(self, no_print):
        temp = (f'\x1b[0;31;40mAt {m.msg_date} user msg_user from chat_id post message #msg_id:\nmsg_text\n{"="*70}\x1b[0m')
        id = 'msg_id'
        user = 'msg_user'
        chat = 'chat_id'
        msg = 'msg_text'
        warn = True
        self.assertEqual(m.echo(id, m.date, user, chat, msg, warn), temp)


class counting_start(unittest.TestCase):
    def setUp(self):
        m.I.__init__()
        m.I.DB_NAME = 'test_case.db'
        m.chat_id = 24101991
        m.msg_date = 688251600  # 24.10.1991

    def tearDown(self):
        try:
            os.remove('test_case.db')
        except FileNotFoundError:
            ...

    def test_counting_start_lazy(self):
        m.init_db()
        msg = '!bot start counting for lazy'
        connect = sqlite3.connect(m.I.DB_NAME)
        c = connect.cursor()
        c.execute("INSERT INTO MAIN (ID, CHAT_ID, NAME, TIME) VALUES (0, 24101991, 'block lazy', '01.01.1970')")
        connect.commit()
        connect.close()
        m.counting_start(m.chat_id, m.msg_date, msg)
        connect = sqlite3.connect(m.I.DB_NAME)
        c = connect.cursor()
        c.execute('SELECT * FROM MAIN')
        result = c.fetchall()
        connect.close()
        self.assertEqual(result, [(0, 24101991, 'block lazy', '01.01.1970'), (1, 24101991, 'lazy', datetime.datetime.strftime(datetime.datetime.fromtimestamp(m.msg_date), '%d.%m.%Y'))])

    def test_counting_start_word(self):
        m.init_db()
        words = ('now', 'today', 'tomorrow', 'yesterday')
        for i in words:
            msg = f'!bot start counting since {i} for {i}'
            m.counting_start(m.chat_id, m.msg_date, msg)
        connect = sqlite3.connect(m.I.DB_NAME)
        c = connect.cursor()
        c.execute('SELECT * FROM MAIN')
        result = c.fetchall()
        connect.close()
        date = datetime.datetime.strptime(datetime.datetime.strftime(datetime.datetime.fromtimestamp(m.msg_date), '%d.%m.%Y'), '%d.%m.%Y')
        self.assertEqual(result, [(0, 24101991, 'now', date.strftime('%d.%m.%Y')),
                                  (1, 24101991, 'today', date.strftime('%d.%m.%Y')),
                                  (2, 24101991, 'tomorrow', (date + datetime.timedelta(days=1)).strftime('%d.%m.%Y')),
                                  (3, 24101991, 'yesterday', (date - datetime.timedelta(days=1)).strftime('%d.%m.%Y'))])
        self.assertEqual(m.I.LAST_PRECIOUS, 4)

    def test_counting_start_date(self):
        m.init_db()
        msg = '!bot start counting since 24.10.1991 for 24.10.1991'
        m.counting_start(m.chat_id, m.msg_date, msg)
        connect = sqlite3.connect(m.I.DB_NAME)
        c = connect.cursor()
        c.execute('SELECT * FROM MAIN')
        result = c.fetchall()
        connect.close()
        self.assertEqual(result, [(0, 24101991, '24.10.1991', '24.10.1991')])
        self.assertEqual(m.I.LAST_PRECIOUS, 1)

    def test_counting_start_fail(self):
        m.init_db()
        msg = '!bot start counting and show'
        m.counting_start(m.chat_id, m.msg_date, msg)
        self.assertEqual(m.I.LAST_PRECIOUS, 0)


@patch('__main__.m.print', return_value=...)
class counting_show(unittest.TestCase):
    def setUp(self):
        m.I.__init__()
        m.I.DB_NAME = 'test_case.db'
        m.chat_id = 24101991
        m.msg_date = 688251600  # 24.10.1991

    def tearDown(self):
        try:
            os.remove('test_case.db')
        except FileNotFoundError:
            ...

    def test_counting_show_all(self, no_print):
        m.init_db()
        connect = sqlite3.connect(m.I.DB_NAME)
        c = connect.cursor()
        c.execute("INSERT INTO MAIN (ID, CHAT_ID, NAME, TIME) VALUES (?, ?, ?, ?)", (0, m.chat_id, 'smth', '01.01.1970'))
        c.execute("INSERT INTO MAIN (ID, CHAT_ID, NAME, TIME) VALUES (?, ?, ?, ?)", (1, m.chat_id, 'smth', '01.01.3000'))
        connect.commit()
        connect.close()
        self.assertEqual(m.counting_show(m.chat_id, m.msg_date, 'all'), 1)

    def test_counting_show_all_fail(self, no_print):
        m.init_db()
        self.assertEqual(m.counting_show(m.chat_id, m.msg_date, 'all'), 0)

    def test_counting_show_smt(self, no_print):
        m.init_db()
        connect = sqlite3.connect(m.I.DB_NAME)
        c = connect.cursor()
        c.execute("INSERT INTO MAIN (ID, CHAT_ID, NAME, TIME) VALUES (?, ?, ?, ?)", (0, m.chat_id, 'smth', '24.10.1991'))
        connect.commit()
        connect.close()
        self.assertEqual(m.counting_show(m.chat_id, m.msg_date, 'smth'), 1)

    def test_counting_show_smt_fail(self, no_print):
        m.init_db()
        self.assertEqual(m.counting_show(m.chat_id, m.msg_date, 'smth'), 0)

    def test_show_smt_future(self, no_print):
        m.init_db()
        connect = sqlite3.connect(m.I.DB_NAME)
        c = connect.cursor()
        c.execute("INSERT INTO MAIN (ID, CHAT_ID, NAME, TIME) VALUES (?, ?, ?, ?)", (0, m.chat_id, 'smth', '01.01.3000'))
        connect.commit()
        connect.close()
        self.assertEqual(m.counting_show(m.chat_id, m.msg_date, 'smth'), 1)

    def test_counting_show_looooong(self, no_print):
        m.init_db()
        connect = sqlite3.connect(m.I.DB_NAME)
        c = connect.cursor()
        for i in range(100):
            c.execute("INSERT INTO MAIN (ID, CHAT_ID, NAME, TIME) VALUES (?, ?, ?, ?)", (i, m.chat_id, f'{i*150}', '24.10.1991'))
        connect.commit()
        connect.close()
        self.assertEqual(m.counting_show(m.chat_id, m.msg_date, 'all'), 1)


@patch('__main__.m.print', return_value=...)
class counting_reset(unittest.TestCase):
    def setUp(self):
        m.I.__init__()
        m.I.DB_NAME = 'test_case.db'
        m.chat_id = 24101991
        m.msg_date = 688251600  # 24.10.1991

    def tearDown(self):
        try:
            os.remove('test_case.db')
        except FileNotFoundError:
            ...

    def test_counting_reset_succ(self, no_print):
        m.init_db()
        connect = sqlite3.connect(m.I.DB_NAME)
        c = connect.cursor()
        c.execute("INSERT INTO MAIN (ID, CHAT_ID, NAME, TIME) VALUES (?, ?, ?, ?)", (0, m.chat_id, 'reset', '24.10.1991'))
        connect.commit()
        m.counting_reset(m.chat_id, m.msg_date, 'reset')
        c.execute('SELECT * FROM MAIN')
        result = c.fetchall()
        connect.close()
        self.assertEqual(result, [(0, 24101991, 'reset',  datetime.datetime.strftime(datetime.datetime.fromtimestamp(m.msg_date), '%d.%m.%Y'))])

    def test_counting_reset_fail(self, no_print):
        m.init_db()
        connect = sqlite3.connect(m.I.DB_NAME)
        c = connect.cursor()
        c.execute("INSERT INTO MAIN (ID, CHAT_ID, NAME, TIME) VALUES (?, ?, ?, ?)", (0, m.chat_id, 'reset', '24.10.1991'))
        connect.commit()
        m.counting_reset(m.chat_id, m.msg_date, 'reset fail')
        c.execute('SELECT * FROM MAIN')
        result = c.fetchall()
        connect.close()
        self.assertEqual(result, [(0, 24101991, 'reset', '24.10.1991')])


@patch('__main__.m.print', return_value=...)
class counting_delete(unittest.TestCase):
    def setUp(self):
        m.I.__init__()
        m.I.DB_NAME = 'test_case.db'
        m.chat_id = 24101991
        m.msg_date = 688251600  # 24.10.1991

    def tearDown(self):
        try:
            os.remove('test_case.db')
        except FileNotFoundError:
            ...

    def test_counting_delete_succ(self, no_print):
        m.init_db()
        connect = sqlite3.connect(m.I.DB_NAME)
        c = connect.cursor()
        c.execute("INSERT INTO MAIN (ID, CHAT_ID, NAME, TIME) VALUES (?, ?, ?, ?)", (0, m.chat_id, 'delete', '24.10.1991'))
        connect.commit()
        m.counting_delete(m.chat_id, m.msg_date, 'delete')
        c.execute('SELECT * FROM MAIN')
        result = c.fetchall()
        connect.close()
        self.assertEqual(result, [])

    def test_counting_delete_succ_future(self, no_print):
        m.init_db()
        connect = sqlite3.connect(m.I.DB_NAME)
        c = connect.cursor()
        c.execute("INSERT INTO MAIN (ID, CHAT_ID, NAME, TIME) VALUES (?, ?, ?, ?)", (0, m.chat_id, 'delete', '24.10.3000'))
        connect.commit()
        m.counting_delete(m.chat_id, m.msg_date, 'delete')
        c.execute('SELECT * FROM MAIN')
        result = c.fetchall()
        connect.close()
        self.assertEqual(result, [])

    def test_counting_delete_fail(self, no_print):
        m.init_db()
        m.counting_delete(m.chat_id, m.msg_date, 'delete')

if __name__ == '__main__':
    unittest.main()
