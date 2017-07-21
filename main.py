'''
Days since telegram bot
Can count days since smth, for example - last jewish tricks
'''

from datetime import datetime
import json
import re
import requests
import sqlite3
import sys
import time
import urllib


class Init():
    def __init__(self):
        import config
        self.HOST = f'https://api.telegram.org/bot{config.token}'
        self.LAST_ID = None
        self.LAST_PRECIOUS = 0
        self.OWNER_ID = config.owner_id
        self.DB_NAME = config.db_name


def main():
    echo(msg='Good day, sir!', warn=True)
    if not get_status(req=f'{I.HOST}/getMe'):
        return echo(msg='Bot is down', warn=True)
    if not init_db():
        return echo(msg='Can\'t initialize DB', warn=True)
    echo(msg=f'Now in DB {I.LAST_PRECIOUS} records\nBot work well. Getting messages...', warn=True)
    run = 1
    while run is 1:
        msg = get_updates(offset=I.LAST_ID)
        if len(msg["result"]) > 0:
            for last_update in range(len(msg['result'])):
                if handle_msg(msg, last_update) is 0:
                    run = 0
        time.sleep(0.5)


def init_db():
    try:
        connect = sqlite3.connect(I.DB_NAME)
        c = connect.cursor()
        try:
            c.execute('''CREATE TABLE MAIN
                     (ID      INT PRIMARY KEY   NOT NULL,
                     CHAT_ID              INT   NOT NULL,
                     NAME                TEXT   NOT NULL,
                     TIME                 INT   NOT NULL);''')
        except sqlite3.OperationalError:
            c.execute('SELECT COUNT(*) FROM MAIN')
            I.LAST_PRECIOUS = int(c.fetchone()[0])
        connect.close()
        return 1
    except:
        echo(msg=f'init_db() exit code 0 {sys.exc_info()}', warn=True)
        return 0


def action(req):
    response = requests.get(req)
    content = response.content.decode('utf8')
    return content


def get_json(req):
    content = action(req)
    content = json.loads(content)
    return content


def get_status(req):
    response = get_json(req)
    return response["ok"]


def get_updates(offset=None, timeout=100):
    req = f'{I.HOST}/getUpdates?timeout={timeout}'
    if offset:
        req += f'&offset={offset}'
    msg = get_json(req)
    return msg


def handle_msg(msg, last_update):
    # handling message id
    msg_id = msg['result'][last_update]['update_id']
    # handling message type
    try:
        msg_header = msg['result'][last_update]['message']
    except:
        msg_header = msg['result'][last_update]['edited_message']
    # handling message date time
    msg_date = msg_header['date']
    # handling message author
    msg_user = msg_header['from']['username']
    # handling message chat id
    msg_chat_id = msg_header['chat']['id']
    # handling message text
    try:
        msg_text = msg_header['text']
    except:
        try:
            msg_text = msg_header['sticker']['emoji']
        except:
            msg_text = '...'
            echo(msg=f'!!! Some stange message: {msg_header}', warn=True)
    # logging
    echo(msg_id, msg_date, msg_user, msg_chat_id, msg_text)
    I.LAST_ID = msg_id + 1
    # shutdown button
    if msg_text.lower() == '/bot_stop' and msg_chat_id == I.OWNER_ID:
        get_updates(offset=msg_id+1, timeout=0)
        send_msg(msg_chat_id, '🏁')
        return 0
    # start counting
    elif msg_text.lower()[:20] == '!bot start counting ':
        if len(msg_text[20:]) > 200:
            return send_msg(msg_chat_id, 'This message is too long. It cannot be record.')
        else:
            return counting_start(msg_chat_id, msg_date, msg_text)
    # show counting
    elif msg_text.lower()[:10] == '!bot show ':
        return counting_show(msg_chat_id, msg_date, msg_text[10:])
    # reset counting
    elif msg_text.lower()[:11] == '!bot reset ':
        return counting_reset(msg_chat_id, msg_date, msg_text[11:])
    # delete counting
    elif msg_text.lower()[:12] == '!bot delete ':
        return counting_delete(msg_chat_id, msg_date, msg_text[12:])
    # show help
    elif msg_text.lower()[:9] == '!bot help' and len(msg_text) == 9:
        return send_help(msg_chat_id)
    return 1


def echo(id='...', date=time.time(), user='...', chat='...', msg='...', warn=False):
    date = datetime.fromtimestamp(int(date)).strftime('%d.%m.%Y - %H:%M:%S')
    temp = (f'At {date} user {user} from {chat} post message #{id}:\n{msg}\n{"="*70}')
    if warn:
        temp = (f'\x1b[0;31;40m{temp}\x1b[0m')
    print(temp)
    return temp


def send_msg(chat_id, msg='Good day, sir!'):
    msg = urllib.parse.quote_plus(msg)
    req = f'{I.HOST}/sendMessage?chat_id={chat_id}&text={msg}&parse_mode=markdown'
    return action(req)


