import json

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QFrame, QApplication
from api import UrlAPI
from hRequester import HRequester


class AllPhotosForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)

        self.mainAlbumNames = ['Фотографии с моей страницы', 'Фотографии со мной', 'Фотографии на моей стене', 'Сохранённые фотографии']

        self.parent = parent
        self.chil = [item for item in self.parent.itemList if item.b.checkState() == 2 and item.frozen == 0]

        self.ui()
        self.work()
        self.show()

    def work(self):

        for acc in self.chil:
            self.filing(acc)

    def ui(self):
        self.sizeMonitor = QApplication.desktop().availableGeometry()
        self.setGeometry(0, 0, self.sizeMonitor.width(), self.sizeMonitor.height())

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.albumLayout = QVBoxLayout()
        self.albumWidget = QWidget()
        self.albumWidget.setLayout(self.albumLayout)
        self.mainLayout.addWidget(self.albumWidget)

        scrollWidget = QWidget()
        scrollWidget.setLayout(self.mainLayout)
        scroll = QScrollArea()
        scroll.setWidget(scrollWidget)
        scroll.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

    def filing(self, acc):
        requester = HRequester()
        getUrl = UrlAPI(acc.token)
        urlAlbums  = getUrl.photos.getAlbums(need_system=1)
        requester(urlAlbums, acc.session, 'albums')
        requester(getUrl.photos.getAll(no_service_albums=0, skip_hidden=1, count=200), acc.session, 'photos')

        response = requester.request()

        for r in response:

            if r[2][0] == 'photos':
                dataPhotos = json.loads(r[0].text)['response']
                self.setPhotos(acc, dataPhotos)

            elif r[2][0] == 'albums':
                dataAlbums = json.loads(r[0].text)['response']
                self.setAlbums(acc, dataAlbums)

    def setPhotos(self, acc, dataPhotos):
        requester = HRequester()

        for item in dataPhotos['items']:
            urlPhoto = item['photo_604']
            requester(urlPhoto, acc.session, item['id'])

        response = requester.request()

        for r in response:
            photoByte = r[0]
            photoId = r[2][0]

            photo = Photo(self, photoByte, photoId, acc)
            self.mainLayout.addWidget(photo, alignment=Qt.AlignLeft)

    def setAlbums(self, acc, dataAlbums):

        for album in dataAlbums['items']:

            if album['title'] in self.mainAlbumNames:
                continue

            albumWidget = ItemAlbum(title=album['title'], size=album['size'], id=album['id'], acc=acc)

            self.albumLayout.addWidget(albumWidget)

    def updateWidgetSize(self, widget, layout):
        try:
            if layout.count() == 1:
                widget.setFixedWidth(layout.totalSizeHint().width())
                widget.setFixedHeight(layout.totalSizeHint().height())
                self.setFixedWidth(self.layout().totalSizeHint().width())
            else:
                widget.setFixedWidth(layout.totalSizeHint().width() - (widget.width()/layout.count()))
                widget.setFixedHeight(layout.totalSizeHint().height())
                self.setFixedWidth(self.layout().totalSizeHint().width())
        except:
            self.self.deleteLater()
            return print('Нет фото')




class Photo(QWidget):
    def __init__(self, parent=None, photo=None, id=None, acc=None):
        QWidget.__init__(self, parent)
        self.id = id
        self.acc = acc

        self.pixmap = QPixmap()
        self.pixmap.loadFromData(photo.content)
        labelImg = QLabel()
        myPixmap = self.pixmap.scaled(labelImg.size(), Qt.KeepAspectRatio, Qt.FastTransformation)
        labelImg.setPixmap(myPixmap)

        layout = QVBoxLayout()
        layout.addWidget(labelImg)

        self.setLayout(layout)

    def mouseDoubleClickEvent(self, QMouseEvent):
        requester = HRequester()
        getUrl = UrlAPI(self.acc.token)

        requester(getUrl.photos.delete(photo_id=self.id), self.acc.session)
        response = requester.request()

        for r in response:
            j = json.loads(r[0].text)

            try:
                if j['response'] == 1:
                    self.deleteLater()
            except Exception as e:
                print(repr(e))


class ItemAlbum(QWidget):
    def __init__(self, parent=None, title=None, size=None, id=None, acc=None):
        QWidget.__init__(self, parent)

        self.acc = acc

        albumLayout = QVBoxLayout()
        nameAlbum = QLabel(title)
        countPhoto = QLabel(str(size))
        self.albumId = id
        albumLayout.addWidget(nameAlbum, )
        albumLayout.addWidget(countPhoto)

        frame = QFrame()
        frame.setFrameShape(QFrame.Panel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setLayout(albumLayout)

        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(frame)


    def mouseDoubleClickEvent(self, QMouseEvent):
        requester = HRequester()
        getUrl = UrlAPI(self.acc.token)

        requester(getUrl.photos.deleteAlbum(album_id=self.albumId), self.acc.session)
        response = requester.request()

        for r in response:
            j = json.loads(r[0].text)

            try:
                if j['response'] == 1:
                    self.deleteLater()
            except KeyError:
                print(KeyError, 'Ошибка удаления альбома', r[0])









