import json
import os
import sqlite3 as sql
import time
from urllib import parse

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtNetwork import QNetworkProxy
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton

from api import UrlAPI

from multiprocessing.dummy import Pool as ThreadPool



class ImitatingConversation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)

        self.parent = parent
        self.webViewList = []
        self.chil = [item for item in self.parent.itemList if item.b.checkState() == 2 and item.frozen == 0]

        self.ui()
        self.creatingViews()

        self.btn_chek_dialogs.clicked.connect(self.chek_dialogs)

    def ui(self):
        self.btn_chek_dialogs = QPushButton('Проверить диалоги')

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(self.btn_chek_dialogs)

        self.show()

    def chek_dialogs(self):
        os.chdir('/root/PycharmProjects/HearSheep')
        con = sql.connect(os.getcwd() + '/db/db.sqlite3')
        cur = con.cursor()

        with con:
            cur.execute('SELECT * FROM chat')
            chats = cur.fetchall()
            cur.execute('SELECT * FROM accaunt_chat')
            acc_chats = cur.fetchall()

        # checking whether the account is in a chat
        for view in self.webViewList:

            if [row for row in acc_chats if row[0] == view.user_id]:
                continue
            else:
                self.throughTheFreeChats(view, chats)

    def throughTheFreeChats(self, view, chats):
        print('view', str(view.user_id))
        # Through chats
        for chat in chats:
            number_chat, count_users, invite_link = chat

            if count_users < 10:
                join_the_chat = view.joinTheChat(chat)

                if join_the_chat:
                    return

        # Create chat
        create_chat = view.createChat()

        if create_chat:
            return

    def creatingViews(self):

        def setSignal(btn, view):
            return btn.clicked.connect(view.show)

        for acc in self.chil:
            view_name = 'view_' + str(acc.user_id)
            btn_view_name = 'btn_' + view_name
            setattr(self, view_name, MyWebView(self, acc))
            setattr(self, btn_view_name, QPushButton(str(acc.user_id)))
            view = getattr(self, view_name)
            btn  = getattr(self, btn_view_name)
            self.webViewList.append(view)
            self.mainLayout.addWidget(btn)
            setSignal(btn, view)