def counting_start(chat_id, msg_date, msg):
    connect = sqlite3.connect(I.DB_NAME)
    c = connect.cursor()
    name = ''
    # get timestamp of date
    timestamp = int(time.mktime(datetime.strptime(datetime.fromtimestamp(int(msg_date)).strftime("%d.%m.%Y"), "%d.%m.%Y").timetuple()))
    # lazy counter
    if re.search(r'^!bot start counting for (.*)', msg):
        name = msg[24:]
    # words counter
    elif re.search(r'^!bot start counting since (now|today|tomorrow|yesterday) for (.*)', msg):
        res = re.match(r'^!bot start counting since (now|today|tomorrow|yesterday) for (.*)', msg)
        name = res.group(2)
        if res.group(1) == 'tomorrow':
            timestamp += 86400
        elif res.group(1) == 'yesterday':
            timestamp -= 86400
    # date counter
    elif re.search(r'!bot start counting since ([\d]{2}[.][\d]{2}[.][\d]{4}) for (.*)', msg):
        res = re.match(r'!bot start counting since ([\d]{2}[.][\d]{2}[.][\d]{4}) for (.*)', msg)
        name = res.group(2)
        try:
            timestamp = int(time.mktime(datetime.strptime(res.group(1), "%d.%m.%Y").timetuple()))
            if timestamp < 0:
                raise
        # fix for windows
        except Exception as e:
            timestamp = 0
            msg += '. But honestly i can\'t count earlier than 01.01.1970.'
    if name != '':
        while 1:
            try:
                c.execute("INSERT INTO MAIN (ID, CHAT_ID, NAME, TIME) VALUES (?, ?, ?, ?)", (I.LAST_PRECIOUS, chat_id, name, timestamp))
                send_msg(chat_id=chat_id, msg=f'I {msg[5:]}')
                I.LAST_PRECIOUS += 1
                break
            except sqlite3.IntegrityError:
                I.LAST_PRECIOUS += 1
    else:
        send_msg(chat_id=chat_id, msg=f'Wrong command')
    connect.commit()
    connect.close()


def counting_show(chat_id, msg_date, msg):
    connect = sqlite3.connect(I.DB_NAME)
    c = connect.cursor()
    temp = ''
    try:
        if msg == 'all':
            c.execute("SELECT * FROM MAIN WHERE CHAT_ID=?", (str(chat_id), ))
            result = c.fetchall()
            if len(result) is 0:
                raise
            for row in result:
                print(f'!!!, {msg_date} - {int(row[3])}')
                if msg_date < int(row[3]):
                    date = 0  # Don't count for the future
                else:
                    date = int(msg_date - int(row[3])) // 86400
                date = '️⃣'.join(tuple(str(date)))
                if len(temp + row[2]) < 1000:
                    temp += f'Day\'s since {row[2]}: {date}️⃣\n'
                else:
                    send_msg(chat_id=chat_id, msg=temp)
                    temp = ''
                    temp += f'Day\'s since {row[2]}: {date}️⃣\n'
        else:
            c.execute("SELECT * FROM MAIN WHERE CHAT_ID=? AND NAME=?", (str(chat_id), str(msg)))
            result = c.fetchone()
            if msg_date < int(result[3]):
                    date = 0  # Don't count for the future
            else:
                date = int(msg_date - int(result[3])) // 86400
            date = '️⃣'.join(tuple(str(date)))
            temp += f'Day\'s since {result[2]}: {date}️⃣\n'
    except:
        connect.close()
        temp = 'Nothing to show'
        send_msg(chat_id=chat_id, msg=temp)
        echo(date=msg_date, chat=chat_id, msg=f'{msg} - {sys.exc_info()}', warn=True)
        return 0
    connect.close()
    send_msg(chat_id=chat_id, msg=temp)
    return 1


def counting_reset(chat_id, msg_date, msg):
    try:
        connect = sqlite3.connect(I.DB_NAME)
        c = connect.cursor()
        temp = ''
        # reset all by design
        c.execute("UPDATE MAIN SET TIME=? WHERE CHAT_ID=? AND NAME=?", (int(time.mktime(datetime.strptime(datetime.fromtimestamp(int(msg_date)).strftime("%d.%m.%Y"), "%d.%m.%Y").timetuple())), str(chat_id), str(msg)))
        result = c.fetchall()
        if connect.total_changes is 0:
            raise
        temp = f'Resetting {connect.total_changes} records'
        connect.commit()
        connect.close()
    except:
        echo(date=msg_date, chat=chat_id, msg=sys.exc_info(), warn=True)
        temp = 'Nothing to reset'
    send_msg(chat_id=chat_id, msg=temp)


def counting_delete(chat_id, msg_date, msg):
    connect = sqlite3.connect(I.DB_NAME)
    c = connect.cursor()
    temp = ''
    try:
        result = c.execute("SELECT TIME FROM MAIN WHERE CHAT_ID=? AND ID=(SELECT MIN(ID) FROM MAIN WHERE CHAT_ID=? AND NAME=?)", (str(chat_id), str(chat_id), str(msg)))
        date = c.fetchone()
        c.execute("DELETE FROM MAIN WHERE CHAT_ID=? AND ID=(SELECT MIN(ID) FROM MAIN WHERE CHAT_ID=? AND NAME=?)", (str(chat_id), str(chat_id), str(msg)))
        date = round(int(time.time() - int(date[0])) // 86400)
        date = '️⃣'.join(tuple(str(date)))
        temp = f'I delete counting for {msg} since {date}️⃣ days!'
    except:
        echo(date=msg_date, chat=chat_id, msg=sys.exc_info(), warn=True)
        temp = 'Nothing to delete'
    connect.commit()
    connect.close()
    send_msg(chat_id=chat_id, msg=temp)
    echo(date=msg_date, chat=chat_id, msg=f'!bot delete {msg}', warn=True)


def send_help(chat_id):
    text = '''
*"Days since"* commands:
`!bot start counting for <smth>` - start unique counting for user|group with name `<smth>`
`!bot start counting since <dd.mm.yyy> for <smth>` - start unique counting for user|group with name `<smth>` since `<dd.mm.yyy>`
`!bot show <smth>` - show how many days sice event `<smth>`
`!bot show all` - show all events for user|group
`!bot reset <smth>` - reset counter for event `<smth>`
`!bot delete <smth>` - delete counter for event `<smth>`
`!bot help` - idk
'''
    send_msg(chat_id=chat_id, msg=text)


if __name__ == '__main__':
    I = Init()
    main()
else:
    I = Init()
