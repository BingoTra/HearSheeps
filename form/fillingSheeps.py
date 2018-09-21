import json
import re
import sqlite3 as sql
import sys
import time

import requests
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QShortcut, QFileDialog, QWidget, QPushButton, \
    QVBoxLayout
from requests import Session

import MyData
from api import UrlAPI, API
from customWidget.items import ItemAcc, ItemDialog
from form.addAccauntForm import AddAccauntForm
from form.addGroup import HAddGroup
from form.hPost import HAddPost
from form.infoForm import InfoForm
from hRequester import HRequester
from methodHandler import MethodHandler


class Main(QWidget):
    def __init__(self, parent=None):
        QWindow.__init__(self, parent)

        self.parent = parent

        self.chil = [item for item in self.parent.itemList if item.b.checkState() == 2 and item.frozen == 0]

        QShortcut(QtGui.QKeySequence(Qt.Key_Escape), self).activated.connect(self.close)

        self.gui()

    def gui(self):

        self.btn_go = QPushButton('Go')

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.btn_go)

        self.setLayout(mainLayout)

        self.show()

    def loadFromBd(self):
        con = sql.connect('db/db.sqlite3')
        cur = con.cursor()





App = QApplication(sys.argv)
Prim = Main()
sys.exit(App.exec_())