class MyWebView(QWebEngineView):
    def __init__(self, parent=None, acc=None):
        super().__init__()

        self.parent = parent
        self.session = acc.session
        self.user_id = acc.user_id
        self.chekLoadFinish = False
        self.progress = 0

        # Connect sql and get data
        os.chdir('/root/PycharmProjects/HearSheep')
        con = sql.connect(os.getcwd() + '/db/db.sqlite3')
        cur = con.cursor()

        with con:
            cur.execute('SELECT login, pass, token, proxy, user_agent FROM accaunt where user_id=?', (self.user_id,))
            row = cur.fetchone()
            self.login, self.password, self.token, proxy, user_agent = row

        con.close()

        # Path Cookies
        os.chdir('/root/PycharmProjects/HearSheep')
        pathCookies = '/root/PycharmProjects/HearSheep/cookies/' + str(self.user_id)

        if os.path.exists(pathCookies):
            pass
        else:
            os.chdir('/root/PycharmProjects/HearSheep/cookies')
            os.mkdir(str(self.user_id))
            pathCookies = '/root/PycharmProjects/HearSheep/cookies/' + str(self.user_id)

        # settings
        profile = self.page().profile()
        profile.setPersistentStoragePath(pathCookies)
        profile.setHttpUserAgent(user_agent)
        profile.setHttpAcceptLanguage("ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4")

        urlinfo = parse.urlparse(proxy)
        self.proxy = QNetworkProxy()
        self.proxy.setType(QNetworkProxy.HttpProxy)
        self.proxy.setHostName(urlinfo.hostname)
        self.proxy.setPort(urlinfo.port)
        self.proxy.setUser(urlinfo.username)
        self.proxy.setPassword(urlinfo.password)
        QNetworkProxy.setApplicationProxy(self.proxy)
        self.page().proxyAuthenticationRequired.connect(self.handleProxyAuthReq)

        self.loadProgress.connect(self.setProgress)

        self.load(QtCore.QUrl('https://vk.com/'))
        self.auth()

    def handleProxyAuthReq(self, url, auth, proxyhost):
        auth.setUser(self.proxy.user())
        auth.setPassword(self.proxy.password())

    def setProgress(self, value):
        self.progress = value

    def waitForSignal(self):
        loop = QEventLoop()

        def work(value):
            print('loop', value)
            if value > 95:
                loop.quit()

        self.loadProgress.connect(work)
        loop.exec_()
        self.loadProgress.disconnect()
        time.sleep(2)
        return True

    def auth(self):
        self.waitForSignal()

        if self.page().url().url() == 'https://vk.com/' or self.page().url().url() == 'https://vk.com/index.php':
            page = self.page()
            page.runJavaScript(
                'document.querySelector("#index_email").value = "{}"'.format(self.login))
            page.runJavaScript(
                'document.querySelector("#index_pass").value = "{}"'.format(self.password))
            page.runJavaScript(
                'document.querySelector("#index_login_button").click()')

        print('auth complete')

    def joinTheChat(self, chat):
        number_chat, count_users, invite_link = chat
        print('connect to', invite_link)
        self.load(QtCore.QUrl(invite_link))
        print('waiting load inviting page')
        self.waitForSignal()

        page = self.page()
        page.runJavaScript(
            "document.querySelector('button.flat_button.round_button._im_join_chat.im-invitation--join').click()")

        print('waiting after clicking the button "connect"')
        self.waitForSignal()


        # Check the entry in the chat
        print('get dialogs')
        getUrl = UrlAPI(self.token)
        response = self.session.get(getUrl.messages.getDialogs(count=3), proxies=self.session.proxies)
        dialogs = json.loads(response.text)['response']['items']

        for dialog in dialogs:
            print(dialog)

            if dialog['message']['title'] == 'Читаем стихи':
                print('Find')
                os.chdir('/root/PycharmProjects/HearSheep')
                con = sql.connect(os.getcwd() + '/db/db.sqlite3')
                cur = con.cursor()

                with con:
                    cur.execute('INSERT INTO accaunt_chat(user_id,chat_id,number_chat) VALUES(?,?,?)',
                                (self.user_id, dialog['message']['chat_id'], number_chat))
                    cur.execute('UPDATE chat SET count_users=? WHERE number_chat=?', (count_users+1, number_chat))

                con.close()

                print('joined the chat')
                return True

        print("not joined the chat")
        return False

    def createChat(self):
        getUrl = UrlAPI(self.token)
        response = self.session.get(getUrl.messages.createChat(title='Читаем стихи'), proxies=self.session.proxies)
        jResponse = json.loads(response.text)

        if 'response' in jResponse:
            chat_id = jResponse['response']
            peer_id = 2000000000 + chat_id

            res = self.session.get(getUrl.messages.getInviteLink(peer_id=peer_id), proxies=self.session.proxies)
            jRes = json.loads(res.text)['response']
            invite_link = jRes['link']

            os.chdir('/root/PycharmProjects/HearSheep')
            con = sql.connect(os.getcwd() + '/db/db.sqlite3')
            cur = con.cursor()

            with con:
                cur.execute('INSERT INTO chat(number_chat,count_users,invite_link) VALUES (NULL,1,?)', (invite_link, ))
                cur.execute('SELECT number_chat FROM chat WHERE invite_link=?', (invite_link, ))
                row = cur.fetchone()
                number_chat = row[0]
                cur.execute('INSERT INTO accaunt_chat(user_id,chat_id,number_chat) VALUES (?,?,?)', (self.user_id, chat_id, number_chat))

            con.close()
            print('the chat created')
            return True

        print("the chat don't created")
        return False

    def sendMessage(self):

        page = self.page()
        page.runJavaScript(
            "document.getElementById('im_editable88230675').innerHTML = 'Йо!'")
        page.runJavaScript(
            "document.querySelector('button.im-send-btn.im-chat-input--send.im-send-btn_saudio._im_send.im-send-btn_audio').click()")
