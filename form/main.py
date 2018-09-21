import io
import json
import os
import random
import re
import sqlite3 as sql
import sys
import time

import requests
from PIL import Image
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QShortcut, QFileDialog, QButtonGroup
from requests import Session

import MyData
from api import UrlAPI
from customWidget.items import ItemAcc, ItemDialog
from form.AvaratForChek import AvatarForChek
from form.addAccauntForm import AddAccauntForm
from form.addGroup import HAddGroup
from form.allAvatarForm import AllAvatarForm
from form.allPhotosForm import AllPhotosForm
from form.allPostForm import RecordsForm
from form.browser import Browser
from form.changeNicknameWidget import ChangeNicknameWidget
from form.changePassword import ChangePassword
from form.changeReadinessWidget import ChangeReadinessWidget
from form.editInfoWidget import EditInfoWidget
from form.friendsRequests import FriendsRequests
from form.hPost import HAddPost
from form.hSettingsPrivacy import SettingsPrivacy
from form.imitatingConversation import ImitatingConversation
from form.infoForm import InfoForm
from form.infoFrozenForm import InfoFrozenForm
from form.likeMachineWidget import LikeMachine
from form.repostsForm import RepostsForm
from form.surveyForm import SurveyForm
from hRequester import HRequester, HPostRequester
from methodHandler import MethodHandler
from promotion import Promotion


