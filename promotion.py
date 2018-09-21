import json
import random
import time
from captcha import Captcha

from threading import Thread

from PyQt5.QtWidgets import QShortcut, QCheckBox

from hRequester import HRequester, HPostRequester
from api import UrlAPI

from PyQt5 import QtGui
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QFrame, QApplication


class Promotion(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        a = QApplication.desktop().availableGeometry()
        self.setGeometry(300, 100, a.width() / 2, a.height() / 2)
        QShortcut(QtGui.QKeySequence(Qt.Key_Escape), self).activated.connect(self.close)

        self.parent = parent
        self.numberOfCall = 0
        self.postRequester = HPostRequester()
        self.chil = [item for item in self.parent.itemList if item.b.checkState() == 2 and item.frozen == 0]

        self.ui()
        self.load_data()
        self.synchronization()
        self.threads = []


        self.btn_send.clicked.connect(self.run)

    def ui(self):

        mainLayout = QVBoxLayout(self)

        self.checkBoxOnline = QCheckBox()
        self.btn_send = QPushButton('Go')
        self.btn_send.setFocus()

        mainLayout.addWidget(QLabel('Online'))
        mainLayout.addWidget(self.checkBoxOnline)
        mainLayout.addWidget(self.btn_send)

        self.show()

    def load_data(self):
        self.mas_ids = []
        self.masLikers = []


        with open('files/вк_жен_омск_80к.txt') as file:
            for line in file:
                self.mas_ids.append(line.strip('\n'))

        for chil in self.chil:
            self.masLikers.append(User(chil.name, chil.token, chil.session))

    def synchronization(self):
        mas_completed_names = []

        #Заполняем массив с лайкнутыми аккаунтами
        with open('files/completed') as file:
            for line in file:
                mas_completed_names.append(line.strip('\n'))

        #Исключает из массива айди, которые уже лайкнуты
        for complete_name in mas_completed_names:
            for i in range(len(self.mas_ids)):

                 if complete_name == self.mas_ids[i]:
                    self.mas_ids.pop(i)
                    break


        print(self.mas_ids)

    def getLine(self, n):
        self.numberOfCall += 500
        masUsers = []

        for i in range(self.numberOfCall - 500, self.numberOfCall):
            try:
                masUsers.append(self.mas_ids[i])
            except Exception as exeption:
                print(exeption)
                return '''var friends'''+ str(n) +'''= API.users.get({"user_ids":"''' + ",".join(masUsers) + '''", "fields":"photo_id,online"});'''

        return '''var friends'''+ str(n) +'''= API.users.get({"user_ids":"''' + ",".join(masUsers) + '''", "fields":"photo_id,online"});'''

    def getInfoMembers(self):
        members = []

        for i in range(0, divmod(len(self.mas_ids), 5000)[0] + 1):
            code = 'var mas = [];'

            for j in range(10):
                line = self.getLine(j)

                if line == '''var friends'''+ str(j) +''' = API.users.get({"user_ids":"","fields":"photo_id,online"});''':
                    break
                else:
                    code += line + 'mas = mas + friends' + str(j) + ';'

            code += '''return mas;'''

            print(code)

            random_chil = random.choice(self.chil)

            session = random_chil.session
            getUrl = UrlAPI(random_chil.token)
            self.postRequester(getUrl.execute(), session, 'null', data={'code': code})

            response = self.postRequester.request()
            for r in response:
                print(r[0].text)
                j = json.loads(r[0].text)
                print(len(j['response']))

                [members.append(user) for user in j['response']]

        print(len(members))

        if self.checkBoxOnline.checkState() == 2:
            members = [user for user in members if user['online'] == 1]

        return members

    def fillingLikers(self):
        members = self.getInfoMembers()

        for member in members:
            for liker in self.masLikers:

                if member['first_name'].lower() == liker.name.lower():

                    try:
                        liker.photoIdsList.append(member['photo_id'])
                    except Exception as e:
                        print(e, member)
                        break

        for l in self.masLikers:
            print(l.photoIdsList)

    def run(self):

        thFilling = Thread(target=self.fillingLikers)
        thFilling.setDaemon(True)
        thFilling.start()
        thFilling.join()

        for liker in self.masLikers:
            th = Thread(target=liker.run)
            th.setDaemon(True)
            th.start()

    def analysis(self):
        members = self.getInfoMembers()
        names = {}

        for member in members:

            if member['first_name'].lower() in names:
                names[member['first_name'].lower()] += 1
            else:
                names.update(dict.fromkeys([member['first_name'].lower()], 1))

        filtered = []

        for name in names:
            filtered.append([name,names[name]])

        filtered.sort(key=lambda i: i[1])

        for name in filtered:
            print(name)


class User:
    def __init__(self, name, token, session):
        self.name = name
        self.timeout = 0
        self.interval1 = 75
        self.interval2 = 95
        self.session = session
        self.getUrl = UrlAPI(token)
        self.requester = HRequester()
        self.photoIdsList = []


    def run(self):

        for photo_id in self.photoIdsList:
            self.like(photo_id)
            time.sleep(random.randint(self.interval1, self.interval2))


    def like(self, photo_id):
        captcha = False
        captcha_result = ''
        captcha_sid = ''

        while True:

            owner_id, item_id = photo_id.split('_')

            if captcha == False:
                url = self.getUrl.likes.add(type='photo', owner_id=owner_id, item_id=item_id)
            else:
                url = self.getUrl.likes.add(type='photo', owner_id=owner_id, item_id=item_id, captcha_sid=captcha_sid, captcha_key=captcha_result)

            self.requester(url, self.session)

            response = self.requester.request()
            for r in response:
                j = json.loads(r[0].text)

                try:

                    if 'likes' in j['response']:

                        with open('files/completed', 'a') as file:
                            file.write(str(owner_id) + '\n')

                        print('+', owner_id)
                        return

                except Exception as e:
                    print(e)
                    print(r[0].text)

                    if 'error' in j:

                        if j['error']['error_code'] == 14:
                            print("Решаем капчу")
                            captcha = Captcha()
                            captcha_result = captcha.solve(self.session, j['error']['captcha_img'])
                            captcha_sid = j['error']['captcha_sid']

                            if captcha_result == 'error':
                                self.interval = 2000
                                return
                            else:
                                captcha = True
                                print(self.name, 'Captcha', captcha_result)

                        if j['error']['error_code'] == 15:

                            with open('files/completed', 'a') as file:
                                file.write(str(owner_id) + '\n')

                            print('+', owner_id)
                            return

                        if j['error']['error_code'] == 17:
                            self.interval = 99999
                            return