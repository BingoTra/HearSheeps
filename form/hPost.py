import io
import json
import random
import sqlite3 as sql
import time

import copy
from PIL import Image
from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout, QFrame, QTabWidget, QApplication, \
    QFileDialog, QLabel, QLCDNumber

from threading import Thread
from api import UrlAPI
from hRequester import HRequester, HPostRequester


class HAddPost(QObject):
    signal = pyqtSignal()

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.post_time = 0
        self.parent = parent
        self.byteImgMas = []
        self.pixmap = QPixmap()
        self.group_list_repost = []
        self.chil = [item for item in self.parent.itemList if item.b.checkState() == 2 and item.frozen == 0]

        # Create a gui object.
        self.gui = Gui()

        # Make any cross object connections.
        self._connectSignals()

        self.gui.show()
        self.clockThread()

    def _connectSignals(self):
        self.signal.connect(self.fillingLineGroup)
        self.gui.btn_browse.clicked.connect(self.browse)
        self.gui.btn_pinPost.clicked.connect(self.pinPost)
        self.gui.btn_addRepost.clicked.connect(self.repost)
        self.gui.btn_sendPost.clicked.connect(self.sendPost)
        self.gui.btn_addComment.clicked.connect(self.sendCommnet)
        self.gui.lineRepost.editingFinished.connect(self.lineRepostDownloadThread)

    def repost(self):
        groupList = []

        post_str = self.gui.lineRepost.text().strip('https://vk.com/')

        self.post_time += int(self.gui.line_sleep_time.text()) * 60

        if self.gui.lineGroup1.text() != '':
            groupList.append(self.gui.lineGroup1.text())

        if self.gui.lineGroup2.text() != '':
            groupList.append(self.gui.lineGroup2.text())

        if self.gui.lineGroup3.text() != '':
            groupList.append(self.gui.lineGroup3.text())

        wo = WorkerObject(None, self.chil)
        th = Thread(target=wo.repost, args=(post_str, groupList, self.post_time, self.gui.likeCheckBox.checkState()))
        th.setDaemon(True)
        th.start()

    def pinPost(self):
        number_post = self.gui.pinLine.text()

        wo = WorkerObject(None, self.chil)
        th = Thread(target=wo.pinPost, args=(number_post, ))
        th.setDaemon(True)
        th.start()

    def browse(self):
        # choise photos
        path = QFileDialog.getOpenFileName()

        imq = QLabel()
        self.browseLayout.addWidget(imq)
        self.pixmap.load(path[0])
        myPixmap = self.pixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        imq.setPixmap(myPixmap)

        self.byteImgMas.append(open(path[0], 'rb').read())

    def sendPost(self):

        photosList = self.getPhotos()

        for item in self.masSessions:
            session, token, user_id = item
            photos = ','
            masP = []

            for photo in photosList:

                if session == photo[0]:
                    masP.append(photo[1])

            getUrl = UrlAPI(token)

            if self.linePost.text() == '':
                url = getUrl.wall.post(attachments=photos.join(masP))
                self.requester(url, session)
            else:
                url = getUrl.wall.post(message=self.linePost.text(), attachments=photos.join(masP))
                self.requester(url, session)

        response = self.requester.request()
        for r in response:
            print(r[0].text)

        print('Кол-во акков', len(self.masSessions), 'Ответов сервера:', len(response))

    def sendCommnet(self):
        text = self.gui.commentLineText.text()
        group = self.gui.commentLineGroup.text()
        post_id = self.gui.commentLineItemId.text()

        wo = WorkerObject(None, self.chil)
        th = Thread(target=wo.sendComment, args=(group, post_id, text))
        th.setDaemon(True)
        th.start()

    def getPhotos(self):
        photosList = []

        for mas in self.masSessions:
            session, token, user_id = mas
            getUrl = UrlAPI(token)

            # get upload url for photos
            for imgByte in self.byteImgMas:
                editImg = self.editPhoto(imgByte)
                urlUpload = getUrl.photos.getWallUploadServer()
                self.requester(urlUpload, session, editImg)

        urlResponse = self.requester.request()

        for ur in urlResponse:
            print(ur[0].text)
            img = ur[2][0]
            session = ur[1]
            session.headers.update(Accept='multipart/form-data')
            data = json.loads(ur[0].text)
            url = data['response']['upload_url']
            user_id = data['response']['user_id']
            self.postRequester(url, session, user_id, files={'photo': ('image.jpg', img)})

        postResponse = self.postRequester.request()

        for pr in postResponse:
            print(pr[0].text, pr[2][0])
            dataPost = json.loads(pr[0].text)
            session = pr[1]
            user_id = pr[2][0]
            server = dataPost['server']
            photo = dataPost['photo']
            hash = dataPost['hash']

            for item in self.masSessions:
                if item[0] == session:
                    getUrl = UrlAPI(item[1])
                    saveUrl = getUrl.photos.saveWallPhoto(server=server, photo=photo, hash=hash)
                    self.requester(saveUrl, session, user_id)

        saveResponse = self.requester.request()
        for r in saveResponse:
            print(r[0].text, 'save')
            user_id = r[2][0]
            session = r[1]
            data = json.loads(r[0].text)
            photo_id = data['response'][0]['id']
            photo = 'photo' + str(user_id) + '_' + str(photo_id)

            photosList.append([session, photo])

        return photosList

    def editPhoto(self, image_data):
        image = Image.open(io.BytesIO(image_data))
        width, height = image.size
        pix = image.load()
        step = 1 * width / 100
        factor = 5

        i = 0
        while i < width:

            j = 0
            while j < height:
                rand = random.randint(-factor, factor)
                a, b, c = pix[i, j]
                pix[i, j] = a + rand, b + rand, c + rand

                j = j + step

            i = i + step

        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format='jpeg')
        return imgByteArr.getvalue()

    def countClock(self):

        while True:

            if self.post_time <= 0:
                pass
            else:

                hour, remnant = divmod(self.post_time, 3600)
                minute, second = divmod(remnant, 60)

                self.gui.lcd.display(str(hour) + ':' + str(minute))

                self.post_time -= 1
                time.sleep(1)

    def clockThread(self):
        th = Thread(target=self.countClock)
        th.setDaemon(True)
        th.start()

    def lineRepostDownloadThread(self):
        th = Thread(target=self.lineRepostDownload)
        th.setDaemon(True)
        th.start()

    def lineRepostDownload(self):
        self.group_list_repost = []

        post_str = self.gui.lineRepost.text().strip('https://vk.com/wall')

        requester = HRequester()
        acc = random.choice(self.chil)
        getUrl = UrlAPI(acc.token)
        url = getUrl.wall.getById(posts=post_str, extended=1)
        requester(url, acc.session)

        response = requester.request()

        for r in response:

            try:
                j = json.loads(r[0].text)
            except:
                continue

            if 'response' in j:

                for group in j['response']['groups']:
                    self.group_list_repost.append(group['id'])

                self.signal.emit()
            else:
                print(j)

    def fillingLineGroup(self):

        for i in range(len(self.group_list_repost)):

            if i == 0:
                self.gui.lineGroup1.setText(str(self.group_list_repost[i]))
            if i == 1:
                self.gui.lineGroup2.setText(str(self.group_list_repost[i]))
            if i == 2:
                self.gui.lineGroup3.setText(str(self.group_list_repost[i]))


