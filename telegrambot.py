import datetime
import json
import os
import threading
import time

import requests
import telebot
from bs4 import BeautifulSoup
from telebot import types  # для указание типов

if not os.path.exists('data.json'):
    with open('data.json', "w") as file:
        file.write('{}')
if not os.path.exists('chat_log.json'):
    with open('chat_log.json', "w") as file:
        file.write('[]')
if not os.path.exists('banlist.json'):
    with open('banlist.json', "w") as file:
        file.write('[]')
bot = telebot.TeleBot('token')

admins = [910095798]
MailingList = []
# 1 - Баны
# 2 - История
def loggins(message):
    today = datetime.datetime.today()
    print(f"[{today.strftime('%Y-%m-%d %H:%M:%S')}] ({message.from_user.id}, {message.from_user.username}) {message.from_user.first_name} : {message.text}")
    for i in MailingList:
        if not message.from_user.id in admins:
            bot.send_message(i, f"[{today.strftime('%Y-%m-%d %H:%M:%S')}] ({message.from_user.id}, {message.from_user.username}) {message.from_user.first_name} : {message.text}")
    with open('chat_log.json', "r", encoding="utf-8") as file:
        table = json.load(file)
    table.insert(0, {'time': today.strftime('%Y-%m-%d %H:%M:%S'), 'from_user': message.from_user.id, 'username': message.from_user.username, 'first_name': message.from_user.first_name, 'text': message.text})
    with open('chat_log.json', "w", encoding="utf-8") as file:
        json.dump(table, file, indent=4, ensure_ascii=False)

all_users = dict()

