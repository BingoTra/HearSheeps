import json
from PyQt5 import QtGui

import requests
from threading import Thread

import time
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QShortcut, QFileDialog, QWidget, QPushButton, \
    QFormLayout, QHBoxLayout, QScrollArea, QVBoxLayout, QLabel, QFrame, QLineEdit

from api import UrlAPI
from customWidget.recordWall import RecordWall
from hRequester import HRequester


class RecordsForm(QWidget):
    signal = pyqtSignal(QObject, dict)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.gui = Gui(self)
        self.parent = parent
        self.chil = [item for item in self.parent.itemList if item.b.checkState() == 2 and item.frozen == 0]

        # Make any cross object connections.
        self._connectSignals()

        self.gui.show()

    def _connectSignals(self):
        self.gui.btn_start.clicked.connect(self.start)
        self.gui.signalCreatedRecords.connect(self.fillRecord)
        self.gui.btn_delete_all.clicked.connect(self.deleteAll)

    def start(self):
        count = self.gui.line_count.text()
        offset = self.gui.line_offset.text()

        for acc in self.chil:

            th = Thread(target=self.getDataWall, args=(acc, offset, count))
            th.setDaemon(True)
            th.start()


    def getDataWall(self, acc, offset, count):
        print('getData Wall')
        getUrl = UrlAPI(acc.token)
        url = getUrl.wall.get(extended=1, count=count, offset=offset)

        def dowload():
            print('dowmload')
            try:
                response = requests.get(url, proxies=acc.session.proxies)
                return response
            except requests.exceptions.ProxyError as e:
                print(repr(e))
                return dowload()
            except requests.exceptions.Timeout as e:
                print(repr(e))
                return dowload()
            except requests.exceptions.ConnectionError as e:
                print(e)
                return None

        response = dowload()

        if response:
            print('if response')
            dataWall = json.loads(response.text)

            if 'response' in dataWall:
                # self.gui.createRecords(acc, dataWall['response'])
                self.signal.emit(acc, dataWall['response'])
        else:
            print(response)

    def filingRecord(self, acc, records, dataWall):
        print('filling record')
        requester = HRequester()

        # mark reckords wall
        for i in range(len(dataWall['items'])):
            print(len(records))
            try:
                record = records[i][0]
            except IndexError:
                continue

            # Set post ID
            record.post_id = dataWall['items'][i]['id']

            # Set name
            if dataWall['items'][i]['from_id'] == dataWall['items'][i]['owner_id']:
                record.setNameLayout('Я', '.', 'src/icon.png')
            else:
                record.setNameLayout(str(dataWall['items'][i]['from_id']), '.', 'src/icon.png')

            # Post source
            if 'data' in dataWall['items'][i]['post_source']:
                record.setPostSource(dataWall['items'][i]['post_source']['data'])

            # Set data
            record.setDateLayout(dataWall['items'][i]['date'])

            # Set text
            record.setText(dataWall['items'][i]['text'])

            # Attechments
            if 'attachments' in dataWall['items'][i]:
                for item in dataWall['items'][i]['attachments']:
                    if item['type'] == 'photo':
                        requester(item['photo']['photo_130'], acc.session, record.setAttachments)

            # Information
            if 'views' in dataWall['items'][i]:
                record.setInfo(dataWall['items'][i]['likes']['count'],
                               dataWall['items'][i]['reposts']['count'],
                               dataWall['items'][i]['views']['count'])
            else:
                record.setInfo(dataWall['items'][i]['likes']['count'],
                               dataWall['items'][i]['reposts']['count'])

            # Repost
            if 'copy_history' in dataWall['items'][i]:
                repost = records[i][1]
                repost.deleteInformation()
                repost.delButton.deleteLater()
                repost.frame.setFrameShape(QFrame.StyledPanel)

                repost.setText(dataWall['items'][i]['copy_history'][0]['text'])
                repost.setDateLayout(dataWall['items'][i]['copy_history'][0]['date'])

                '''Set attachments'''
                if 'attachments' in dataWall['items'][i]['copy_history'][0]:
                    for item in dataWall['items'][i]['copy_history']:

                        try:
                            for ite in item['attachments']:
                                if ite['type'] == 'photo':
                                    requester(ite['photo']['photo_604'], acc.session, repost.setAttachments)
                        except KeyError:
                            continue

                '''Set profile info'''
                for item in dataWall['items'][i]['copy_history']:
                    owner_id = item['owner_id']
                    if owner_id < 0:
                        for group in dataWall['groups']:
                            if group['id'] == (owner_id * -1):
                                requester(group['photo_50'], acc.session, repost.setNameLayout, group['name'], '.')

                    elif owner_id > 0:
                        for profile in dataWall['profiles']:
                            if profile['id'] == (owner_id):
                                requester(profile['photo_50'], acc.session, repost.setNameLayout, profile['first_name'],
                                          profile['last_name'])

                record.repostLayout.addWidget(repost)

        response = requester.request()

        for r in response:

            if len(r[2]) == 1:
                seter = r[2][0]
                photo = r[0].content
                seter(photo)
            else:
                rList = list(r[2])
                seter = rList.pop(0)
                photo = r[0].content
                args = [i for i in rList]
                seter(*args, photo)

    def fillRecord(self, acc, records, dataWall):
        print('fill record')
        th = Thread(target=self.filingRecord, args=(acc, records, dataWall))
        th.setDaemon(True)
        th.start()

        th.join()

    def deleteAll(self):
        requester = HRequester()

        for post in self.gui.allPost:
            getUrl = UrlAPI(post.token)
            requester(getUrl.wall.delete(post_id=post.post_id), post.session, post)

        response = requester.request()
        for r in response:
            j = json.loads(r[0].text)
            post = r[2][0]

            if j['response'] == 1:
                post.deleteLater()
            else:
                print('Error Response by delete post', r[0].text)


class Gui(QWidget):
    signalCreatedRecords = pyqtSignal(QObject, list, dict)

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)

        parent.signal.connect(self.createRecords)

        self.sizeMonitor = QApplication.desktop().availableGeometry()
        self.setGeometry(0, 0, self.sizeMonitor.width(), self.sizeMonitor.height())

        self.myForm = QFormLayout()
        self.allPost = []

        # Create scroll and put in general layout
        scrollWidget = QWidget()
        scrollWidget.setLayout(self.myForm)
        scroll = QScrollArea()
        scroll.setWidget(scrollWidget)
        scroll.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

        self.line_count = QLineEdit()
        self.line_count.setText('count')
        self.line_offset = QLineEdit()
        self.line_offset.setText('offset')
        self.btn_start = QPushButton('Click')
        self.btn_delete_all = QPushButton('Удалить все')

        self.myForm.addWidget(self.line_count)
        self.myForm.addWidget(self.line_offset)
        self.myForm.addWidget(self.btn_start)
        self.myForm.addWidget(self.btn_delete_all)

    def createRecords(self, acc, dataWall):
        print('create record')
        recordList = []

        layName = QHBoxLayout()
        layName.addWidget(QLabel(acc.name))
        layName.addWidget(QLabel(acc.last_name))
        wLayName = QWidget()
        wLayName.setLayout(layName)
        self.myForm.addWidget(wLayName)

        for i in range(len(dataWall['items'])):
            record = RecordWall(self, acc.session, acc.token)
            repost = RecordWall(self)
            recordList.append([record,repost])
            self.allPost.append(record)
            self.myForm.addWidget(record)

        self.signalCreatedRecords.emit(acc, recordList, dataWall)




