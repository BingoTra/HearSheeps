import sqlite3 as sql

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QHBoxLayout, QLabel, QCheckBox, QVBoxLayout

import MyData
from customWidget.clickableLabel import ClickableLabel


class ItemAcc(QWidget):
    def __init__(self, parent=None, info=None):
        QListWidgetItem.__init__(self, parent)

        self.pixmap = QtGui.QPixmap()
        self.name = info['name']
        self.login = info['login']
        self.proxy = info['proxy']
        self.token = info['token']
        self.frozen = info['frozen']
        self.session = info['session']
        self.user_id = info['user_id']
        self.password = info['password']
        self.nickname = info['nickname']
        self.readiness = info['readiness']
        self.last_name = info['last_name']
        self.user_agent = info['user_agent']

        if self.name == '':
            self.name = self.login
            self.last_name = ''

        self.ui()

        self.icon.clicked.connect(self.chekFrozen)

    def ui(self):
        self.icon = ClickableLabel()
        self.lbl_nickname = QLabel(self.nickname)
        self.lbl_name = QLabel(self.name + ' ' + self.last_name)
        self.lbl_user_id = QLabel(str(self.user_id))
        self.b = QCheckBox()

        if self.frozen == 0 or self.frozen == None:
            self.icon.setStyleSheet("background-color:" + self.getHexColor(self.readiness) + ";")
        elif self.frozen == 1:
            self.pixmap.load('src/frozen.png')
            myPixmap = self.pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.icon.setPixmap(myPixmap)

        layIN = QHBoxLayout()
        layIN.addWidget(self.icon, alignment=Qt.AlignLeft)
        layIN.addWidget(self.lbl_nickname)
        layIN.addWidget(self.lbl_name)
        layIN.addWidget(self.lbl_user_id)

        lay = QHBoxLayout()
        lay.addLayout(layIN)
        lay.addWidget(self.b, alignment=Qt.AlignRight)

        self.setLayout(lay)

    def getHexColor(self, readiness):
        r = 0
        g = 0
        b = 0
        m = int(255 / 25)

        if readiness <= 25:
            r = 255 - m * readiness
            g = 255
            b = 0

        elif 25 < readiness <= 50:
            r = 0
            g = 255
            b = m * (readiness - 25)

        elif 50 < readiness <= 75:
            r = 0
            g = 255 - m * (readiness - 50)
            b = 255

        elif 75 < readiness <= 98:
            r = m * (readiness - 75)
            g = 0
            b = 255

        if readiness == 99:
            r = 207
            g = 0
            b = 222

        return str("#{:02x}{:02x}{:02x}".format(r, g, b))

    def chekFrozen(self):
        con = sql.connect(MyData.CWD + '/db/db.sqlite3')
        cur = con.cursor()

        with con:

            if self.frozen == 0 or self.frozen == None:
                cur.execute("UPDATE accaunt SET frozen=? WHERE user_id=?", (1, self.user_id))
                self.frozen = 1
                self.pixmap.load('src/frozen.png')
                myPixmap = self.pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.FastTransformation)
                self.icon.setPixmap(myPixmap)
                con.commit()

            elif self.frozen == 1:
                cur.execute("UPDATE accaunt SET frozen=? WHERE user_id=?", (0, self.user_id))
                self.frozen = 0
                self.pixmap.load('src/sheep_icon.png')
                myPixmap = self.pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.FastTransformation)
                self.icon.setPixmap(myPixmap)
                con.commit()


class ItemDialog(QWidget):
    def __init__(self, parent=None):
        QListWidgetItem.__init__(self, parent)

        layNameMessage = QVBoxLayout()
        self.user_id = 0
        self.name = QLabel()
        self.message = QLabel()
        self.layMessage = QHBoxLayout()
        self.layMessage.addWidget(self.message, alignment=Qt.AlignLeft)

        layNameMessage.addWidget(self.name)
        layNameMessage.addLayout(self.layMessage)

        allLayout = QHBoxLayout()
        allLayout.addLayout(layNameMessage)

        self.w = QWidget()
        self.w.setLayout(allLayout)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.w)

        self.setLayout(mainLayout)

    def setUnread(self, unread):

        if unread > 0:
            self.w.setStyleSheet("background-color:" + MyData.COLOR_BACKGROUND + ";")

    def setReadState(self, readState):
        if readState == 0:
            myAvatar = QLabel()
            pixmap = QPixmap()

            self.layMessage.insertWidget(0, myAvatar, alignment=Qt.AlignLeft)
            pixmap.load('src/sheep_icon.png')
            myPixmap = pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.FastTransformation)
            myAvatar.setPixmap(myPixmap)

            self.message.setStyleSheet('color:gray;')

    def setName(self, name, user_id):
        self.user_id = user_id
        self.name.setText("<p> <strong>" + name + "</strong></p>")

    def setMessage(self, message):

        self.message.setText(message)
