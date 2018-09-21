from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QFileDialog
from api import UrlAPI
import json
from downloadDecorator import DownloadDecorator


class ChangeAvatar(QWidget):
    def __init__(self, parent=None, session=None, token=None):
        super().__init__(parent, Qt.Window)
        self.downloader = DownloadDecorator(session)
        self.session = session
        getUrl = UrlAPI(token)

        # choise photos
        path = QFileDialog.getOpenFileName()
        self.session.headers.update(Accept='multipart/form-data')

        # get upload url for photos
        urlUpload = getUrl.photos.getOwnerPhotoUploadServer()
        response = self.session.get(urlUpload, proxies=self.session.proxies)
        j1 = json.loads(response.text)
        urlUpload = j1['response']['upload_url']
        print(response.text)

        try:
            r = self.session.post(urlUpload, files={'photo': open(path[0], 'rb')}, proxies=self.session.proxies)
        except FileNotFoundError:
            return print('Не был выбран файл')

        dataUU = json.loads(r.text)
        print(r.text)

        server = dataUU['server']
        photo = dataUU['photo']
        hash = dataUU['hash']
        saveUrl = getUrl.photos.saveOwnerPhoto(server=server, photo=photo, hash=hash)
        r = self.session.get(saveUrl, proxies=self.session.proxies)
        print(r.text)

        res = json.loads(r.text)
        if 'saved' in res['response']:
            print('Upload avatar completed')





