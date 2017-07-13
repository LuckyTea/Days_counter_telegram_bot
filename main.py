'''
Days since telegram bot
Can count days since smth, for example - last jewish tricks
'''
import datetime
import json
import requests
import sqlite3
import sys
import time
import urllib

import config


class Init():
    def init(self):
        self.HOST = f'https://api.telegram.org/bot{config.token}'
        self.LAST_ID = None
        self.LAST_PRECIOUS = None


def main():
    warn(f'Good day, sir!')
    if not get_info():
        warn('Bot is down')
        return
    if not init_db():
        warn('Can\'t initialize DB')
        return
    warn(f'Now in DB {I.LAST_PRECIOUS} records')
    warn('Bot work well. Getting messages...')
    run = 1
    while run is 1:
        msg = get_updates(offset=I.LAST_ID)
        if len(msg["result"]) > 0:
            for last_update in range(len(msg['result'])):
                if not handle_msg(msg, last_update):
                    run = 0
        time.sleep(0.5)


def init_db():
    connect = sqlite3.connect('precious.db')
    c = connect.cursor()
    # c.execute("""drop table if exists MAIN""")
    try:
        c.execute('''CREATE TABLE MAIN
                 (ID      INT PRIMARY KEY   NOT NULL,
                 CHAT_ID              INT   NOT NULL,
                 NAME                TEXT   NOT NULL,
                 TIME                 INT   NOT NULL);''')
    except sqlite3.OperationalError:
        ...
    c.execute('''SELECT COUNT(*) FROM MAIN''')
    I.LAST_PRECIOUS = int(c.fetchone()[0])
    connect.close()
    return 1


def action(req):
    response = requests.get(req)
    content = response.content.decode('utf8')
    return content


def get_json(req):
    content = action(req)
    content = json.loads(content)
    return content


def get_info():
    req = f'{I.HOST}/getMe'
    response = get_json(req)
    return response["ok"]


def get_updates(offset=None):
    req = f'{I.HOST}/getUpdates?timeout=100'
    if offset:
        req += f'&offset={offset}'
    msg = get_json(req)
    return msg


def handle_msg(msg, last_update):
    msg_id = msg['result'][last_update]['update_id']
    # handling type of message
    try:
        msg_header = msg['result'][last_update]['message']
    except:
        msg_header = msg['result'][last_update]['edited_message']
    # handling message date time
    msg_time = time.time()
    # handling message author
    msg_user = msg_header['from']['username']
    # handling message chat id
    try:
        msg_chat_id = msg_header['chat']['id']
    except:
        msg_chat_id = msg_header['from']['id']
    # handling message text
    try:
        msg_text = msg_header['text']
    except:
        try:
            msg_text = msg_header['sticker']['emoji']
        except:
            msg_text = '...'
            print(msg_header)

    # shutdown button
    if msg_text.lower() == '/bot_stop' and msg_chat_id == config.owner_id and I.LAST_ID == msg_id:
        send_msg(chat_id=msg_chat_id, text=f'Bot shutdown')
        get_updates(msg_id)
        return False
    # start counting
    elif msg_text.lower()[:31] == '!bot start counting days since ' and I.LAST_ID == msg_id:
        counting_start(chat_id=msg_chat_id, msg=msg_text[4:])
    # show counting
    elif msg_text.lower()[:10] == '!bot show ':
        counting_show(chat_id=msg_chat_id, req=msg_text[10:])
    # reset counting
    elif msg_text.lower()[:11] == '!bot reset ':
        counting_reset(chat_id=msg_chat_id, req=msg_text[11:])
    # delete counting
    elif msg_text.lower()[:12] == '!bot delete ':
        counting_delete(chat_id=msg_chat_id, req=msg_text[12:])
    # show help
    elif msg_text.lower()[:9] == '!bot help' and len(msg_text) == 9:
        send_help(chat_id=msg_chat_id)
    # echo
    elif I.LAST_ID == msg_id:
        print(f'At {msg_time} user {msg_user} from {msg_chat_id} post message #{msg_id}:\n\t{msg_text}\n{msg_header}\n')
    I.LAST_ID = msg_id + 1
    return True


def send_msg(chat_id=config.owner_id, text='Good day, sir!'):
    text = urllib.parse.quote_plus(text)
    req = f'{I.HOST}/sendMessage?chat_id={chat_id}&text={text}'
    return action(req)


def counting_start(chat_id, msg):
    connect = sqlite3.connect('precious.db')
    c = connect.cursor()
    while 1:
        try:
            c.execute("INSERT INTO MAIN (ID, CHAT_ID, NAME, TIME) VALUES (?, ?, ?, ?)", (I.LAST_PRECIOUS, chat_id, msg[27:], int(time.time())))
            break
        except sqlite3.IntegrityError:
            I.LAST_PRECIOUS += 1
    connect.commit()
    connect.close()
    send_msg(chat_id=chat_id, text=f'I {msg}')
    I.LAST_PRECIOUS += 1
    warn(f'Add {msg} for {chat_id}')
    return


def counting_show(chat_id, req):
    connect = sqlite3.connect('precious.db')
    c = connect.cursor()
    temp = ''
    try:
        if req == 'all':
            result = c.execute("SELECT * FROM MAIN WHERE CHAT_ID=?", (str(chat_id), ))
        else:
            result = c.execute("SELECT * FROM MAIN WHERE CHAT_ID=? AND NAME=?", (str(chat_id), str(req)))
        for row in result:
            date = round(int(time.time() - int(row[3])) / 86400)
            date = '️⃣'.join(tuple(str(date)))
            temp += f'Day\'s since {row[2]}: {date}️⃣\n'
    except:
        warn(f'{sys.exc_info()}')
        temp = 'Nothing to show'
    send_msg(chat_id=chat_id,text=temp)
    connect.close()


def counting_reset(chat_id, req):
    connect = sqlite3.connect('precious.db')
    c = connect.cursor()
    temp = ''
    try:
        c.execute("UPDATE MAIN SET TIME=? WHERE CHAT_ID=? AND NAME=?", (int(time.time()), str(chat_id), str(req)))
        connect.commit()
        temp = f'Resetting {connect.total_changes} records'
    except:
        warn(f'{sys.exc_info()}')
        temp = 'Nothing to update'
    send_msg(chat_id=chat_id,text=temp)
    connect.close()


def counting_delete(chat_id, req):
    connect = sqlite3.connect('precious.db')
    c = connect.cursor()
    try:
        result = c.execute("SELECT * FROM MAIN WHERE CHAT_ID=? AND NAME=?", (str(chat_id), str(req)))
        for row in result:
            c.execute("DELETE FROM MAIN where ID=?", (str(row[0])))
            connect.commit()
            print("Total number of rows deleted :", connect.total_changes)
        temp = 'Success!'
    except:
        warn(f'{sys.exc_info()}')
        temp = 'Nothing to delete'
    send_msg(chat_id=chat_id, text=temp)
    connect.close()


def send_help(chat_id):
    text = '''
*"Days since"* commands:
`!bot start counting days since <smth>` - start counting unique event for user|group
`!bot show <smth>` - show how many days sice event _<smth>_
`!bot show all` - show all events for user|group
`!bot reset <smth>` - reset counter for event _<smth>_
`!bot delete <smth>` - delete counter for event _<smth>_
`!bot help` - idk
'''
    req = f'{I.HOST}/sendMessage?chat_id={chat_id}&text={text}&parse_mode=markdown'
    return action(req)


def warn(msg):
    print(f'\x1b[0;31;40m{msg}\x1b[0m')

if __name__ == '__main__':
    I = Init()
    I.init()
    main()
