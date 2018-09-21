import re
import sqlite3 as sql

from PyQt5 import uic, QtCore
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QApplication, QTabWidget, QVBoxLayout, QShortcut
from requests import Session

from methodHandler import MethodHandler


class AddAccauntForm(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.ui()

        self.con = sql.connect('db/db.sqlite3')

        self.btn_add_multi.clicked.connect(self.addAccauntMulti)

        self.quit = QShortcut(QKeySequence(QtCore.Qt.Key_Escape), self)
        self.quit.activated.connect(self.close)

        self.show()

    def ui(self):
        uic.loadUi("uiForm/addAccauntForm.ui", self)
        a = QApplication.desktop().availableGeometry()
        self.setGeometry(a.width() / 6, (a.height() / 4) - (a.height() / 2) / 2, (2 * a.width()) / 3, a.height())

        # Tabs
        tab = QTabWidget()
        tab.addTab(self.multiFrame, "Аккаунты")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(tab)

        self.setLayout(mainLayout)

        self.close()

    def addAccauntMulti(self):
        lpt = self.textEdit_login.toPlainText()
        ppt = self.textEdit_pass.toPlainText()
        prpt = self.textEdit_proxy.toPlainText()
        uapt = self.textEdit_user_agent.toPlainText()
        proxies = re.split('\n', prpt)
        user_agents = uapt.strip('\n')

        if ppt == '':
            logins = re.split('\n', lpt)
            passwords = []

            print(logins)

            for i in range(len(logins)):
                split = re.split(':', logins[i].strip('\n'))
                logins[i] = split[0].strip('\n')
                passwords.append(split[1])

            print(logins)
            print(passwords)
        else:
            logins = re.split('\n', lpt)
            passwords = re.split('\n', ppt)


        for i in range(len(logins)):
            s = Session()
            s.proxies.update(http=proxies[i], https=proxies[i], all=proxies[i])
            s.headers.update({'User-Agent': user_agents})

            try:
                token_and_user_id = MethodHandler.getAccessToken(s, logins[i], passwords[i])
                print(token_and_user_id, 'token and user_id')
                token = token_and_user_id[0]
                user_id = token_and_user_id[1]

                try:
                    if type(int(user_id)) == int:
                        print('Успешно', logins[i], proxies[i])
                except:
                    print('Неуспешно', logins[i], proxies[i])

            except KeyError:
                print(KeyError, logins[i], proxies[i])
                continue


            with self.con:
                print(user_id, '', '', logins[i], passwords[i], proxies[i], user_agents, token, 0, 0)

                try:
                    cur = self.con.cursor()
                    cur.execute("INSERT INTO accaunt VALUES(?,?,?,?,?,?,?,?,?,?,?)", (
                        user_id, '', '', '', str(logins[i]), str(passwords[i]), proxies[i], user_agents, token, 0, 0))
                except:
                    cur.execute('UPDATE accaunt SET token=? WHERE user_id=?', (token, user_id))

                self.con.commit()

            self.close()