class Gui(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        uic.loadUi("uiForm/post.ui", self)
        a = QApplication.desktop().availableGeometry()
        self.setGeometry(a.width() / 6, a.height() / 6, (2 * a.width()) / 3, a.height() / 2)

        self.byteImgMas = []
        self.pixmap = QPixmap()

        # Repost tab
        repostLayout = QVBoxLayout()
        repostLayout.addWidget(self.repostWidget)
        frame = QFrame()
        frame.setLayout(repostLayout)

        # Record tab
        recordLayout = QVBoxLayout()
        recordLayout.addWidget(self.postWidget)
        frame1 = QFrame()
        frame1.setLayout(recordLayout)

        # Comemnt tab
        commentLayout = QVBoxLayout()
        self.commentLineText = QLineEdit()
        self.commentLineGroup = QLineEdit()
        self.commentLineItemId = QLineEdit()
        self.btn_addComment = QPushButton('Добавить')
        commentLayout.addWidget(QLabel('Id группы'))
        commentLayout.addWidget(self.commentLineGroup)
        commentLayout.addWidget(QLabel('Id поста'))
        commentLayout.addWidget(self.commentLineItemId)
        commentLayout.addWidget(QLabel('Текст'))
        commentLayout.addWidget(self.commentLineText)
        commentLayout.addWidget(self.btn_addComment)
        frame2 = QFrame()
        frame2.setLayout(commentLayout)

        # Pin Posttab
        pinLayout = QVBoxLayout()
        self.pinLine = QLineEdit()
        self.btn_pinPost = QPushButton('Закрепить')
        pinLayout.addWidget(QLabel('Запись по счету'))
        pinLayout.addWidget(self.pinLine)
        pinLayout.addWidget(self.btn_pinPost)
        frame3 = QFrame()
        frame3.setLayout(pinLayout)

        # Test Posttab
        testLayout = QVBoxLayout()
        self.btn_test = QPushButton('Test')
        testLayout.addWidget(self.btn_test)
        frame_test = QFrame()
        frame_test.setLayout(testLayout)

        # Tabs
        tab = QTabWidget()
        tab.addTab(frame, "Репост")  # вкладки
        tab.addTab(frame1, "Запись")
        tab.addTab(frame2, "Комментарий")
        tab.addTab(frame3, "Закрепить")
        tab.addTab(frame_test, "Test")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(tab)

        self.setLayout(mainLayout)

        self.lineRepost.setFocus()

    @pyqtSlot(str)
    def completeComment(self, message):
        if message == 'comment':
            print('Comments sends')


class WorkerObject(QObject):
    signalComplete = pyqtSignal(str)

    def __init__(self, parent=None, chil=None):
        super(self.__class__, self).__init__(parent)

        self.chil = chil
        self.requester = HRequester()
        self.postRequester = HPostRequester()

    @pyqtSlot()
    def startWork(self):
        self.signalComplete.emit()

    def sendComment(self, group_id, post_id, comment_text):
        error = []

        for acc in self.chil:
            getUrl = UrlAPI(acc.token)
            url = getUrl.wall.createComment(owner_id=group_id, post_id=post_id, message=comment_text)
            self.requester(url, acc.session, acc)

        response = self.requester.request()
        for item in response:
            acc = item[2][0]

            try:
                res = json.loads(item[0].text)
                if 'comment_id' in res['response']:
                    pass

                else:
                    error.append([res, acc.user_id])

            except:
                error.append([item[0].text, acc.user_id])

        if len(error) == 0:
            print('All comments send')
        else:
            [print(i) for i in error]

        self.signalComplete.emit('comment')

    def repost(self, post_str, group_list, sleep_time, likeCheckState):

        time.sleep(sleep_time)

        if post_str != '':
            con = sql.connect('db/db.sqlite3')
            cur = con.cursor()

            with con:
                cur.execute('SELECT group_post_id FROM repost WHERE group_post_id=?',(post_str.strip('wall'),))
                row = cur.fetchone()

                if row:
                    print('Такой репост уже есть')
                    self.signalComplete.emit('existing repost')
                    return

            if likeCheckState == 2:
                self.sendLike(post_str)
            else:
                self.sendRepost(post_str)

        if group_list:
            self.addGroup(group_list)

        self.signalComplete.emit('reposts made')

    def sendRepost(self, post_str):
        error = []
        atLeastOneRepost = False
        con = sql.connect('db/db.sqlite3')
        cur = con.cursor()
        group_post_id = post_str.strip('wall')

        for acc in self.chil:
            getUrl = UrlAPI(acc.token)
            url = getUrl.wall.repost(object=post_str)
            self.requester(url, acc.session, acc.user_id)

        response = self.requester.request()
        for item in response:
            user_id = item[2][0]
            res = json.loads(item[0].text)

            if 'response' in res and 'success' in res['response']:

                post_id = res['response']['post_id']

                if res['response']['success'] == 1:
                    with con:
                        cur.execute('INSERT INTO accaunt_repost (user_id, group_post_id, post_id) VALUES (?,?,?)',
                                    (user_id, group_post_id, post_id))
                        atLeastOneRepost = True
                else:
                    if 'error' in res:
                        error.append([res, user_id])
                    else:
                        error.append([res, user_id])

        if atLeastOneRepost == True:
            with con:
                cur.execute('INSERT INTO repost (group_post_id) VALUES (?)', (group_post_id,))
                print('Репосты сделаны')

        if len(error) == 0:
            print('Все репосты сделаны удачно')
        else:
            [print(i) for i in error]

        self.signalComplete.emit('reposts')

    def sendLike(self, post_str):
        error = []
        atLeastOneRepost = False

        for acc in self.chil:
            owner_id, item_id = post_str.strip('wall').split('_')
            getUrl = UrlAPI(acc.token)
            url = getUrl.likes.add(type='post', owner_id=owner_id, item_id=item_id)
            self.requester(url, acc.session, acc.user_id)

        response = self.requester.request()
        for item in response:
            user_id = item[2][0]
            res = json.loads(item[0].text)

            if 'response' in res and 'likes' in res['response']:
                atLeastOneRepost = True
            else:
                if 'error' in res:
                    error.append([res, user_id])
                else:
                    error.append([res, user_id])

        if atLeastOneRepost == True:
            print('Лайки поставлены')

        if len(error) == 0:
            print('Все лайки поставлены удачно')
        else:
            [print(i) for i in error]

        self.signalComplete.emit('reposts')

    def addGroup(self, group_list):
        error = []

        for group in group_list:

            for acc in self.chil:
                getUrl = UrlAPI(acc.token)
                url = getUrl.groups.join(group_id=group)
                self.requester(url, acc.session, acc)

        response = self.requester.request()
        for item in response:
            acc = item[2][0]

            try:
                res = json.loads(item[0].text)
                if res['response'] == 1:
                    pass

                else:
                    error.append([res, acc.user_id])

            except:
                error.append([item[0].text, acc.user_id])

        if len(error) == 0:
            print('Все группы добавленны удачно')
        else:
            [print(i) for i in error]

        self.signalComplete.emit('groups added')

    def pinPost(self, number_post):
        error = []

        for acc in self.chil:
            getUrl = UrlAPI(acc.token)
            url = getUrl.wall.get(extended=1, count=1, offset=number_post)
            self.requester(url, acc.session, acc, getUrl)

        response = self.requester.request()
        for r in response:
            acc = r[2][0]
            getUrl = r[2][1]

            try:
                res = json.loads(r[0].text)['response']['items'][0]
                post_id = res['id']
                self.requester(getUrl.wall.pin(post_id=post_id), acc.session, acc)

            except Exception as e:
                print(repr(e))
                error.append([r[0].text, acc.user_id])

        response = self.requester.request()
        for r in response:
            acc = r[2][0]

            try:
                res = json.loads(r[0].text)['response']

                if res != 1:
                    error.append([r[0].text, acc.user_id])

            except:
                error.append([r[0].text, acc.user_id])

        if len(error) == 0:
            print('All pined')
        else:
            [print(i) for i in error]