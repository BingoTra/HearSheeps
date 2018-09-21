from PyQt5 import QtGui, QtCore

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QFormLayout, QScrollArea, QVBoxLayout, QPushButton, QFrame, QLabel, \
    QHBoxLayout

from api import API


class FriendsForm(QWidget):
    def __init__(self, parent=None, session=None, token=None):
        super().__init__(parent, Qt.Window)
        self.ui()

        self.session = session
        self.token = token
        api = API(self.session, self.token)

        friends = api.friends.get(order='hints', name_case='nom', fields='name,last_name')

        for friend in friends['response']['items']:
            f = Friend(session=session, token=token)
            f.setFriendInfo(friend['first_name'] + ' ' + friend['last_name'], friend['id'])
            self.myForm.addWidget(f)

        self.show()

    def ui(self):
        self.sizeMonitor = QApplication.desktop().availableGeometry()
        self.setGeometry(self.sizeMonitor.width() / 6, 0, (2 * self.sizeMonitor.width()) / 3, self.sizeMonitor.height())

        self.myForm = QFormLayout()

        # Create scroll and put in general layout
        scrollWidget = QWidget()
        scrollWidget.setLayout(self.myForm)
        scroll = QScrollArea()
        scroll.setWidget(scrollWidget)
        scroll.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)



class Friend(QWidget):
    def __init__(self, parent=None, session=None, token=None):
        QWidget.__init__(self, parent)
        self.pixmap = QtGui.QPixmap()
        self.api = API(session, token)

        self.nameLayout = QHBoxLayout()
        self.icon = QLabel()
        self.name = QLabel()
        self.id = 0
        self.deleteFriend = QPushButton('Del')
        self.nameLayout.addWidget(self.icon, 0)
        self.nameLayout.addWidget(self.name, 1)
        self.nameLayout.addWidget(self.deleteFriend, 2, QtCore.Qt.AlignRight)

        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Panel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setLayout(self.nameLayout)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.frame)

        self.setLayout(self.mainLayout)

        self.name.setStyleSheet('''color: rgb(60,  50,  130);''')
        self.frame.setStyleSheet('''background-color:rgb(255, 255, 255);''')

        self.deleteFriend.clicked.connect(self.delete)

    def setFriendInfo(self, name, id):
        self.name.setText(name)
        self.id = id

    def delete(self):
        response = self.api.friends.delete(user_id=self.id)
        if response['response']['success'] == 1:
            self.deleteLater()
            print('Frend deleted')
        else:
            print('error')
