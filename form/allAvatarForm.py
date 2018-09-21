import json

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QFrame, QApplication
from api import UrlAPI
from form.changeAvatar import ChangeAvatar
from hRequester import HRequester


class AllAvatarForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)

        self.mainAlbumNames = ['Фотографии с моей страницы', 'Фотографии со мной', 'Фотографии на моей стене', 'Сохранённые фотографии']

        self.parent = parent
        self.chil = [item for item in self.parent.itemList if item.b.checkState() == 2 and item.frozen == 0]

        self.ui()
        self.filing()
        self.show()


    def ui(self):
        self.sizeMonitor = QApplication.desktop().availableGeometry()
        self.setGeometry(0, 0, self.sizeMonitor.width(), self.sizeMonitor.height())

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)


        scrollWidget = QWidget()
        scrollWidget.setLayout(self.mainLayout)
        scroll = QScrollArea()
        scroll.setWidget(scrollWidget)
        scroll.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)


    def filing(self):
        requester = HRequester()

        for acc in self.chil:
            getUrl = UrlAPI(acc.token)

            urlAvatars = getUrl.users.get(fields='photo_200')
            requester(urlAvatars, acc.session, acc)

        response = requester.request()

        for r in response:
            acc = r[2][0]

            try:
                dataAvatars = json.loads(r[0].text)['response'][0]

                if dataAvatars['photo_200'] != 'https://vk.com/images/camera_200.png':
                    requester(dataAvatars['photo_200'], acc.session, acc)
                else:
                    photo = Photo(self, None, acc)
                    self.mainLayout.addWidget(photo, alignment=Qt.AlignLeft)

            except Exception as e:
                print(repr(e))

        response = requester.request()

        for r in response:
            acc = r[2][0]
            photoByte = r[0]
            photo = Photo(self, photoByte, acc)
            self.mainLayout.addWidget(photo, alignment=Qt.AlignLeft)




class Photo(QWidget):
    def __init__(self, parent=None, photo=None, acc=None):
        QWidget.__init__(self, parent)
        self.acc = acc

        if photo == None:
            self.pixmap = QPixmap()
            self.pixmap.load('./src/sheep_icon.png')
            labelImg = QLabel()
            myPixmap = self.pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.FastTransformation)
            labelImg.setPixmap(myPixmap)
        else:
            self.pixmap = QPixmap()
            self.pixmap.loadFromData(photo.content)
            labelImg = QLabel()
            myPixmap = self.pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.FastTransformation)
            labelImg.setPixmap(myPixmap)

        layout = QHBoxLayout()
        layout.addWidget(labelImg)
        layout.addWidget(QLabel(acc.name))
        layout.addWidget(QLabel(acc.last_name))

        self.setLayout(layout)

    def mouseDoubleClickEvent(self, QMouseEvent):
        ChangeAvatar(self, self.acc.session, self.acc.token)







