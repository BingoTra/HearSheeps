from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QFileDialog
from api import UrlAPI
import json
from downloadDecorator import DownloadDecorator


class AddPhoto(QWidget):
    def __init__(self, parent=None, session=None, token=None):
        super().__init__(parent, Qt.Window)
        self.downloader = DownloadDecorator(session)
        self.session = session
        getUrl = UrlAPI(token)
        albumId = 0

        code = '''
        var album = API.photos.getAlbums({"need_system":1});
        var albumsTitle = album.items@.title;
        var albumsId = album.items@.id;
        var albumId = 0;
        
        var i = 0;
        while (i < albumsTitle.length) {
            if ("Мои фото" == albumsTitle[i]){
                albumId = albumsId[i];
        	i = 999;
            }
            
            i = i + 1;
        };
        
        if (albumId == 0){
        	var createAlbum = API.photos.createAlbum({"title":"Мои фото"});
        	albumId = createAlbum["id"];
            }
        
        
        var urlUploadServer = API.photos.getUploadServer({"album_id":albumId});
        var url = urlUploadServer["upload_url"];
        
        var mas = [albumId, url];
        
        return mas;
        '''

        #get upload url for photos
        urlGetUploadServer = getUrl.execute()
        response = self.session.post(urlGetUploadServer, data={'code': code}, proxies=self.session.proxies)
        j1 = json.loads(response.text)
        albumId = j1['response'][0]
        upload_url = j1['response'][1]

        #choise photos
        paths = QFileDialog.getOpenFileNames()
        self.session.headers.update(Accept='multipart/form-data')

        #upload photos
        for path in paths[0]:
            r = self.session.post(upload_url, files={'photo': open(path, 'rb')}, proxies=self.session.proxies)
            dataUU = json.loads(r.text)

            server = dataUU['server']
            photos_list = dataUU['photos_list']
            hash = dataUU['hash']
            saveUrl = getUrl.photos.save(album_id=albumId, server=server, photos_list=photos_list, hash=hash)
            self.downloader(saveUrl, 'None', 'savePhotos')

        download = self.downloader.download()
        for item in download:
            print(item[0].text)




