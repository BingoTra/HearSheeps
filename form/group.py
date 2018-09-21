from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QFrame, QApplication, QFormLayout, \
    QScrollArea
from PyQt5.QtCore import Qt
from downloadDecorator import DownloadDecorator
from api import API


class GroupForm(QWidget):
    def __init__(self, parent=None, session=None, token=None):
        super().__init__(parent, Qt.Window)
        self.sizeMonitor = QApplication.desktop().availableGeometry()
        self.setGeometry(self.sizeMonitor.width() / 6, 0, (2 * self.sizeMonitor.width()) / 3, self.sizeMonitor.height())

        myForm = QFormLayout()

        # Create scroll and put in general layout
        scrollWidget = QWidget()
        scrollWidget.setLayout(myForm)
        scroll = QScrollArea()
        scroll.setWidget(scrollWidget)
        scroll.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

        downloader = DownloadDecorator(session)
        api = API(session, token)

        groups = api.groups.get(extended=1)
        for group in groups['response']['items']:
            downloader(group["photo_100"], 'None', 'group', group['name'], group['id'])

        download = downloader.download()
        for item in download:
            g = Group(session=session, token=token)
            g.setGroup(item[0].content, item[3][0], item[3][1])
            myForm.addWidget(g)

        self.show()



class Group (QWidget):
    def __init__(self, parent = None, session=None, token=None):
        QWidget.__init__(self, parent)
        self.pixmap        = QtGui.QPixmap()
        self.api = API(session, token)

        self.nameLayout    = QHBoxLayout()
        self.icon          = QLabel()
        self.name          = QLabel()
        self.id            = 0
        self.deletGroup    = QPushButton('Del')
        self.nameLayout.addWidget(self.icon, 0)
        self.nameLayout.addWidget(self.name, 1)
        self.nameLayout.addWidget(self.deletGroup, 2, QtCore.Qt.AlignRight)

        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Panel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setLayout(self.nameLayout)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.frame)

        self.setLayout(self.mainLayout)

        self.name.setStyleSheet(  '''color: rgb(60,  50,  130);''')
        self.frame.setStyleSheet(     '''background-color:rgb(255, 255, 255);''')

        self.deletGroup.clicked.connect(self.delete)

    def setGroup(self, image, name, id):
        self.name.setText(name)
        self.id = id

        self.pixmap.loadFromData(image)
        myPixmap = self.pixmap.scaled(64, 64, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        self.icon.setPixmap(myPixmap)

    def delete(self):
        response = self.api.groups.leave(group_id=self.id)
        if response['response'] ==1:
            self.deleteLater()
            print('Leave group')
        else:
            print('error')
