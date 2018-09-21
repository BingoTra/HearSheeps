import json

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QFrame, QApplication, QListWidget
from api import UrlAPI
from hRequester import HRequester


class AvatarForChek(QWidget):
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
            urlAvatars = getUrl.users.get(fields='photo_50')
            requester(urlAvatars, acc.session, acc)

        response = requester.request()

        for r in response:
            acc = r[2][0]

            try:
                dataAvatars = json.loads(r[0].text)['response'][0]

                if dataAvatars['photo_50'] != 'https://vk.com/images/camera_50.png':
                    acc.b.setChecked(True)
                else:
                    acc.b.setChecked(False)

            except Exception as e:
                print(repr(e))








