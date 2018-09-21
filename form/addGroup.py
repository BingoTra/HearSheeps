import json
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QKeySequence, QPixmap
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout, QFrame, QTabWidget, QShortcut, QApplication, \
    QFileDialog, QLabel
from PyQt5.QtCore import Qt
from hRequester import HRequester
from api import UrlAPI

class HAddGroup(QWidget):

    def __init__(self, parent=None, mas=None):
        super().__init__(parent, Qt.Window)
        self.ui()
        self.masSessions = mas
        self.requester = HRequester()

        self.btn_send.clicked.connect(self.leaveGroup)

        self.show()

    def ui(self):

        mainLayout = QVBoxLayout(self)

        self.btn_send = QPushButton('Send')
        self.btn_send.setFocus()
        self.line = QLineEdit()


        mainLayout.addWidget(self.btn_send)
        mainLayout.addWidget(self.line)

        self.line.setFocus()


    def leaveGroup(self):

        for mas in self.masSessions:
            session = mas[0]
            token   = mas[1]
            getUrl = UrlAPI(token)
            url = getUrl.groups.leave(group_id=self.line.text())
            self.requester(url, session)

        response = self.requester.request()
        for item in response:
            try:
                res = json.loads(item[0].text)

                if res['response'] == 1:
                    print('Успешно')
                else:
                    print(res)
            except:
                print('Ошибка', item[0].text)







