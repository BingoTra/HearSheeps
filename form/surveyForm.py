import sqlite3 as sql

import shutil

import os
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidgetItem, QWidget, QLabel, \
    QPushButton, QHBoxLayout, QFormLayout, QScrollArea, QVBoxLayout

from customWidget.items import ItemAcc


class SurveyForm(QWidget):
    def __init__(self, parent=None, masAccaunt=None):
        QWidget.__init__(self, parent)

        self.parent = parent
        self.masAcc = masAccaunt

        self.ui()
        self.loadAccaunt()

        self.closeBtn.clicked.connect(lambda: self.parent.widgetsConductor(self, delete=True))

    def ui(self):
        self.myForm = QFormLayout()

        # Close btn
        self.closeBtn = QPushButton('Закрыть')
        closeLay = QHBoxLayout()
        closeLay.addWidget(self.closeBtn, alignment=Qt.AlignRight)
        wCloseLay = QWidget()
        wCloseLay.setLayout(closeLay)

        # Create scroll
        scrollWidget = QWidget()
        scrollWidget.setLayout(self.myForm)
        scroll = QScrollArea()
        scroll.setWidget(scrollWidget)
        scroll.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

        self.myForm.addWidget(wCloseLay)

    def loadAccaunt(self):
        mas = []
        for acc in self.masAcc:
            suevayItem = SueveyItem(self, acc)
            self.myForm.addWidget(suevayItem)

    def select(self, suevayItem):
        self.parent.listAccaunt.clear()

        for item in self.parent.masAccaunts:

            if item['user_id'] == suevayItem.acc.user_id:
                itemW = QListWidgetItem()
                itemW.setSizeHint(QtCore.QSize(100, 40))
                myItem = ItemAcc(self.parent, item)
                self.parent.itemList.append(myItem)
                self.parent.listAccaunt.addItem(itemW)
                self.parent.listAccaunt.setItemWidget(itemW, myItem)


class SueveyItem(QWidget):
    def __init__(self, parent=None, acc=None):
        QWidget.__init__(self, parent)

        self.acc = acc
        self.proxy= ''
        self.parent = parent
        self.con = sql.connect('db/db.sqlite3')

        self.ui()
        self.setName()

        self.btn_select.clicked.connect(lambda: self.parent.select(self))
        self.btn_delete.clicked.connect(self.delete)

    def ui(self):
        self.labelName = QLabel()
        self.btn_select = QPushButton('Выбрать')
        self.btn_delete = QPushButton('Удалить')

        mainLayout = QHBoxLayout(self)
        mainLayout.addWidget(self.labelName)
        mainLayout.addWidget(self.btn_select)
        mainLayout.addWidget(self.btn_delete)

    def setName(self):

        with self.con:
            cur = self.con.cursor()
            cur.execute('SELECT name, last_name, proxy FROM accaunt where user_id=?', (self.acc.user_id,))
            row = cur.fetchone()

            self.labelName.setText(str(self.acc.user_id) + ' ' + row[0] + ' ' + row[1])
            self.proxy = row[2]

    def delete(self):

        with self.con:
            cur = self.con.cursor()
            cur.execute('INSERT INTO free_proxy VALUES(?)', (self.proxy,))
            cur.execute('DELETE FROM accaunt WHERE user_id=?', (self.acc.user_id,))

            os.chdir('/root/PycharmProjects/HearSheep/cookies')
            try:
                shutil.rmtree('/root/PycharmProjects/HearSheep/cookies/'+str(self.acc.user_id), ignore_errors=False, onerror=None)
            except FileNotFoundError:
                pass

            self.con.commit()

        self.deleteLater()
