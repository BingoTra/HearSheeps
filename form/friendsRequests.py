import json
import random
import sqlite3 as sql
import time

import copy
from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QScrollArea, QHBoxLayout, QPushButton

from api import UrlAPI
from customWidget.items import ItemAcc
from hRequester import HRequester, HPostRequester


class FriendsRequests(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.parent = parent

        self.ui()

        self.btn_randomFriends.clicked.connect(
            lambda: self.parent.widgetsConductor(RandomFriends(self.parent), show=True))
        self.btn_differentNames.clicked.connect(
            lambda: self.parent.widgetsConductor(DifferentNames(self.parent), show=True))
        self.btn_standartInfo.clicked.connect(
            lambda: self.parent.widgetsConductor(StandartInfo(self.parent), show=True))
        self.btn_autoAdd.clicked.connect(
            lambda: self.parent.widgetsConductor(AutoAdd(self.parent), show=True))

    def ui(self):
        self.btn_differentNames = QPushButton('Разные имена')
        self.btn_randomFriends = QPushButton('Рандомные имена')
        self.btn_standartInfo = QPushButton('Обычная информация')
        self.btn_autoAdd = QPushButton('Автоматическое Добавление')

        mainLay = QHBoxLayout()
        mainLay.addWidget(self.btn_differentNames)
        mainLay.addWidget(self.btn_standartInfo)
        mainLay.addWidget(self.btn_randomFriends)
        mainLay.addWidget(self.btn_autoAdd)

        self.setLayout(mainLay)


class DifferentNames(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.con = sql.connect('db/db.sqlite3')
        self.parent = parent
        self.number_of_additions = 3
        self.chil = [item for item in self.parent.itemList if item.b.checkState() == 2 and item.frozen == 0]
        self.mainNames = ['Сергей', 'Алексей', 'Виталий', 'Максим', 'Данил', 'Данила', 'Денис', 'Екатерина',
                          'Александр', 'Роман']

        self.ui()
        self.sendRequests()

        self.btn_close.clicked.connect(lambda: self.parent.widgetsConductor(self, delete=True))

    def ui(self):
        self.btn_close = QPushButton('Закрыть')

        mainLay = QVBoxLayout()
        mainLay.addWidget(self.btn_close, alignment=Qt.AlignRight)

        self.setLayout(mainLay)

    def sendRequests(self):
        otherAccList = []
        requester = HRequester()

        with self.con:
            cur = self.con.cursor()
            cur.execute('SELECT * FROM friends')
            friendsRelation = cur.fetchall()

        # Function to find relation of users and added in requester
        def added(acc1, acc2, amountAdded):

            if acc1.user_id == acc2.user_id:
                return 'next'

            elif str(acc1.user_id) + '_' + str(acc2.user_id) in friendsRelation:
                return 'next'

            elif str(acc2.user_id) + '_' + str(acc1.user_id) in friendsRelation:
                return 'next'

            else:
                getUrl = UrlAPI(acc.token)
                requester(getUrl.friends.add(user_id=acc2.user_id), acc1.session, acc1.user_id, acc2.user_id)
                amountAdded += 1

                if amountAdded < self.number_of_additions:
                    return 'amountAdded'

                if amountAdded == self.number_of_additions:
                    return 'complete'

        # search for accounts that do not have main names
        for acc in self.parent.masAccaunts:

            if acc['name'] in self.mainNames:
                pass
            else:
                otherAccList.append(ItemAcc(self, acc))

        # accounts iterate and call function 'added'
        for acc in self.chil:
            print(acc)
            amountAdded = 0

            for otherAcc in otherAccList:
                result = added(acc, otherAcc, amountAdded)
                print(result)

                if result == 'complete':
                    break

                elif result == 'next':
                    continue

                elif result == 'amountAdded':
                    amountAdded += 1

        response = requester.request()
        successfully = 0
        error = 0

        for r in response:
            j = json.loads(r[0].text)
            user_id1, user_id2 = r[2]
            print(user_id1, user_id2)

            if 'response' in j:

                if j['response'] == 1:
                    successfully += 1

                    with self.con:
                        cur = self.con.cursor()
                        cur.execute('INSERT INTO friends VALUES(?,?)', (user_id1, user_id2))
                        self.con.commit()

                else:
                    print(j)
                    error += 1

            else:
                print(j)
                error += 1

        if error == 0:
            print('Успешно у всех. Кол-во выбранных:', str(len(self.chil)), 'Кол-во удачно отправленных:',
                  str(successfully / 3))
        else:
            print('Кол-во выбранных:', str(len(self.chil)), 'Кол-во удачно отправленных:', str(successfully / 3),
                  'Кол-во ошибок', str(error / 3))


class RandomFriends(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.ui()
        self.widgetList = []
        self.nuberOfCall = 0
        self.parent = parent
        self.members = {'items': []}
        requester = HRequester()
        postRequester = HPostRequester()

        self.closeBtn.clicked.connect(lambda: self.parent.widgetsConductor(self, delete=True))
        self.btn_sendRequestEverything.clicked.connect(self.sendRequestEverything)
        self.btn_unsubscribeEverything.clicked.connect(self.unsubscribeEverything)
        self.btn_resevedOneFriend.clicked.connect(self.resevedOneFriend)

        chil = [item for item in self.parent.itemList if item.b.checkState() == 2 and item.frozen == 0]

        for item in chil:
            getUrl = UrlAPI(item.token)
            postRequester(getUrl.execute(), item.session, item, data={'code': self.getCode()})

        response = postRequester.request()
        response.sort(key=lambda r: json.loads(r[0].text)['response'][0]['count'])

        for r in response:
            j = json.loads(r[0].text)['response']
            item = r[2][0]
            masSended = [sended for sended in j[1]['items']]
            masReceived = [received for received in j[2]['items']]

            self.addAccaunt(item, str(j[0]['count']), str(j[1]['count']), str(j[2]['count']), masSended, masReceived)

            for inf in j[3]['items']:
                try:
                    if inf['online'] == 1 and inf['city']['id'] == 1:
                        self.members['items'].append(inf)
                except KeyError:
                    pass

            for inf in j[4]['items']:
                try:
                    if inf['online'] == 1 and inf['city']['id'] == 1:
                        self.members['items'].append(inf)
                except KeyError:
                    pass

            for inf in j[5]['items']:
                try:
                    if inf['online'] == 1 and inf['city']['id'] == 1:
                        self.members['items'].append(inf)
                except KeyError:
                    pass

        self.parent.statusBar.showMessage(
            'Загруженно акков ' + str(len(response)) + '/' + str(len(chil)) + ' Чел онлайн:' + str(
                len(self.members['items'])))

    def getCode(self):
        self.nuberOfCall += 1000
        self.code = '''
            var friends = API.friends.get();
            var sended  = API.friends.getRequests({"count":1000, "out":1});
            var recived = API.friends.getRequests({"count":1000, "out":0});
            var members1 = API.groups.getMembers({"group_id":24608732, "sort":"id_desc", "fields":"online,city", "offset":''' + str(
            self.nuberOfCall) + '''});
            var members2 = API.groups.getMembers({"group_id":52255475, "sort":"id_desc", "fields":"online,city", "offset":''' + str(
            self.nuberOfCall) + '''});
            var members3 = API.groups.getMembers({"group_id":132909030, "sort":"id_desc", "fields":"online,city", "offset":''' + str(
            self.nuberOfCall) + '''});
            var members4 = API.groups.getMembers({"group_id":34985835, "sort":"id_desc", "fields":"online,city", "offset":''' + str(
            self.nuberOfCall) + '''});

            return [friends,sended,recived,members1,members2,members3,members4];
            '''
        return self.code

    def ui(self):
        self.myForm = QFormLayout()

        # Close btn
        self.closeBtn = QPushButton('Закрыть')
        self.btn_sendRequestEverything = QPushButton('+3 отпрвить')
        self.btn_unsubscribeEverything = QPushButton('-5 исходящих')
        self.btn_resevedOneFriend = QPushButton('+1 добавить')
        closeLay = QHBoxLayout()
        closeLay.addWidget(self.btn_sendRequestEverything, alignment=Qt.AlignLeft)
        closeLay.addWidget(self.btn_unsubscribeEverything, alignment=Qt.AlignLeft)
        closeLay.addWidget(self.btn_resevedOneFriend, alignment=Qt.AlignLeft)
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

    def addAccaunt(self, item, countFriends, sendedRequests, receivedRequests, masSended, masReceived):
        w = Item(self, item, countFriends, sendedRequests, receivedRequests, masSended, masReceived)
        self.myForm.addWidget(w)
        self.widgetList.append(w)

    def sendRequestEverything(self):
        requester = HRequester()
        countCaptcha = 0
        countSuccessfully = 0

        for w in self.widgetList:
            getUrl = UrlAPI(w.item.token)

            for i in range(3):
                user = random.choice(self.members['items'])
                requester(getUrl.friends.add(user_id=user['id']), w.item.session, w)

        response = requester.request()
        for r in response:
            w = r[2][0]
            j = json.loads(r[0].text)

            if 'error' in j:

                if j['error']['error_code'] == 14:
                    countCaptcha += 1
                else:
                    print(j)

            elif 'response' in j:

                if j['response'] == 1:
                    countSuccessfully += 1
                    w.countSendedRequests.setText(str(int(w.countSendedRequests.text()) + 1))

                elif j['response'] == 2:
                    print('Добавлен ранее')

                else:
                    print(j)

            else:
                print(j)

        if countSuccessfully / len(self.widgetList) == 3:
            self.parent.statusBar.showMessage('Успешно отправлено у всех')
            print('Успешно отправлено у всех')
        else:
            self.parent.statusBar.showMessage(
                'Кол-во успешных:' + str(countSuccessfully) + ' Кол-во капч:' + str(countCaptcha))
            print('Кол-во успешных:' + str(countSuccessfully) + ' Кол-во капч:' + str(countCaptcha))

    def unsubscribeEverything(self):
        requester = HRequester()
        countCaptcha = 0
        countLimitRequests = 0
        countSuccessfully = 0

        for w in self.widgetList:
            getUrl = UrlAPI(w.item.token)

            for i in range(5):
                try:
                    user = w.masSended.pop(0)
                    requester(getUrl.friends.delete(user_id=user), w.item.session, w)
                except:
                    break

        response = requester.request()
        for r in response:
            w = r[2][0]
            j = json.loads(r[0].text)

            if 'error' in j:

                if j['error']['error_code'] == 14:
                    countCaptcha += 1

                elif j['error']['error_code'] == 6:
                    countLimitRequests += 1

                else:
                    print(j)

            elif 'response' in j:

                if j['response']['success'] == 1:
                    countSuccessfully += 1
                    w.countSendedRequests.setText(str(int(w.countSendedRequests.text()) - 1))

                else:
                    print(j)

            else:
                print(j)

        if countSuccessfully / len(response) == 1:
            self.parent.statusBar.showMessage('Успешно удалено у всех')
            print('Успешно удалено у всех')
        else:
            self.parent.statusBar.showMessage('Кол-во успешных:' + str(countSuccessfully) + ' Кол-во капч:' + str(
                countCaptcha) + ' Кол-во лимитов:' + str(countLimitRequests))
            print('Кол-во успешных:' + str(countSuccessfully) + ' Кол-во капч:' + str(
                countCaptcha) + ' Кол-во лимитов:' + str(countLimitRequests))

    def resevedOneFriend(self):
        requester = HRequester()
        countCaptcha = 0
        countLimitRequests = 0
        countSuccessfully = 0

        widgetList = [w for w in self.widgetList if len(w.masReceived) > 0]

        for w in widgetList:
            getUrl = UrlAPI(w.item.token)
            added_user_id = w.masReceived.pop(0)

            requester(getUrl.friends.add(user_id=added_user_id), w.item.session, w, added_user_id)

        response = requester.request()
        for r in response:
            w = r[2][0]
            added_user_id = r[2][1]
            j = json.loads(r[0].text)

            if 'error' in j:

                if j['error']['error_code'] == 14:
                    countCaptcha += 1

                elif j['error']['error_code'] == 6:
                    countLimitRequests += 1

                elif j['error']['error_code'] == 177:
                    getUrl = UrlAPI(w.item.token)
                    rDel = w.item.session.get(getUrl.friends.delete(user_id=added_user_id),
                                              proxies=w.item.session.proxies)
                    countSuccessfully += 1

                else:
                    print(j)

            elif 'response' in j:

                if j['response'] > 1:
                    countSuccessfully += 1
                    w.countReceivedRequests.setText(str(int(w.countReceivedRequests.text()) - 1))

                else:
                    print(j)

            else:
                print(j)

        if countSuccessfully / len(response) == 1:
            self.parent.statusBar.showMessage('Успешно добавлено у всех')
            print('Успешно добавлено у всех')
        else:
            self.parent.statusBar.showMessage('Кол-во успешных:' + str(countSuccessfully) + ' Кол-во капч:' + str(
                countCaptcha) + ' Кол-во лимитов:' + str(countLimitRequests))
            print('Кол-во успешных:' + str(countSuccessfully) + ' Кол-во капч:' + str(
                countCaptcha) + ' Кол-во лимитов:' + str(countLimitRequests))


class StandartInfo(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.ui()
        self.widgetList = []
        self.nuberOfCall = 0
        self.parent = parent
        requester = HRequester()
        postRequester = HPostRequester()

        self.closeBtn.clicked.connect(lambda: self.parent.widgetsConductor(self, delete=True))
        self.btn_unsubscribeEverything.clicked.connect(self.unsubscribeEverything)
        self.btn_resevedOneFriend.clicked.connect(self.resevedOneFriend)

        chil = [item for item in self.parent.itemList if item.b.checkState() == 2 and item.frozen == 0]

        for item in chil:
            getUrl = UrlAPI(item.token)
            postRequester(getUrl.execute(), item.session, item, data={'code': self.getCode()})

        response = postRequester.request()
        response.sort(key=lambda r: json.loads(r[0].text)['response'][0]['count'])

        for r in response:
            j = json.loads(r[0].text)['response']
            item = r[2][0]
            masSended = [sended for sended in j[1]['items']]
            masReceived = [received for received in j[2]['items']]

            self.addAccaunt(item, str(j[0]['count']), str(j[1]['count']), str(j[2]['count']), masSended, masReceived)

        self.parent.statusBar.showMessage(
            'Загруженно акков ' + str(len(response)) + '/' + str(len(chil)))

    def getCode(self):
        self.code = '''
            var friends = API.friends.get();
            var sended  = API.friends.getRequests({"count":1000, "out":1});
            var recived = API.friends.getRequests({"count":1000, "out":0});

            return [friends,sended,recived];
            '''
        return self.code

    def ui(self):
        self.myForm = QFormLayout()

        # Close btn
        self.closeBtn = QPushButton('Закрыть')
        self.btn_unsubscribeEverything = QPushButton('-5 исходящих')
        self.btn_resevedOneFriend = QPushButton('+1 добавить')
        closeLay = QHBoxLayout()
        closeLay.addWidget(self.btn_unsubscribeEverything, alignment=Qt.AlignLeft)
        closeLay.addWidget(self.btn_resevedOneFriend, alignment=Qt.AlignLeft)
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

    def addAccaunt(self, item, countFriends, sendedRequests, receivedRequests, masSended, masReceived):
        w = Item(self, item, countFriends, sendedRequests, receivedRequests, masSended, masReceived)
        self.myForm.addWidget(w)
        self.widgetList.append(w)

    def unsubscribeEverything(self):
        requester = HRequester()
        countCaptcha = 0
        countLimitRequests = 0
        countSuccessfully = 0

        for w in self.widgetList:
            getUrl = UrlAPI(w.item.token)

            for i in range(5):
                try:
                    user = w.masSended.pop(0)
                    requester(getUrl.friends.delete(user_id=user), w.item.session, w)
                except:
                    break

        response = requester.request()
        for r in response:
            w = r[2][0]
            j = json.loads(r[0].text)

            if 'error' in j:

                if j['error']['error_code'] == 14:
                    countCaptcha += 1

                elif j['error']['error_code'] == 6:
                    countLimitRequests += 1

                else:
                    print(j)

            elif 'response' in j:

                if j['response']['success'] == 1:
                    countSuccessfully += 1
                    w.countSendedRequests.setText(str(int(w.countSendedRequests.text()) - 1))

                else:
                    print(j)

            else:
                print(j)

        if countSuccessfully / len(response) == 1:
            self.parent.statusBar.showMessage('Успешно удалено у всех')
            print('Успешно удалено у всех')
        else:
            self.parent.statusBar.showMessage('Кол-во успешных:' + str(countSuccessfully) + ' Кол-во капч:' + str(
                countCaptcha) + ' Кол-во лимитов:' + str(countLimitRequests))
            print('Кол-во успешных:' + str(countSuccessfully) + ' Кол-во капч:' + str(
                countCaptcha) + ' Кол-во лимитов:' + str(countLimitRequests))

    def resevedOneFriend(self):
        requester = HRequester()
        countCaptcha = 0
        countLimitRequests = 0
        countSuccessfully = 0

        widgetList = [w for w in self.widgetList if len(w.masReceived) > 0]

        for w in widgetList:
            getUrl = UrlAPI(w.item.token)
            added_user_id = w.masReceived.pop(0)

            requester(getUrl.friends.add(user_id=added_user_id), w.item.session, w, added_user_id)

        response = requester.request()
        for r in response:
            w = r[2][0]
            added_user_id = r[2][1]
            j = json.loads(r[0].text)

            if 'error' in j:

                if j['error']['error_code'] == 14:
                    countCaptcha += 1

                elif j['error']['error_code'] == 6:
                    countLimitRequests += 1

                elif j['error']['error_code'] == 177:
                    getUrl = UrlAPI(w.item.token)
                    rDel = w.item.session.get(getUrl.friends.delete(user_id=added_user_id),
                                              proxies=w.item.session.proxies)
                    countSuccessfully += 1

                else:
                    print(j)

            elif 'response' in j:

                if j['response'] > 1:
                    countSuccessfully += 1
                    w.countReceivedRequests.setText(str(int(w.countReceivedRequests.text()) - 1))

                else:
                    print(j)

            else:
                print(j)

        if countSuccessfully / len(response) == 1:
            self.parent.statusBar.showMessage('Успешно добавлено у всех')
            print('Успешно добавлено у всех')
        else:
            self.parent.statusBar.showMessage('Кол-во успешных:' + str(countSuccessfully) + ' Кол-во капч:' + str(
                countCaptcha) + ' Кол-во лимитов:' + str(countLimitRequests))
            print('Кол-во успешных:' + str(countSuccessfully) + ' Кол-во капч:' + str(
                countCaptcha) + ' Кол-во лимитов:' + str(countLimitRequests))


class AutoAdd(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.otherAccList = []
        self.con = sql.connect('db/db.sqlite3')
        self.parent = parent
        self.number_of_additions = 1
        self.listRecived = []
        self.chil = [item for item in self.parent.itemList if item.b.checkState() == 2 and item.frozen == 0]
        self.mainNames = ['Сергей', 'Алексей', 'Виталий', 'Максим', 'Данил', 'Данила', 'Денис', 'Екатерина',
                          'Александр', 'Роман']

        self.users_id_list = [acc.user_id for acc in self.chil]

        self.run()

    def getAddedUser(self, masReceived):

        for userRecived in masReceived:

            if userRecived in self.users_id_list:
                return userRecived

    def sendRequests(self):
        requester = HRequester()

        with self.con:
            cur = self.con.cursor()
            cur.execute('SELECT * FROM friends')
            friendsRelation = cur.fetchall()

        # Function to find relation of users and added in requester
        def added(acc1, acc2, amountAdded):

            if acc1.user_id == acc2.user_id:
                return 'next'

            elif str(acc1.user_id) + '_' + str(acc2.user_id) in friendsRelation:
                return 'next'

            elif str(acc2.user_id) + '_' + str(acc1.user_id) in friendsRelation:
                return 'next'

            else:
                getUrl = UrlAPI(acc.token)
                requester(getUrl.friends.add(user_id=acc2.user_id), acc1.session, acc1.user_id, acc2.user_id)
                amountAdded += 1

                if amountAdded < self.number_of_additions:
                    return 'amountAdded'

                if amountAdded == self.number_of_additions:
                    return 'complete'

        # search for accounts that do not have main names
        for acc in self.parent.masAccaunts:

            if acc['name'] in self.mainNames:
                pass
            if acc['name'] not in self.mainNames and acc['frozen'] == 0:
                self.otherAccList.append(ItemAcc(self, acc))

        # accounts iterate and call function 'added'
        for acc in self.chil:
            amountAdded = 0
            curOtherList = [i for i in self.otherAccList]

            while curOtherList:
                randomIndex = random.randint(0, len(curOtherList)-1)
                randomAcc = curOtherList.pop(randomIndex)
                result = added(acc, randomAcc, amountAdded)

                if result == 'complete':
                    break

                elif result == 'next':
                    continue

                elif result == 'amountAdded':
                    amountAdded += 1

        response = requester.request()
        successfully = 0
        error = 0

        for r in response:
            j = json.loads(r[0].text)
            user_id1, user_id2 = r[2]

            if 'response' in j:

                if j['response'] <= 2:
                    successfully += 1

                    with self.con:
                        cur = self.con.cursor()
                        cur.execute('INSERT INTO friends VALUES(?,?)', (user_id1, user_id2))
                        self.con.commit()

                else:
                    print(j)
                    error += 1

            else:
                print(j)
                error += 1

        if error == 0:
            print('Успешно у всех. Кол-во выбранных:', str(len(self.chil)), 'Кол-во удачно отправленных:',
                  str(successfully / self.number_of_additions))
        else:
            print('Кол-во выбранных:', str(len(self.chil)), 'Кол-во удачно отправленных:',
                  str(successfully / self.number_of_additions), 'Кол-во ошибок', str(error / self.number_of_additions))

    def addFriends(self):
        requester = HRequester()

        for item in self.chil:
            getUrl = UrlAPI(item.token)
            requester(getUrl.friends.getRequests(count=1000, out=0), item.session, item)

        response = requester.request()

        for r in response:

            try:
                j = json.loads(r[0].text)['response']
                item = r[2][0]
                masReceived = [received for received in j['items']]
                self.listRecived.append([item, masReceived])
            except Exception as e:
                print(e)

        widgetList = [w for w in self.listRecived if len(w[1]) > 0]

        for w in widgetList:
            item, masReceived = w
            getUrl = UrlAPI(item.token)
            added_user_id = self.getAddedUser(masReceived)

            if added_user_id != None:
                requester(getUrl.friends.add(user_id=added_user_id), item.session)

        requester.request()

    def run(self):

        while True:
            print('Отправка запросов')
            self.sendRequests()

            time.sleep(120)

            print('Добавление в друзья')
            self.addFriends()

            time.sleep(3600)


class Item(QWidget):
    clicked = pyqtSignal()

    def __init__(self, parent=None, item=None, countFriends=None, sendedRequests=None, receivedRequests=None,
                 masSended=None, masReceived=None):
        QWidget.__init__(self, parent)
        uic.loadUi("uiForm/friendsRequests.ui", self)

        self.parent = parent
        self.masSended = masSended
        self.masReceived = masReceived
        self.item = item

        self.name.setText(self.item.name)
        self.last_name.setText(self.item.last_name)
        self.lbl_id.setText(str(self.item.user_id))
        self.countFriends.setText(countFriends)
        self.countSendedRequests.setText(sendedRequests)
        self.countReceivedRequests.setText(receivedRequests)

        lay = QVBoxLayout(self)
        lay.addWidget(self.mainWidget)

        self.btn_add.clicked.connect(self.addFriends)
        self.btn_unsubscribe.clicked.connect(self.unsubscribe)
        self.btn_sendRequests.clicked.connect(self.sendRequest)
        self.mark_user_btn.clicked.connect(lambda: self.item.b.setChecked(True))

    def addFriends(self):
        getUrl = UrlAPI(self.item.token)

        try:
            added_user_id = self.masReceived.pop(0)
        except IndexError:
            return

        r = self.item.session.get(getUrl.friends.add(user_id=added_user_id), proxies=self.item.session.proxies)
        j = json.loads(r.text)

        if 'error' in j:
            if 'error_code' in j['error'] and j['error']['error_code'] == 177:
                print('Баненный акк')
                rDel = self.item.session.get(getUrl.friends.delete(user_id=added_user_id),
                                             proxies=self.item.session.proxies)
            else:
                print(j)
        elif 'response' in j:
            if j['response'] > 1:
                print('Добавлен')

        self.countReceivedRequests.setText(str(int(self.countReceivedRequests.text()) - 1))

    def sendRequest(self):
        getUrl = UrlAPI(self.item.token)
        requester = HRequester()

        for i in range(3):
            user = random.choice(self.parent.members['items'])
            requester(getUrl.friends.add(user_id=user['id']), self.item.session)

        response = requester.request()
        for r in response:
            j = json.loads(r[0].text)

            if 'error' in j:

                if j['error']['error_code'] == 14:
                    print('КАПЧА-----')
                else:
                    print(j)

            elif 'response' in j:

                if j['response'] == 1:
                    print('Запрос отправлен')
                    self.countSendedRequests.setText(str(int(self.countSendedRequests.text()) + 1))
                else:
                    print(j)

            else:
                print(j)

    def unsubscribe(self):
        getUrl = UrlAPI(self.item.token)
        unsubscribe_user_id = self.masSended.pop(0)

        r = self.item.session.get(getUrl.friends.delete(user_id=unsubscribe_user_id), proxies=self.item.session.proxies)
        j = json.loads(r.text)

        if 'response' in j:

            if j['response']['success'] == 1:
                print('Удален')
            else:
                print('Ошибка', j)

        else:
            print('Ошибка', j)

        self.countSendedRequests.setText(str(int(self.countSendedRequests.text()) - 1))