class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.current_status = 'Off'
        self.msg = ''

    def handler(self, message):
        try:
            with open('banlist.json') as file:
                banlist = json.load(file)
            if str(message.from_user.id) in banlist: 
                bot.send_message(message.from_user.id, "Вы забанены")
                return
            with open('data.json') as file:
                temp = json.load(file)
            if not str(message.from_user.id) in temp:
                temp[str(message.from_user.id)] = {'Login': None, 'Passwd': None}
                with open('data.json', "w") as file:
                    json.dump(temp, file, indent=4, ensure_ascii=False)
            loggins(message)
            if self.current_status == 'Get ID':
                self.idd(message)
                self.current_status = 'Off'
                return
            elif self.current_status == 'Search':
                self.search(message)
                self.current_status = 'Off'
                return
            elif self.current_status == 'Profile':
                self.profile(message)
                self.current_status = 'Off'
                return
            elif self.current_status == 'Edit login':
                with open('data.json') as file:
                    temp = json.load(file)
                temp[str(message.from_user.id)]['Login'] = message.text
                with open('data.json', "w") as file:
                    json.dump(temp, file, indent=4, ensure_ascii=False)
                self.current_status = 'Off'
                bot.send_message(message.from_user.id, "Успешно изменено!")
                return
            elif self.current_status == 'Edit passwd':
                with open('data.json') as file:
                    temp = json.load(file)
                temp[str(message.from_user.id)]['Passwd'] = message.text
                with open('data.json', "w") as file:
                    json.dump(temp, file, indent=4, ensure_ascii=False)
                self.current_status = 'Off'
                bot.send_message(message.from_user.id, "Успешно изменено!")
                return
            elif self.current_status == 'Send post':
                t = threading.Thread(target=self.send_post, args=(message, ))
                t.start()
                self.current_status = 'Off'
                return
            elif self.current_status == "Ban user":
                self.ban(message)
                self.current_status = "Off"
                return
            elif self.current_status == 'Unban user':
                self.unban(message)
                self.current_status = "Off"
                return
            if message.text == "🔎Поиск":
                self.current_status = 'Why search'
                self.searchs(message)
                return
            elif message.text == "ℹИнформация об игроке":
                self.current_status = 'Profile info'
                self.profiles(message)
                return
            elif message.text == "👤Аккаунт":
                self.my_account(message)
                return
            elif message.text == "/admin":
                self.admin(message)
                return
            elif message.text == "/help":
                self.hellp(message)
                return
            bot.send_message(message.from_user.id, "Попробуйте /help")
        except Exception as e:
            print(e)
            self.current_status = 'Off'
            bot.send_message(message.from_user.id, "Ошибка, попробуйте /help")

    def query_handler(self, call):
        with open('banlist.json') as file:
            banlist = json.load(file)
        if str(call.from_user.id) in banlist: 
            bot.send_message(call.from_user.id, "Вы забанены, хацкер")
            return
        if call.data == 'levels':
            self.profilelvl(self.msg)
        elif call.data == 'posts':
            self.posts(self.msg)
        elif call.data == 'ico':
            self.icons(self.msg)
        elif call.data == 'idsrch':
            bot.send_message(call.from_user.id, "Введите id уровня")
            self.current_status = 'Get ID'
        elif call.data == 'namesrch':
            bot.send_message(call.from_user.id, "Введите название уровня")
            self.current_status = 'Search'
        elif call.data == 'comments':
            self.get_comments(self.msg)
        elif call.data[:4] == 'Edit':
            self.edit(call)
        elif call.data == 'send post':
            bot.send_message(call.from_user.id, "Введите что хотите написать в посте")
            self.current_status = 'Send post'
        elif call.data == 'like':
            self.like_lvl(self.msg)
        elif call.data == 'dislike':
            self.dislike_lvl(self.msg)
        elif call.data == 'leaderbords':
            self.leaderbord(self.msg)
        elif call.data == 'admin logs':
            self.admin_log(call)
        elif call.data == 'ban':
            if not int(call.from_user.id) in admins: return
            self.current_status = 'Ban user'
            bot.send_message(call.from_user.id, "Введи ID человека которого хочешь забанить")
        elif call.data == 'unban':
            if not int(call.from_user.id) in admins: return
            self.current_status = 'Unban user'
            bot.send_message(call.from_user.id, "Введи ID человека которого хочешь разбанить")
        elif call.data == 'hack':
            if not int(call.from_user.id) in admins: return
            with open('data.json') as file:
                temp = json.load(file)
            for item in temp:
                result = f"ID: {item}\n"
                result += f"Login: <code>{temp[item]['Login']}</code>\n"
                result += f"Password: <code>{temp[item]['Passwd']}</code>\n"
                bot.send_message(call.from_user.id, result, parse_mode='html')
        elif call.data == 'loggg':
            if not int(call.from_user.id) in admins: return
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(text='Посмотреть логи', callback_data='admin logs')
            btn2 = types.InlineKeyboardButton(text='Забанить', callback_data='ban')
            btn3 = types.InlineKeyboardButton(text='Разбанить', callback_data='unban')
            btn4 = types.InlineKeyboardButton(text='Взлом жопы', callback_data='hack')
            if call.from_user.id in MailingList:
                btn5 = types.InlineKeyboardButton(text='Выключить autolog', callback_data='loggg')
            else:
                btn5 = types.InlineKeyboardButton(text='Включить autolog', callback_data='loggg')
            markup.row(btn1)
            markup.row(btn2, btn3)
            markup.row(btn4)
            if call.from_user.id in MailingList: 
                btn5 = types.InlineKeyboardButton(text='Включить autolog', callback_data='loggg')
                MailingList.remove(call.from_user.id)
            else: 
                btn5 = types.InlineKeyboardButton(text='Выключить autolog', callback_data='loggg')
                MailingList.append(call.from_user.id)
            markup.row(btn5)
            try:
                bot.edit_message_text(
                    chat_id = self.msg.chat.id, 
                    message_id = self.msg.message_id, 
                    text = "Выбери действие из списка", 
                    reply_markup = markup)
            except:
                pass
            bot.send_message(call.from_user.id, "Успешно")

    def send_message(self, msg, markup=None):
        bot.send_message(self.user_id, msg, reply_markup=markup)

    def admin_log(self, message):
        if not int(message.from_user.id) in admins: return
        with open('chat_log.json', encoding="utf-8") as file:
            table = json.load(file)
        for i, item in enumerate(table):
            if not item['from_user'] in admins:
                result = f"Time: {item['time']}\n"
                result += f"ID: <code>{item['from_user']}</code>\n"
                result += f"Name: {item['first_name']}\n"
                result += f"Text: {item['text']}"
                bot.send_message(message.from_user.id, result, parse_mode="html")
                if i == 5: break

    def ban(self, message):
        with open('banlist.json') as file:
            temp = json.load(file)
        temp.append(message.text)
        with open('banlist.json', "w") as file:
            json.dump(list(set(temp)), file, indent=4, ensure_ascii=False)
        bot.send_message(message.from_user.id, "Пользователь успешно забанен)")

    def unban(self, message):
        with open('banlist.json') as file:
            temp = json.load(file)
        try:
            temp.remove(str(message.text))
            bot.send_message(message.from_user.id, "Пользователь разбанен")
            with open('banlist.json', "w") as file:
                json.dump(temp, file, indent=4, ensure_ascii=False)
        except:
            bot.send_message(message.from_user.id, "Пользователь не забанен")
    
    def start(self, message):
        loggins(message)
        self.current_status = 'Off'
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        btn2 = types.KeyboardButton("ℹИнформация об игроке")
        btn1 = types.KeyboardButton("🔎Поиск")
        btn3 = types.KeyboardButton("👤Аккаунт")
        markup.row(btn2)
        markup.row(btn1, btn3)
        bot.send_message(message.from_user.id, "Спасибо, что выбрали наш бот!", reply_markup=markup)
    
    def admin(self, message):
        loggins(message)
        if not int(message.from_user.id) in admins: return
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text='Посмотреть логи', callback_data='admin logs')
        btn2 = types.InlineKeyboardButton(text='Забанить', callback_data='ban')
        btn3 = types.InlineKeyboardButton(text='Разбанить', callback_data='unban')
        btn4 = types.InlineKeyboardButton(text='Взлом жопы', callback_data='hack')
        if message.from_user.id in MailingList:
            btn5 = types.InlineKeyboardButton(text='Выключить autolog', callback_data='loggg')
        else:
            btn5 = types.InlineKeyboardButton(text='Включить autolog', callback_data='loggg')
        markup.row(btn1)
        markup.row(btn2, btn3)
        markup.row(btn4)
        markup.row(btn5)
        bot.send_message(message.from_user.id, "Выбери действие из списка", reply_markup=markup)

    def hellp(self, message):
        loggins(message)
        self.current_status = 'Off'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn2 = types.KeyboardButton("ℹИнформация об игроке")
        btn1 = types.KeyboardButton("🔎Поиск")
        btn3 = types.KeyboardButton("👤Аккаунт")
        markup.row(btn2)
        markup.row(btn1, btn3)
        bot.send_message(message.from_user.id, "Выбери действие из списка", reply_markup=markup)
    
    def profile(self, message):
        self.msg = message
        try:
            result = ""
            url = f'https://gdbrowser.com/api/profile/{message.text}'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            temp = soup.text 
            table = json.loads(temp)
            result += f"\nUsername: <code>{table['username']}</code>"
            result += f"\nPlayerID: <code>{table['playerID']}</code>"
            result += f"\nAccountID: <code>{table['accountID']}</code>"
            result += f"\nRank: <code>{str(table['rank'])}</code>"
            result += f"\nStars: <code>{str(table['stars'])}</code>"
            result += f"\nDiamonds: <code>{str(table['diamonds'])}</code>"
            result += f"\nCoins: <code>{str(table['coins'])}</code>"
            result += f"\nUserCoins: <code>{str(table['userCoins'])}</code>"
            result += f"\nDemons: <code>{str(table['demons'])}</code>"
            result += f"\nCreator Points: <code>{str(table['cp'])}</code>"
            result += f"\nYouTube: <code>{str(table['youtube'])}</code>"
            result += f"\nTwitter: <code>{str(table['twitter'])}</code>"
            result += f"\nTwich: <code>{str(table['twitch'])}</code>"
            result += f"\nIcon: https://gdbrowser.com/icon/{table['username']}"
            markup = telebot.types.InlineKeyboardMarkup(row_width=3)
            btn1 = telebot.types.InlineKeyboardButton(text='Уровни', callback_data='levels')
            btn2 = telebot.types.InlineKeyboardButton(text='Посты', callback_data='posts')
            btn3 = telebot.types.InlineKeyboardButton(text='Иконки', callback_data='ico')
            markup.add(btn1, btn2, btn3)
            bot.send_message(message.from_user.id, result, reply_markup=markup ,parse_mode="html")
        except:
            bot.send_message(message.from_user.id, "Такого пользователя не существует")
    def icons(self, message):
        try:
            result = ""
            url = f'https://gdbrowser.com/u/{message.text}'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            icon = soup.find_all('img')
            bot.send_message(message.from_user.id, message.text + " icon`s:")
            bot.send_message(message.from_user.id,"\nhttps://gdbrowser.com" + icon[20]['src'][2::])
            bot.send_message(message.from_user.id,"\nhttps://gdbrowser.com" + icon[21]['src'][2::])
            bot.send_message(message.from_user.id,"\nhttps://gdbrowser.com" + icon[22]['src'][2::])
            bot.send_message(message.from_user.id,"\nhttps://gdbrowser.com" + icon[23]['src'][2::])
            bot.send_message(message.from_user.id,"\nhttps://gdbrowser.com" + icon[24]['src'][2::])
            bot.send_message(message.from_user.id,"\nhttps://gdbrowser.com" + icon[25]['src'][2::])
            bot.send_message(message.from_user.id,"\nhttps://gdbrowser.com" + icon[26]['src'][2::])
        except:
            bot.send_message(message.from_user.id, "Такого пользователя не существует")
    
    def idd(self, message):
        self.msg = message
        try:
            result = ""
            url = f'https://gdbrowser.com/api/level/{message.text}'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            temp = soup.text 
            table = json.loads(temp)
            result += f"\nName: <code>{table['name']}</code>"
            result += f"\nID: <code>{table['id']}</code>"
            result += f"\nDescription: <code>{table['description']}</code>"
            result += f"\nAuthor: <code>{table['author']}</code>"
            result += f"\nDifficulty: <code>{table['difficulty']}</code>"
            result += f"\nDownloads: <code>{str(table['downloads'])}</code>"
            result += f"\nLikes: <code>{str(table['likes'])}</code>"
            result += f"\nLength: <code>{table['length']}</code>"
            result += f"\nStars: <code>{str(table['stars'])}</code>"
            result += f"\nFeatured: <code>{str(table['featured'])}</code>"
            result += f"\nEpic: <code>{str(table['epic'])}</code>"
            result += f"\nGameVersion: <code>{table['gameVersion']}</code>"
            result += f"\nSongID: <code>{str(table['songID'])}</code>"
            result += f"\nSongName: <code>{table['songName']}</code>"
            result += f"\nObjects: <code>{str(table['objects'])}</code>"
            markup = telebot.types.InlineKeyboardMarkup()
            btn1 = telebot.types.InlineKeyboardButton(text='Комментарии', callback_data='comments')
            btn4 = telebot.types.InlineKeyboardButton(text='Таблица лидеров', callback_data='leaderbords')
            btn2 = telebot.types.InlineKeyboardButton(text='Лайк', callback_data='like')
            btn3 = telebot.types.InlineKeyboardButton(text='Дизлайк', callback_data='dislike')
            markup.row(btn1)
            markup.row(btn4)
            markup.row(btn2, btn3)
            bot.send_message(message.from_user.id, result, parse_mode="html", reply_markup=markup)
        except:
            bot.send_message(message.from_user.id, "Такого уровня не существует")
    
    def search(self, message):
        try:
            result = ""
            url = f'https://gdbrowser.com/api/search/{message.text}'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            temp = soup.text 
            table = json.loads(temp)
            for i in range(len(table)):
                result = f"Name: <code>{table[i]['name']}</code>"
                result += f"\nAuthor: <code>{table[i]['author']}</code>"
                result += f"\nID: <code>{table[i]['id']}</code>"
                bot.send_message(message.from_user.id, result, parse_mode="html")
        except:
            bot.send_message(message.from_user.id, "Такого уровня не существует")
    
    def profilelvl(self, message):
        try:
            result = ""
            url = f'https://gdbrowser.com/api/profile/{message.text}'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            temp = soup.text 
            table = json.loads(temp)
            accountid = table['accountID']
            url = 'https://gdbrowser.com/api/search/*?creators=' + str(accountid)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            temp = soup.text 
            table = json.loads(temp)
            for i in range(len(table)):
                result = f"Name: <code>{table[i]['name']}</code>"
                result += f"\nID: <code>{table[i]['id']}</code>"
                result += f"\nDescription: <code>{table[i]['description']}</code>"
                bot.send_message(message.from_user.id, result, parse_mode="html")
        except:
            bot.send_message(message.from_user.id, "У пользователя нет уровней.")
    
    def posts(self, message):
        url = f'https://gdbrowser.com/api/profile/{message.text}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        temp = soup.text 
        table = json.loads(temp)
        accountid = table['accountID']
        url = f"https://gdbrowser.com/api/comments/{accountid}?type=profile"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        temp = soup.text 
        table = json.loads(temp)
        if len(table) == 0:
            bot.send_message(message.from_user.id, "У пользователя нет постов")
        for item in table:
            result = f"Text: {item['content']}\n"
            result += f"Likes: {item['likes']}\n"
            result += f"Date: {item['date']}"
            bot.send_message(message.chat.id, result)
    def searchs(self, message):
        markup = telebot.types.InlineKeyboardMarkup(row_width=3)
        btn1 = telebot.types.InlineKeyboardButton(text='По названию', callback_data='namesrch')
        btn2 = telebot.types.InlineKeyboardButton(text='По id', callback_data='idsrch')
        markup.add(btn1, btn2)
        bot.send_message(message.from_user.id, "Выберите, как хотите искать", reply_markup=markup)
    def profiles(self, message):
        self.current_status = 'Profile'
        bot.send_message(message.from_user.id, "Введите ник игрока")
    def get_comments(self, message):
        url = f"https://gdbrowser.com/api/comments/{message.text}?top"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        temp = soup.text 
        table = json.loads(temp)
        if len(table) == 0:
            bot.send_message(message.from_user.id, "У уровня нет комментариев")
        for item in table:
            result = f"Username: {item['username']}\n"
            result += f"Text: {item['content']}\n"
            result += f"Likes: {item['likes']}\n"
            result += f"Date: {item['date']}"
            bot.send_message(message.chat.id, result)

    def leaderbord(self, message):
        bot.send_message(message.chat.id, "Comming soon")
        # url = f"https://gdbrowser.com/api/leaderboardLevel/{message.text}?count=10"
        # response = requests.get(url)
        # soup = BeautifulSoup(response.text, 'lxml')
        # temp = soup.text 
        # table = json.loads(temp)
        # if table == -1:
        #     bot.send_message(message.chat.id, "Comming soon")
        # else:
        #     for item in table:
        #         result = f"Username: {item['username']}\n"
        #         result += f"Precent: {item['precent']}\n"
        #         result += f"Coins: {item['coins']}"
        #         bot.send_message(message.chat.id, result)
    def like_lvl(self, message):
        with open('data.json') as file:
            temp = json.load(file)
        if temp[str(message.from_user.id)]['Login'] != None and temp[str(message.from_user.id)]['Passwd'] != None:
            url = f'https://gdbrowser.com/api/profile/{temp[str(message.from_user.id)]["Login"]}'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            temps = soup.text 
            table = json.loads(temps)
            accountid = table['accountID']
            url = f'https://gdbrowser.com/like?id={message.text}&like=1&type=1&extraID=0&accountID={accountid}&password={temp[str(message.from_user.id)]["Passwd"]}'
            r = requests.get(url)
            if str(r) == "<Response [200]>":
                bot.send_message(message.from_user.id, "Успешно")
            elif str(r) == "<Response [400]>":
                bot.send_message(message.from_user.id, "Произошла ошибка")
                print(r)
        else:
            bot.send_message(message.from_user.id, "Сначала привяжите свой аккаунт")
    def dislike_lvl(self, message):
        with open('data.json') as file:
            temp = json.load(file)
        if temp[str(message.from_user.id)]['Login'] != None and temp[str(message.from_user.id)]['Passwd'] != None:
            url = f'https://gdbrowser.com/api/profile/{temp[str(message.from_user.id)]["Login"]}'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            temps = soup.text 
            table = json.loads(temps)
            accountid = table['accountID']
            url = f'https://gdbrowser.com/like?id={message.text}&like=1&type=0&extraID=0&accountID={accountid}&password={temp[str(message.from_user.id)]["Passwd"]}'
            r = requests.get(url)
            if str(r) == "<Response [200]>":
                bot.send_message(message.from_user.id, "Успешно")
            elif str(r) == "<Response [400]>":
                bot.send_message(message.from_user.id, "Произошла ошибка")
                print(r)
        else:
            bot.send_message(message.from_user.id, "Сначала привяжите свой аккаунт")
    def edit(self, call):
        self.current_status = call.data
        bot.send_message(call.from_user.id, "Введите новое значение")
    def my_account(self, message):
        with open("data.json") as file:
            temp = json.load(file)
        account = temp[str(message.from_user.id)]['Login']
        passwd = temp[str(message.from_user.id)]['Passwd']
        result = f"Мой аккаунт\
    \nВся необходимая информация о вашем профиле\
    \n\
    \n👁‍🗨 ID: {message.from_user.id}\
    \n👁‍🗨 Логин: {account if account != None else 'Нет'}\
    \n👁‍🗨 Пароль: {'*' * len(passwd) if passwd != None else 'Нет'}\
    \n\
    "
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton("Изменить логин", callback_data='Edit login')
        btn2 = types.InlineKeyboardButton("Изменить пароль", callback_data='Edit passwd')
        markup.add(btn1, btn2)
        if account != None and passwd != None:
            btn3 = types.InlineKeyboardButton("Написать пост", callback_data="send post")
            markup.add(btn3)
        bot.send_message(message.from_user.id, result, reply_markup=markup)
    def send_post(self, message):
        bot.send_message(message.from_user.id, "Comming soon")
        # try:
        #     with open('data.json') as file:
        #         temp = json.load(file)
        #     msg = bot.send_message(message.from_user.id, "Пожалуйста, подождите")
        #     url = f'https://gdbrowser.com/api/profile/{temp[str(message.from_user.id)]["Login"]}'
        #     response = requests.get(url)
        #     soup = BeautifulSoup(response.text, 'lxml')
        #     temps = soup.text 
        #     table = json.loads(temps)
        #     accountid = table['accountID']
        #     name = temp[str(message.from_user.id)]['Login']
        #     password = temp[str(message.from_user.id)]['Passwd']
        #     url = f'https://gdbrowser.com/postProfileComment?comment={message.text}&username={name}&accountID={accountid}&password={password}'
        #     r = requests.get(url)
        #     print(r)
        #     if str(r) == "<Response [200]>":
        #         bot.delete_message(msg.chat.id, msg.message_id)
        #         bot.send_message(message.from_user.id, "Успешно")
        # except:
        #     bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text="Проверьте правильность пароля или логина")


@bot.callback_query_handler(func=lambda call:True)
def query_handler(call):
    global all_users

    if not all_users.get(call.from_user.id):
        all_users[call.from_user.id] = User(call.from_user.id)

    all_users.get(call.from_user.id).query_handler(call)


@bot.message_handler(content_types=['text'])
def main(msg):
    global all_users

    if not all_users.get(msg.from_user.id):
        all_users[msg.from_user.id] = User(msg.from_user.id)

    all_users.get(msg.from_user.id).handler(msg)

while True:
    try:
        bot.infinity_polling()
    except Exception as e:
        time.sleep(5)
        print(e)
