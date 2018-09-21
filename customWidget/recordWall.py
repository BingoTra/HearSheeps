import re

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
import datetime

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QFrame, QApplication

import MyData
from api import API


class RecordWall (QWidget):
    def __init__(self, parent = None, session=None, token=None):
        QWidget.__init__(self, parent)
        self.pixmap        = QtGui.QPixmap()
        self.sizeMonitor = QApplication.desktop().availableGeometry()
        self.setGeometry(0, 0, (2 * self.sizeMonitor.width()) / 3, self.sizeMonitor.height())
        self.session = session
        self.token = token
        self.post_id = 0

        self.ui()

        self.delButton.clicked.connect(self.deletePost)

    def ui(self):
        self.nameLayout    = QHBoxLayout()
        self.icon          = QLabel()
        self.textName      = QLabel()
        self.postSource    = QLabel()
        self.delButton     = QPushButton('Del')
        self.nameLayout.addWidget(self.icon, 0, Qt.AlignLeft)
        self.nameLayout.addWidget(self.textName, 1, Qt.AlignLeft)
        self.nameLayout.addWidget(self.postSource, 2, Qt.AlignLeft)
        self.nameLayout.addWidget(self.delButton, 3, Qt.AlignRight)

        self.dateLayout    = QHBoxLayout()
        self.date          = QLabel()
        self.dateLayout.addWidget(self.date)

        self.textLayout    = QHBoxLayout()
        self.text          = QLabel()
        self.textLayout.addWidget(self.text)

        self.attachmentsLayout = QHBoxLayout()

        self.repostLayout = QVBoxLayout()

        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.infoWidget = QWidget()
        self.infoLayout = QHBoxLayout()
        self.like = QLabel()
        self.pixmap.load(MyData.CWD+'/src/like.png')
        myPixmap = self.pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.like.setPixmap(myPixmap)
        self.countLike = QLabel()
        self.repost = QLabel()
        self.pixmap.load(MyData.CWD+'/src/repost.png')
        myPixmap = self.pixmap.scaled(16, 16, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.repost.setPixmap(myPixmap)
        self.countRepost = QLabel()
        self.views = QLabel()
        self.pixmap.load(MyData.CWD+'/src/eye.png')
        myPixmap = self.pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.views.setPixmap(myPixmap)
        self.countViews = QLabel()
        self.infoLayout.addWidget(self.like, alignment=Qt.AlignLeft)
        self.infoLayout.addWidget(self.countLike, alignment=Qt.AlignRight)
        self.infoLayout.addWidget(self.repost, alignment=Qt.AlignLeft)
        self.infoLayout.addWidget(self.countRepost, alignment=Qt.AlignLeft)
        self.infoLayout.addWidget(self.views, alignment=Qt.AlignRight)
        self.infoLayout.addWidget(self.countViews, alignment=Qt.AlignRight)
        self.infoWidget.setLayout(self.infoLayout)
        self.infoWidget.setMaximumWidth(self.infoLayout.totalSizeHint().width() + 50)

        self.allQVBoxLayout = QVBoxLayout()
        self.allQVBoxLayout.addLayout(self.nameLayout)
        self.allQVBoxLayout.addLayout(self.dateLayout)
        self.allQVBoxLayout.addLayout(self.textLayout)
        self.allQVBoxLayout.addLayout(self.attachmentsLayout)
        self.allQVBoxLayout.addLayout(self.repostLayout)
        self.allQVBoxLayout.addWidget(self.line)
        self.allQVBoxLayout.addWidget(self.infoWidget)


        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Panel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setLayout(self.allQVBoxLayout)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.frame)

        self.setLayout(self.mainLayout)

        self.textName.setStyleSheet(  '''color: rgb(60,  50,  130);''')
        self.postSource.setStyleSheet('''color: rgb(170, 170, 170);''')
        self.date.setStyleSheet(      '''color: rgb(130, 130, 130);''')
        self.frame.setStyleSheet(     '''background-color:rgb(255, 255, 255);''')


    def setNameLayout(self, name, lastName, image):
        self.textName.setText(name + ' ' + lastName)

        if type(image) == str:
            self.pixmap.load(image)
            myPixmap = self.pixmap.scaled(32,32, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.icon.setPixmap(myPixmap)
        elif type(image) == bytes:
            self.pixmap.loadFromData(image)
            myPixmap = self.pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.icon.setPixmap(myPixmap)

    def setPostSource(self, postSource):
        if postSource == 'profile_photo':
            self.postSource.setText('Обновил фотографию на странице')
        elif postSource == 'profile_activity':
            self.postSource.setText('Изменен статус')
        elif postSource == 'pinned':
            self.postSource.setText('Запись закреплена')

    def setDateLayout(self, date):
        value = datetime.datetime.fromtimestamp(date)
        if value.month == 1:
            self.date.setText(value.strftime('%d янв %Y'))
        if value.month == 2:
            self.date.setText(value.strftime('%d фев %Y'))
        if value.month == 3:
            self.date.setText(value.strftime('%d март %Y'))
        if value.month == 4:
            self.date.setText(value.strftime('%d апр %Y'))
        if value.month == 5:
            self.date.setText(value.strftime('%d май %Y'))
        if value.month == 6:
            self.date.setText(value.strftime('%d июнь %Y'))
        if value.month == 7:
            self.date.setText(value.strftime('%d июль %Y'))
        if value.month == 8:
            self.date.setText(value.strftime('%d авг %Y'))
        if value.month == 9:
            self.date.setText(value.strftime('%d сен %Y'))
        if value.month == 10:
            self.date.setText(value.strftime('%d окт %Y'))
        if value.month == 11:
            self.date.setText(value.strftime('%d ноя %Y'))
        if value.month == 12:
            self.date.setText(value.strftime('%d дек %Y'))

    def setText(self, text):
        split = re.split('\n', text)
        retext =''

        for mas in split:
            sp = re.findall('.', mas)

            if len(sp) > 30:
                retext += ''.join(sp[0:len(sp) // 2])
                retext += '\n'
                retext += ''.join(sp[len(sp) // 2:len(sp)])
                retext += ('\n')
            else:
                retext += mas + '\n'

        self.text.setText(retext)

    def setAttachments(self, imgata):
        attachment = QLabel()
        self.attachmentsLayout.addWidget(attachment, Qt.AlignLeft)
        self.pixmap.loadFromData(imgata)
        myPixmap = self.pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.FastTransformation)
        attachment.setPixmap(myPixmap)

    def setInfo(self, likes, reposts, views=None):
        self.countLike.setText(str(likes))
        self.countRepost.setText(str(reposts))

        if views != None:
            self.countViews.setText(str(views))

    def deleteInformation(self):
        self.line.deleteLater()
        self.infoLayout.deleteLater()
        self.like.deleteLater()
        self.countLike.deleteLater()
        self.repost.deleteLater()
        self.countRepost.deleteLater()
        self.views.deleteLater()
        self.countViews.deleteLater()

    def deletePost(self):
        api = API(self.session, self.token)
        response = api.wall.delete(post_id=self.post_id)
        if response['response'] ==1:
            self.deleteLater()
        print('Response by delete post',response)

    def mouseDoubleClickEvent(self, QMouseEvent):
        api = API(self.session, self.token)
        response = api.wall.delete(post_id=self.post_id)

        if response['response'] == 1:
            self.deleteLater()
        print('Response by delete post', response)
