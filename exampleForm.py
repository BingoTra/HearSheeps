import json
import re
import sqlite3 as sql
import sys
import time

import requests
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QShortcut, QFileDialog, QWidget
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
        a = QApplication.desktop().availableGeometry()
        self.setGeometry(300, 100, a.width() / 2, a.height()/2)
        QShortcut(QtGui.QKeySequence(Qt.Key_Escape), self).activated.connect(self.close)


        self.show()




App = QApplication(sys.argv)
Prim = Main()
Prim.show()
sys.exit(App.exec_())
