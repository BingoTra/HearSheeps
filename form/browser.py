import random
import sqlite3 as sql
from urllib import parse

import time

import os
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QWindow
from PyQt5.QtNetwork import QNetworkProxy
from PyQt5.QtWebEngineCore import QWebEngineCookieStore
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QShortcut, QLabel


class Browser(QWidget):
    def __init__(self, parent=None, user_id=None):
        super().__init__(parent, Qt.Window)

        self.user_id = user_id
        self.web = MyWebView(self, self.user_id)

        self.ui()

        self.web.titleChanged.connect(self.adjustTitle)
        self.web.loadFinished.connect(self.adjustLocation)
        self.line_url.returnPressed.connect(self.changeLocation)

        QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_P), self).activated.connect(lambda: Password(self))

    def ui(self):
        self.line_url = QLineEdit()

        main = QVBoxLayout(self)
        main.addWidget(self.line_url)
        main.addWidget(self.web)

        self.showMaximized()
        self.web.setFocus()


    def adjustTitle(self):
        self.adjustLocation()
        self.setWindowTitle(self.web.title())

    def adjustLocation(self):
        self.line_url.setText(str(self.web.url().url()))

    def changeLocation(self):
        url = self.line_url.text()
        self.web.load(QtCore.QUrl(url))
        self.web.setFocus()

    def close(self):
        self.web.deleteLater()
        self.deleteLater()




class MyWebView(QWebEngineView):
    def __init__(self, parent=None, user_id=None):
        super().__init__()

        self.parent = parent
        self.chekLoadFinish = False

        # Connect sql and get data
        os.chdir('/root/PycharmProjects/HearSheep')
        con = sql.connect(os.getcwd() + '/db/db.sqlite3')
        cur = con.cursor()

        with con:
            cur.execute('SELECT login, pass, proxy, user_agent FROM accaunt where user_id=?', (user_id,))
            row = cur.fetchone()
            self.login, self.password, proxy, user_agent = row

        con.close()

        #Path Cookies
        os.chdir('/root/PycharmProjects/HearSheep')
        pathCookies = '/root/PycharmProjects/HearSheep/cookies/' + str(user_id)

        if os.path.exists(pathCookies):
            pass
        else:
            os.chdir('/root/PycharmProjects/HearSheep/cookies')
            os.mkdir(str(user_id))
            pathCookies = '/root/PycharmProjects/HearSheep/cookies/' +str(user_id)

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

        #
        self.page().proxyAuthenticationRequired.connect(self.handleProxyAuthReq)
        self.loadStarted.connect(self.loadStart)
        self.loadFinished.connect(self.loadFinish)
        self.load(QtCore.QUrl('https://vk.com'))

    def handleProxyAuthReq(self, url, auth, proxyhost):
        auth.setUser(self.proxy.user())
        auth.setPassword(self.proxy.password())

    def loadStart(self):
        self.chekLoadFinish = False

    def loadFinish(self):
        self.chekLoadFinish = True

        if self.page().url().url() == 'https://vk.com/':
            self._auth()

    def _auth(self):
        page = self.page()
        page.runJavaScript(
            'document.querySelector("#index_email").value = "{}"'.format(self.login))
        page.runJavaScript(
            'document.querySelector("#index_pass").value = "{}"'.format(self.password))
        page.runJavaScript(
            'document.querySelector("#index_login_button").click()')


class Password(QWidget):
    def __init__(self, parent=None):
        QWindow.__init__(self, parent)

        QShortcut(QtGui.QKeySequence(Qt.Key_Escape), self).activated.connect(self.close)


        pas = ''

        for x in range(16):  # Количество символов (16)
            pas = pas + random.choice(list('1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ'))

        lbl = QLabel('Новый Пароль')
        edit_text = QLineEdit()
        edit_text.setText(pas)

        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(edit_text)

        self.show()

