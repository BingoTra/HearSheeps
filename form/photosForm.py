import json
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from downloadDecorator import DownloadDecorator
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QFrame
import datetime
from api import UrlAPI, API


class PhotosForm(QWidget):
    def __init__(self, parent=None, session=None, token=None, dataAllPhotos=None ):
        super().__init__(parent, Qt.Window)

        self.session = session
        self.token = token
        self.dataAllPhotos = dataAllPhotos
        self.createApi = UrlAPI(self.token)
        self.api = API(self.session, self.token)

        self.ui()
        self.filing()
        self.show()

    def ui(self):
        self.setGeometry(300, 100, 700, 500)
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.albumLayout = QHBoxLayout()
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

    def filing(self):
        downloader = DownloadDecorator(self.session)
        urlAlbums  = self.createApi.photos.getAlbums(need_system=1)
        downloader(urlAlbums, 'None', 'albums')

        for item in self.dataAllPhotos['items']:
            value = datetime.datetime.fromtimestamp(item['date'])
            urlPhoto = item['photo_604']
            downloader(urlPhoto, value.year, 'photos', item['id'])

        download = downloader.download()
        groupYear = [[0, 0]]

        for item in download:

            if item[2] == 'photos':
                photo = Photo(self, item[0], item[3][0], self.api)
                year = item[1]
                yearWidget = QWidget()
                yearLayout = QHBoxLayout()

                b = False
                for mas in groupYear:
                    if year in mas:
                        yearLayout = mas[1]
                        yearLayout.addWidget(photo, alignment=Qt.AlignLeft)
                        yearWidget = mas[2]

                        self.updateWidgetSize(yearWidget, yearLayout)
                        b = True

                        break

                if b == False:
                    yearLayout = QHBoxLayout()
                    yearLayout.addWidget(photo, alignment=Qt.AlignLeft)
                    yearWidget = QWidget()
                    yearWidget.setLayout(yearLayout)
                    labelYear = QLabel(str(year))

                    self.mainLayout.addWidget(labelYear, alignment=Qt.AlignLeft)
                    self.mainLayout.addWidget(yearWidget, alignment=Qt.AlignLeft)
                    self.updateWidgetSize(yearWidget, yearLayout)

                    groupYear.append([year, yearLayout, yearWidget])

                photo.clicked.connect(lambda : self.updateWidgetSize(yearWidget, yearLayout))



            if item[2] == 'albums':
                data = json.loads(item[0].text)

                for album in data['response']['items']:
                    albumWidget = ItemAlbum(title=album['title'], size=album['size'], id=album['id'], api=self.api)

                    self.albumLayout.addWidget(albumWidget)
                    self.albumWidget.setFixedWidth(self.albumLayout.totalSizeHint().width())
                    self.albumWidget.setFixedHeight(self.albumLayout.totalSizeHint().height())

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
    clicked = pyqtSignal()


    def __init__(self, parent=None, photo=None, id=None, api=None):
        QWidget.__init__(self, parent)
        self.id = id
        self.api = api

        self.pixmap = QPixmap()
        self.pixmap.loadFromData(photo.content)
        labelImg = QLabel()
        myPixmap = self.pixmap.scaled(labelImg.size(), Qt.KeepAspectRatio, Qt.FastTransformation)
        labelImg.setPixmap(myPixmap)

        layout = QVBoxLayout()
        layout.addWidget(labelImg)


        self.setLayout(layout)

    def mouseDoubleClickEvent(self, QMouseEvent):
        response = self.api.photos.delete(photo_id=self.id)

        if response['response'] == 1:
            self.deleteLater()
            self.clicked.emit()


class ItemAlbum(QWidget):
    def __init__(self, parent=None, title=None, size=None, id=None, api=None):
        QWidget.__init__(self, parent)

        self.api = api

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
        response = self.api.photos.deleteAlbum(album_id=self.albumId)

        try:
            if response['response'] == 1:
                self.deleteLater()
        except KeyError:
            print(KeyError, 'Ошибка удаления альбома', response)