class Main(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        MyData.CWD = os.getcwd()
        self.con = sql.connect('db/db.sqlite3')
        self.widgetMas = []

        self.ui()
        self.loadAccaunts()

        self.addPostAct.triggered.connect(self.hPost)
        self.chekAccAct.triggered.connect(self.chekAcc)
        self.editInfoAct.triggered.connect(self.editInfo)
        self.addVideoAct.triggered.connect(self.addVideo)
        self.addGroupAct.triggered.connect(self.addGroup)
        self.dialogsAct.triggered.connect(self.getDialogs)
        self.refreshAct.triggered.connect(self.refreshName)
        self.editPhotoAct.triggered.connect(self.changePhoto)
        self.refreshTokenAct.triggered.connect(self.getToken)
        self.promotionAct.triggered.connect(self.promotion)
        self.cleaningGroupAct.triggered.connect(self.cleaningGroup)
        self.repostsAct.triggered.connect(lambda: RepostsForm(self))
        self.listDialog.itemDoubleClicked.connect(self.dialogHistory)
        self.addAccAct.triggered.connect(lambda: AddAccauntForm(self))
        self.checkAllAct.triggered.connect(lambda: AllAvatarForm(self))
        self.allPostAct.triggered.connect(lambda: RecordsForm(self))
        self.changePassAct.triggered.connect(lambda: ChangePassword(self))
        self.checkWithAvatar.triggered.connect(lambda: AvatarForChek(self))
        self.cleaningPhotoAct.triggered.connect(lambda: AllPhotosForm(self))
        self.settingsPrivacyAct.triggered.connect(lambda: SettingsPrivacy(self))
        self.filterRadioButtonGroup.buttonReleased.connect(self.clickedFilterButton)
        self.imitatingConversation.triggered.connect(lambda: ImitatingConversation(self))
        self.likeMachineAct.triggered.connect(lambda: self.widgetsConductor(LikeMachine(self), show=True))
        self.friendsAct.triggered.connect(lambda: self.widgetsConductor(FriendsRequests(self), show=True))
        self.changeNicknameAct.triggered.connect(lambda: self.widgetsConductor(ChangeNicknameWidget(self), show=True))
        self.changeReadinessAct.triggered.connect(lambda: self.widgetsConductor(ChangeReadinessWidget(self), show=True))

        self.infoFrozenAct.triggered.connect(lambda: self.widgetsConductor(
            InfoFrozenForm(self, self.listAccaunt.itemWidget(self.listAccaunt.currentItem())), show=True))
        self.browserAct.triggered.connect(
            lambda: Browser(self, self.listAccaunt.itemWidget(self.listAccaunt.currentItem()).user_id))
        self.informAct.triggered.connect(
            lambda: InfoForm(self, self.listAccaunt.itemWidget(self.listAccaunt.currentItem()).session,
                             self.listAccaunt.itemWidget(self.listAccaunt.currentItem()).token))

        self.informAct.setShortcut("I")
        self.dialogsAct.setShortcut("D")
        self.friendsAct.setShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_F))
        self.browserAct.setShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_B))
        QShortcut(QtGui.QKeySequence(Qt.Key_Escape), self).activated.connect(self.close)
        QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_N), self).activated.connect(
            lambda: [item.b.nextCheckState() for item in self.itemList])
        QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_A), self).activated.connect(
            lambda: [item.b.setChecked(True) for item in self.itemList])

        self.filterLine.installEventFilter(self)

    def ui(self):
        uic.loadUi("uiForm/mainForm.ui", self)
        a = QApplication.desktop().availableGeometry()
        self.setGeometry(a.width() / 6, 0, (2 * a.width()) / 3, a.height())

        # Menu bar
        bar = self.menuBar()

        accauntMenu = bar.addMenu("Аккаунт")
        orderMenu = bar.addMenu('Всем')
        otherMenu = bar.addMenu('Прочее')

        self.informAct = accauntMenu.addAction('Информация')
        self.browserAct = accauntMenu.addAction('Открыть в браузере')
        self.infoFrozenAct = accauntMenu.addAction('Информация по заморозке')
        self.dialogsAct = accauntMenu.addAction('Диалоги')
        self.addAccAct = accauntMenu.addAction('Добавить')
        self.refreshTokenAct = accauntMenu.addAction('Обновить токен')

        self.addPostAct = orderMenu.addAction('Пост')
        self.imitatingConversation = orderMenu.addAction('Имитация диалогов')
        self.addGroupAct = orderMenu.addAction('Выйти из группы')
        self.editPhotoAct = orderMenu.addAction('Сменить фото')
        self.changeReadinessAct = orderMenu.addAction('Изменить % заполненности')
        self.changeNicknameAct = orderMenu.addAction('Изменить ник')
        self.addVideoAct = orderMenu.addAction('Добавить видео')
        self.editInfoAct = orderMenu.addAction('Изменить информацию')
        self.cleaningGroupAct = orderMenu.addAction('Почитсить группы')
        self.checkAllAct = orderMenu.addAction('Просмотр всех аватаров')
        self.checkWithAvatar = orderMenu.addAction('Выбрать всех с аватаром')
        self.cleaningPhotoAct = orderMenu.addAction('Все фото')
        self.allPostAct = orderMenu.addAction('Все записи')
        self.settingsPrivacyAct = orderMenu.addAction('Настройки приватности')
        self.changePassAct = orderMenu.addAction('Сменить пароль')

        self.repostsAct = otherMenu.addAction('Репосты')
        self.chekAccAct = otherMenu.addAction('Чекнуть акки')
        self.refreshAct = otherMenu.addAction('Обновить')
        self.friendsAct = otherMenu.addAction('Друзья')
        self.likeMachineAct = otherMenu.addAction('Like machine')
        self.promotionAct = otherMenu.addAction('Продвижение')

        # Filters raio button
        self.filterRadioButtonGroup = QButtonGroup()
        self.filterRadioButtonGroup.addButton(self.radioFilterNickname)
        self.filterRadioButtonGroup.addButton(self.radioFilterName)
        self.filterRadioButtonGroup.addButton(self.radioFilterReadiness)

        # Status bar
        self.statusBar = self.statusBar()

        # Visible
        self.widgetsConductor(self.textEdit, show=False)
        self.widgetsConductor(self.listDialog, show=False)
        self.filterReadinessWidget.setVisible(False)

    def loadAccaunts(self):
        self.masAccaunts = []
        self.listAccaunt.clear()
        self.itemList = []

        with self.con:
            cur = self.con.cursor()
            cur.execute('SELECT * FROM accaunt')
            rows = cur.fetchall()

            for row in rows:
                user_id, nickname, name, last_name, login, password, proxy, user_agent, token, frozen, readiness = row

                s = Session()
                s.proxies.update(http=proxy, https=proxy, all=proxy)
                s.headers.update(
                    {'User-Agent': user_agent, 'Accept': MyData.ACCEPT, 'Accept-Language': MyData.ACCEPT_LANGUAGE})

                accauntDict = {}
                accauntDict.update(user_id=user_id, nickname=nickname, name=name, last_name=last_name, login=login,
                                   password=password, proxy=proxy, user_agent=user_agent, token=token,
                                   frozen=frozen, readiness=readiness, session=s)

                myItem = ItemAcc(self, accauntDict)
                self.itemList.append(myItem)
                self.masAccaunts.append(accauntDict)

        # sort
        self.itemList.sort(key=lambda i: i.nickname)

        print('-----------------')
        # filling itemList
        for myItem in self.itemList:
            item = QListWidgetItem()
            item.setSizeHint(QtCore.QSize(100, 35))
            self.listAccaunt.addItem(item)
            self.listAccaunt.setItemWidget(item, myItem)

        # set fixet size
        masWidth = [item.width() for item in self.itemList]

        for w in range(len(masWidth)):
            try:
                if masWidth[w] > masWidth[w + 1]:
                    masWidth[w + 1] = masWidth[w]
            except:
                pass

        self.listAccaunt.setFixedWidth(masWidth[len(masWidth) - 1])
        self.filterLine.setFixedWidth(masWidth[len(masWidth) - 1])

    def eventFilter(self, QObject, QEvent):

        # Filter line
        if QObject == self.filterLine:

            if QEvent.type() == QtCore.QEvent.KeyPress:

                if self.radioFilterName.isChecked() == True:
                    self.listAccaunt.clear()
                    self.itemList.clear()
                    charLine = re.findall('\w', self.filterLine.text())

                    for acc in self.masAccaunts:
                        name = str(acc['name']) + ' ' + str(acc['last_name'])
                        charLogin = re.findall('\w', name)

                        try:
                            i = 0
                            while i in range(len(charLine)):

                                if i == len(charLine) - 1 and charLine[len(charLine) - 1] == charLogin[
                                    len(charLine) - 1]:
                                    item = QListWidgetItem()
                                    item.setSizeHint(QtCore.QSize(100, 40))
                                    myItem = ItemAcc(self, acc)
                                    self.itemList.append(myItem)
                                    self.listAccaunt.addItem(item)
                                    self.listAccaunt.setItemWidget(item, myItem)
                                    break
                                elif charLine[i] == charLogin[i]:
                                    i += 1
                                    continue
                                else:
                                    break
                        except:
                            pass

                elif self.radioFilterReadiness.isChecked() == True:
                    try:
                        readinessLine = int(self.filterLine.text())
                    except:
                        self.filterLine.setText('')
                        readinessLine = 1000
                    self.listAccaunt.clear()
                    self.itemList.clear()

                    for acc in self.masAccaunts:
                        name = str(acc['name']) + ' ' + str(acc['last_name'])

                        if self.radioProcLess.isChecked() == True:

                            if acc['readiness'] < readinessLine:
                                item = QListWidgetItem()
                                item.setSizeHint(QtCore.QSize(100, 40))
                                myItem = ItemAcc(self, acc)
                                self.itemList.append(myItem)
                                self.listAccaunt.addItem(item)
                                self.listAccaunt.setItemWidget(item, myItem)

                        elif self.radioProcMore.isChecked() == True:

                            if acc['readiness'] > readinessLine:
                                item = QListWidgetItem()
                                item.setSizeHint(QtCore.QSize(100, 40))
                                myItem = ItemAcc(self, acc)
                                self.itemList.append(myItem)
                                self.listAccaunt.addItem(item)
                                self.listAccaunt.setItemWidget(item, myItem)

                elif self.radioFilterNickname.isChecked() == True:
                    self.listAccaunt.clear()
                    self.itemList.clear()
                    charLine = re.findall('\w', self.filterLine.text())

                    for acc in self.masAccaunts:
                        nickname = str(acc['nickname'])
                        charLogin = re.findall('\w', nickname)

                        try:
                            i = 0
                            while i in range(len(charLine)):

                                if i == len(charLine) - 1 and charLine[len(charLine) - 1] == charLogin[
                                    len(charLine) - 1]:
                                    item = QListWidgetItem()
                                    item.setSizeHint(QtCore.QSize(100, 40))
                                    myItem = ItemAcc(self, acc)
                                    self.itemList.append(myItem)
                                    self.listAccaunt.addItem(item)
                                    self.listAccaunt.setItemWidget(item, myItem)
                                    break
                                elif charLine[i] == charLogin[i]:
                                    i += 1
                                    continue
                                else:
                                    break
                        except:
                            pass

                if self.filterLine.text() == '':

                    for acc in self.masAccaunts:
                        item = QListWidgetItem()
                        item.setSizeHint(QtCore.QSize(100, 40))
                        myItem = ItemAcc(self, acc)
                        self.itemList.append(myItem)
                        self.listAccaunt.addItem(item)
                        self.listAccaunt.setItemWidget(item, myItem)

        return False

    def promotion(self):
        Promotion(self)

    def getDialogs(self):
        self.widgetsConductor(self.listDialog, show=True)
        self.listDialog.clear()

        session = self.listAccaunt.itemWidget(self.listAccaunt.currentItem()).session
        token = self.listAccaunt.itemWidget(self.listAccaunt.currentItem()).token

        print(session.proxies)
        print(token)
        getUrl = UrlAPI(token)

        urlExecute = getUrl.execute()
        response = session.post(urlExecute, data={'code': MyData.CODE_DIALOGS}, proxies=session.proxies)

        try:
            dataResponse = json.loads(response.text)
            dialogs = dataResponse['response']['dialogs']
            users = dataResponse['response']['users']
        except Exception as e:
            print(e)
            return print(response.text)

        # Count unread dialogs
        if 'unread_dialogs' in dialogs:
            listItem = QListWidgetItem()
            listItem.setIcon(QtGui.QIcon('src/envelope.png'))
            listItem.setText('Непрочитанных: ' + str(dialogs['unread_dialogs']))
            self.listDialog.addItem(listItem)

        # Filling dialogs and mark photos
        for item in dialogs['items']:

            if 'chat_id' in item['message']:
                listItem = QListWidgetItem()
                listItem.setSizeHint(QtCore.QSize(200, 80))
                myListItem = ItemDialog()
                myListItem.setReadState(item['message']['read_state'])
                myListItem.setMessage(item['message']['body'])
                myListItem.setName(item['message']['title'], item['message']['user_id'])

                self.listDialog.addItem(listItem)
                self.listDialog.setItemWidget(listItem, myListItem)

            else:
                if item['message']['user_id'] == 100:
                    listItem = QListWidgetItem()
                    listItem.setSizeHint(QtCore.QSize(200, 80))
                    myListItem = ItemDialog()

                    if 'unread' in item:
                        myListItem.setUnread(1)
                    else:
                        myListItem.setReadState(item['message']['read_state'])

                    myListItem.setMessage(item['message']['body'])
                    myListItem.setName('VK', item['message']['user_id'])

                    self.listDialog.addItem(listItem)
                    self.listDialog.setItemWidget(listItem, myListItem)

                elif item['message']['user_id'] < 0:
                    listItem = QListWidgetItem()
                    listItem.setSizeHint(QtCore.QSize(200, 80))
                    myListItem = ItemDialog()
                    myListItem.setName('Сообщество', item['message']['user_id'])
                    myListItem.setMessage(item['message']['body'])
                    myListItem.setReadState(item['message']['read_state'])

                    self.listDialog.addItem(listItem)
                    self.listDialog.setItemWidget(listItem, myListItem)

                else:
                    listItem = QListWidgetItem()
                    listItem.setSizeHint(QtCore.QSize(200, 80))
                    myListItem = ItemDialog()

                    if 'unread' in item:
                        myListItem.setUnread(1)
                    else:
                        myListItem.setReadState(item['message']['read_state'])

                    myListItem.setMessage(item['message']['body'])
                    [myListItem.setName(user['first_name'] + ' ' + user['last_name'], item['message']['user_id']) for
                     user in users if
                     user['id'] == item['message']['user_id']]

                    self.listDialog.addItem(listItem)
                    self.listDialog.setItemWidget(listItem, myListItem)

    def dialogHistory(self):
        self.widgetsConductor(self.textEdit, show=True)
        self.textEdit.clear()

        session = self.listAccaunt.itemWidget(self.listAccaunt.currentItem()).session
        token = self.listAccaunt.itemWidget(self.listAccaunt.currentItem()).token
        methodHandler = MethodHandler(session, token)

        user_id = self.listDialog.itemWidget(self.listDialog.currentItem()).user_id
        name = self.listDialog.itemWidget(self.listDialog.currentItem()).name.text()
        messages = methodHandler.dialogHistory(user_id)
        messages['response']['items'].reverse()

        for message in messages['response']['items']:
            if message['from_id'] == message['user_id']:
                if message['read_state'] == 0:
                    self.textEdit.append(
                        "<div><font color=\"#bbd0ed\">" + name + ': ' + message['body'] + "</font></div>")
                else:
                    self.textEdit.append(name + ': ' + message['body'])
            else:
                if message['read_state'] == 0:
                    self.textEdit.append("<div><font color=\"#bbd0ed\">" + 'Я: ' + message['body'] + "</font></div>")
                else:
                    self.textEdit.append('Я: ' + message['body'])

    def getToken(self):
        chil = [item for item in self.itemList if item.b.checkState() == 2 and item.frozen == 0]

        for acc in chil:
            token_and_user_id = MethodHandler.getAccessToken(acc.session, acc.login, acc.password)
            token = token_and_user_id[0]
            user_id = token_and_user_id[1]

            with self.con:
                cur = self.con.cursor()
                cur.execute("UPDATE accaunt SET token=? WHERE user_id=?", (token, user_id))
                self.con.commit()

                row = cur.fetchone()
                print("Number of rows updated: %d" % cur.rowcount)

        self.loadAccaunts()

    def refreshName(self):
        errorListAcc = []
        requester = HRequester()
        chil = [(item.session, item.token, item.user_id) for item in self.itemList if
                item.b.checkState() == 2 and item.frozen == 0]
        error = 0

        for acc in chil:
            session = acc[0]
            token = acc[1]
            user_id = acc[2]
            getUrl = UrlAPI(token)

            requester(getUrl.account.getProfileInfo(), session, user_id)

        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT name, last_name, user_id FROM accaunt")
            rows = cur.fetchall()

        requests = requester.request()
        for r in requests:
            user_id1 = r[2][0]
            j = json.loads(r[0].text)

            if 'response' in j:
                name = j['response']['first_name']
                lastName = j['response']['last_name']

                nameG, lastNameG, user_idG = [m for m in rows if user_id1 == m[2]].pop()

                if name == nameG and lastName == lastNameG:
                    pass
                else:
                    with self.con:
                        cur = self.con.cursor()
                        cur.execute("UPDATE accaunt SET name=?, last_name=? WHERE user_id=?",
                                    (name, lastName, user_id1))
                        self.con.commit()

            elif 'error' in j:
                error += 1
                acc.responseError = j
                errorListAcc.append(acc)

        if error == 0:
            self.statusBar.showMessage('Обновленно')
        else:
            self.statusBar.showMessage('Обновленно. Проблемных аккаунтов:' + str(error))
            self.widgetsConductor(SurveyForm(self, errorListAcc), show=True)

    def chekAcc(self):
        errorListAcc = []
        requester = HRequester()
        chil = [item for item in self.itemList if item.b.checkState() == 2 and item.frozen == 0]

        for acc in chil:
            getUrl = UrlAPI(acc.token)

            requester(getUrl.account.setOnline(), acc.session, acc)

        requests = requester.request()
        for r in requests:
            acc = r[2][0]
            j = json.loads(r[0].text)

            if 'response' in j:

                if j['response'] == 1:
                    pass
                else:
                    print(j)
                    return

            elif 'error' in j:
                acc.responseError = j
                errorListAcc.append(acc)

        if len(errorListAcc) == 0:
            self.statusBar.showMessage('Обновленно')
        else:
            self.widgetsConductor(SurveyForm(self, errorListAcc), show=True)

    def hPost(self):
        chil = [(item.session, item.token, item.user_id) for item in self.itemList if
                item.b.checkState() == 2 and item.frozen == 0]
        HAddPost(self)

    def editInfo(self):
        chil = [item for item in self.itemList if
                item.b.checkState() == 2 and item.frozen == 0]
        self.widgetsConductor(EditInfoWidget(self, chil), show=True)

    def changePhoto(self):
        requester = HRequester()
        postRequester = HPostRequester()
        chil = [(item.session, item.token) for item in self.itemList if item.b.checkState() == 2 and item.frozen == 0]

        # choise photos
        path = QFileDialog.getOpenFileName()
        byteImg = open(path[0], 'rb').read()

        def editPhoto(image_data):
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            pix = image.load()
            factor = 2
            for i in range(width):
                for j in range(height):
                    rand = random.randint(-factor, factor)
                    a, b, c = pix[i, j]

                    if (a < 0):
                        a = 0
                    if (b < 0):
                        b = 0
                    if (c < 0):
                        c = 0
                    if (a > 255):
                        a = 255
                    if (b > 255):
                        b = 255
                    if (c > 255):
                        c = 255

                    pix[i, j] = a + rand, b + rand, c + rand

            imgByteArr = io.BytesIO()
            image.save(imgByteArr, format='jpeg')
            return imgByteArr.getvalue()

        for item in chil:
            session = item[0]
            getUrl = UrlAPI(item[1])
            session.headers.update(Accept='multipart/form-data')

            # get upload url for photos
            urlUpload = getUrl.photos.getOwnerPhotoUploadServer()
            requester(urlUpload, session)

        response = requester.request()
        for r in response:
            session = r[1]
            j = json.loads(r[0].text)
            urlUpload = j['response']['upload_url']
            postRequester(urlUpload, session, 'null', files={'photo': ('image.jpg', editPhoto(byteImg))})

        postResponse = postRequester.request()
        for pr in postResponse:
            session = pr[1]
            dataPost = json.loads(pr[0].text)
            server = dataPost['server']
            photo = dataPost['photo']
            hash = dataPost['hash']

            for item in chil:
                if item[0] == session:
                    getUrl = UrlAPI(item[1])
                    saveUrl = getUrl.photos.saveOwnerPhoto(server=server, photo=photo, hash=hash)
                    requester(saveUrl, session)

        saveResponse = requester.request()
        for r in saveResponse:
            try:
                j = json.loads(r[0].text)
                if 'saved' in j['response']:
                    print('Upload avatar completed')
                else:
                    print('Error', r[0].text)
            except:
                print('Error', r[0].text)

    def addGroup(self):
        chil = [(item.session, item.token) for item in self.itemList if item.b.checkState() == 2 and item.frozen == 0]
        HAddGroup(self, chil)

    def widgetsConductor(self, widget, show=None, delete=None):

        if show == False:
            self.widgetMas.append(widget)

        elif show == True:

            if widget in self.widgetMas:

                for w in self.widgetMas:
                    w.setVisible(False)

                widget.setVisible(True)

            else:

                for w in self.widgetMas:
                    w.setVisible(False)

                self.widgetMas.append(widget)
                self.mainHLayout.addWidget(widget)

        if delete == True:

            for i in range(len(self.widgetMas)):

                if widget == self.widgetMas[i]:
                    w = self.widgetMas.pop(i)
                    w.deleteLater()
                    break

    def cleaningGroup(self):
        chil = [item for item in self.itemList if item.b.checkState() == 2 and item.frozen == 0]
        requester = HRequester()

        for acc in chil:
            getUrl = UrlAPI(acc.token)
            requester(getUrl.groups.get(extended=1, count=999), acc.session, getUrl)

        responseGroups = requester.request()
        countGroups = [len(json.loads(r[0].text)['response']['items']) for r in responseGroups]
        curProc = 0

        for c in range(len(countGroups)):
            try:
                countGroups[c] = countGroups[c] + countGroups[c - 1]
            except:
                continue

        countOperationLeft = countGroups[len(countGroups) - 1] * 2012
        countOperationProc = 100 / countOperationLeft
        print('Кол-во операций:', countOperationLeft)

        for r in responseGroups:
            getter = r[2][0]
            session = r[1]
            items = json.loads(r[0].text)['response']['items']

            with open('files/cities', 'r') as f:
                lines = f.readlines()

            for item in items:
                for line in lines:
                    result = re.search(line.lower().strip('\n'), item['name'].lower())

                    if result:

                        def delete():
                            try:
                                leave = session.get(getter.groups.leave(group_id=item['id']), proxies=session.proxies,
                                                    timeout=5)
                                j = json.loads(leave.text)
                            except:
                                return

                            if 'response' in j:
                                if j['response'] == 1:
                                    print('Удалено', item['name'])
                                    return
                            elif 'error' in j:
                                if 'error_code' in j['error']:
                                    if j['error']['error_code'] == 6:
                                        print('Повтор удаления')
                                        time.sleep(5)
                                        delete()
                                        return
                                else:
                                    print('Неизвестный error', leave.text)
                            else:
                                print(leave.text)

                        delete()

                    countOperationLeft -= 1
                    curP = round(countOperationProc * countOperationLeft)

                    if curP == curProc:
                        pass
                    else:
                        curProc = curP
                        print('Осталось:', str(curProc) + '%')

    def addVideo(self):
        requester = HRequester()
        chil = [item for item in self.itemList if item.b.checkState() == 2 and item.frozen == 0]
        randomAcc = random.choice(chil)
        getMainUrl = UrlAPI(randomAcc.token)

        responseMain = requests.get(getMainUrl.video.get(owner_id='-29573241', count=5),
                                    proxies=randomAcc.session.proxies)
        responseJson = json.loads(responseMain.text)['response']['items']

        for video in responseJson:
            owner_id = video['owner_id']
            video_id = video['id']

            for acc in chil:
                getUrl = UrlAPI(acc.token)
                requester(getUrl.video.add(video_id=video_id, owner_id=owner_id), acc.session, acc.user_id)

            responseAdd = requester.request()

            for r in responseAdd:
                j = json.loads(r[0].text)
                user_id = r[2][0]

                if 'response' in j:
                    if j['response'] == 1:
                        pass
                    else:
                        print('Не добавленно', user_id, r[0].text)

                else:
                    print('Ошибка', user_id, r[0].text)

        print('----------')

    def clickedFilterButton(self):

        if self.filterRadioButtonGroup.checkedButton() == self.radioFilterReadiness:
            self.filterReadinessWidget.setVisible(True)
        else:
            self.filterReadinessWidget.setVisible(False)

    def OutputCountOfNames(self):
        mas = [['test', 0]]
        for acc in self.masAccaunts:

            chek = False

            for i in range(len(mas)):

                if acc['nickname'] == mas[i][0]:
                    mas[i][1] += 1
                    chek = True
                    break

            if chek == False:
                mas.append([acc['nickname'], 1])

        mas.sort(key=lambda i: i[1])

        [print(m) for m in mas]


App = QApplication(sys.argv)
Prim = Main()
Prim.showMaximized()
sys.exit(App.exec_())
