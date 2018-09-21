import re
import urllib.parse as parse

from bs4 import BeautifulSoup
import sqlite3 as sql
import requests
import json

from PyQt5.QtWidgets import QWidget, QFormLayout, QScrollArea, QVBoxLayout, QHBoxLayout, QFrame, QApplication, QShortcut, QPushButton
from PyQt5.QtGui import QKeySequence
from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt

from downloadDecorator import DownloadDecorator
from methodHandler import MethodHandler
from hRequester import HRequester
from api import UrlAPI

from customWidget.clickableLabel import ClickableLabel
from customWidget.recordWall import RecordWall
from form.changeAvatar import ChangeAvatar
from form.friendsForm import FriendsForm
from form.addPhotoForm import AddPhoto
from form.photosForm import PhotosForm
from form.addPost import AddPost
from form.group import GroupForm


class InfoForm(QWidget):

    def __init__(self, parent=None, session=None, token=None):
        super().__init__(parent, Qt.Window)
        self.ui()

        self.session = session
        self.token = token
        self.currentPhoto = 0
        self.downloadDecorator = DownloadDecorator(self.session)
        self.methodHandler = MethodHandler(self.session, self.token)
        self.createApi = UrlAPI(self.token)
        self.pixmap = QtGui.QPixmap()
        self.curCountRecords = 10

        self.btn_save.clicked.connect(self.save)
        self.btn_photo.clicked.connect(lambda: PhotosForm(self, self.session, self.token, self.dataAllPhotos))
        self.btn_friends.clicked.connect(lambda: FriendsForm(self, self.session, self.token))
        self.avatarImg.clicked.connect(lambda: ChangeAvatar(self, self.session, self.token))
        self.btn_addRecord.clicked.connect(lambda: AddPost(self, self.session, self.token))
        self.btn_addPhoto.clicked.connect(lambda: AddPhoto(self, self.session, self.token))
        self.btn_groups.clicked.connect(lambda: GroupForm(self, self.session, self.token))
        self.btn_load_more_records.clicked.connect(self.loadMoreRecords)
        self.btn_add_group.clicked.connect(lambda: print('add Group'))
        self.btn_setting_privacy.clicked.connect(self.settingPrivacy)
        self.btn_clearingGroups.clicked.connect(self.clearingGroups)

        self.quit = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.quit.activated.connect(self.close)

        try:
            self.getMainInform()
            self.getSecondInform()
        except KeyError:
            print('Ошибка загрузки данных')

        self.show()

    def ui(self):
        uic.loadUi('uiForm/infoFormWall.ui', self)
        self.sizeMonitor = QApplication.desktop().availableGeometry()
        self.setGeometry(self.sizeMonitor.width() / 6, 0, (2 * self.sizeMonitor.width()) / 3, self.sizeMonitor.height())

        self.btn_load_more_records = QPushButton('Load more')
        self.btn_addRecord = QPushButton('+')
        self.avatarImg = ClickableLabel()
        self.myForm = QFormLayout()

        # Create layout with infoWidget
        lay = QHBoxLayout()
        lay.addWidget(self.infoWidget)

        # Frames for layouts
        frame = QFrame()
        frame.setFrameShape(QFrame.Panel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setLayout(lay)

        # Create scroll and put in general layout
        scrollWidget = QWidget()
        scrollWidget.setLayout(self.myForm)
        scroll = QScrollArea()
        scroll.setWidget(scrollWidget)
        scroll.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

        self.myForm.addWidget(frame)
        self.myForm.addWidget(self.btn_addRecord)

        self.avatarLayout.addWidget(self.avatarImg)
        self.avatarImg.setMaximumWidth(self.sizeMonitor.width() / 6)

    def save(self):
        dic = {}

        if self.lineName.text() == self.name:
            pass
        else:
            dic.update(first_name=self.lineName.text())

        if self.lineLastName.text() == self.lastName:
            pass
        else:
            dic.update(last_name=self.lineLastName.text())

        if self.lineBD.text() == self.BD:
            pass
        else:
            dic.update(bdate=self.lineBD.text())

        if self.lineHomeTown.text() == self.homeTown:
            pass
        else:
            dic.update(home_town=self.lineHomeTown.text())

        if self.lineCityId.text() == self.cityId:
            pass
        else:
            dic.update(city_id=self.lineCityId.text())

        if self.lineStatus.text() == self.lineStatus:
            pass
        else:
            dic.update(status=self.lineStatus.text())

        if dic != {}:
            dic.update(bdate_visibility=1)
            self.methodHandler.saveProfileInfo(**dic)

    def getMainInform(self):
        downloader = DownloadDecorator(self.session)

        url = self.createApi.friends.get()
        downloader(url, self.countFriends, 'friends')

        url = self.createApi.groups.get()
        downloader(url, self.countGroups, 'groups')

        url = self.createApi.photos.getAll(no_service_albums=0, skip_hidden=1, count=200)
        downloader(url, 'None', 'allPhotos')

        url = self.createApi.wall.get(extended=1, count=self.curCountRecords)
        downloader(url, 'None', 'wall')

        url = self.createApi.account.getProfileInfo()
        downloader(url, 'None', 'profileInfo')

        # Download and dispersal
        download = downloader.download()
        for item in download:

            if item[2] == 'friends':
                countFriends = item[1]
                self.dataFriends = json.loads(item[0].text)
                self.countFriends.setText(str(self.dataFriends['response']['count']))

            if item[2] == 'groups':
                j = json.loads(item[0].text)
                self.dataGroups = j['response']
                self.countGroups.setText(str(self.dataGroups['count']))

            if item[2] == 'allPhotos':
                j = json.loads(item[0].text)
                self.dataAllPhotos = j['response']
                self.countPhoto.setText(str(self.dataAllPhotos['count']))

            if item[2] == 'wall':
                j = json.loads(item[0].text)
                self.dataWall = j['response']

            if item[2] == 'profileInfo':
                j = json.loads(item[0].text)
                self.dataInfo = j['response']

                lines = [self.lineName, self.lineLastName, self.lineBD, self.lineHomeTown, self.lineStatus,
                         self.lineCountry, self.lineCity, self.lineCityId]

                mas = ['first_name', 'last_name', 'bdate', 'home_town', 'status', 'country', 'city', 'cityId']

                for i in range(len(lines)):
                    item = lines[i]

                    if mas[i] == 'country':
                        try:
                            item.setText(self.dataInfo['country']['title'])
                        except:
                            item.setText('None')

                    elif mas[i] == 'city':
                        try:
                            item.setText(self.dataInfo['city']['title'])
                        except KeyError:
                            item.setText('None')

                    elif mas[i] == 'cityId':
                        try:
                            item.setText(str(self.dataInfo['city']['id']))
                        except KeyError:
                            item.setText('None')

                    else:
                        try:
                            item.setText(self.dataInfo[mas[i]])
                        except KeyError:
                            item.setText('None')

                self.name = self.lineName.text()
                self.lastName = self.lineLastName.text()
                self.BD = self.lineBD
                self.homeTown = self.lineHomeTown
                self.cityId = self.lineCityId

    def getSecondInform(self):
        downloader = DownloadDecorator(self.session)

        # mark reckords wall
        for i in range(len(self.dataWall['items'])):
            record = RecordWall(session=self.session, token=self.token)

            # Set post ID
            record.post_id = self.dataWall['items'][i]['id']

            # Set name
            if self.dataWall['items'][i]['from_id'] == self.dataWall['items'][i]['owner_id']:
                record.setNameLayout('Я', '.', 'src/icon.png')
            else:

                record.setNameLayout(str(self.dataWall['items'][i]['from_id']), '.', 'src/icon.png')

            # Post source
            if 'data' in self.dataWall['items'][i]['post_source']:
                record.setPostSource(self.dataWall['items'][i]['post_source']['data'])

            # Set data
            record.setDateLayout(self.dataWall['items'][i]['date'])

            # Set text
            record.setText(self.dataWall['items'][i]['text'])

            # Attechments
            if 'attachments' in self.dataWall['items'][i]:
                for item in self.dataWall['items'][i]['attachments']:
                    if item['type'] == 'photo':
                        downloader(item['photo']['photo_130'], record.setAttachments, 'wallAtt')

            # Information
            if 'views' in self.dataWall['items'][i]:
                record.setInfo(self.dataWall['items'][i]['likes']['count'],
                               self.dataWall['items'][i]['reposts']['count'],
                               self.dataWall['items'][i]['views']['count'])
            else:
                record.setInfo(self.dataWall['items'][i]['likes']['count'],
                               self.dataWall['items'][i]['reposts']['count'])

            # Repost
            if 'copy_history' in self.dataWall['items'][i]:
                repost = RecordWall()
                repost.deleteInformation()
                repost.delButton.deleteLater()
                repost.frame.setFrameShape(QFrame.StyledPanel)

                repost.setText(self.dataWall['items'][i]['copy_history'][0]['text'])
                repost.setDateLayout(self.dataWall['items'][i]['copy_history'][0]['date'])

                '''Set attachments'''
                if 'attachments' in self.dataWall['items'][i]['copy_history'][0]:
                    for item in self.dataWall['items'][i]['copy_history']:
                        for ite in item['attachments']:
                            if ite['type'] == 'photo':
                                downloader(ite['photo']['photo_604'], repost.setAttachments, 'wallAtt')

                '''Set profile info'''
                for item in self.dataWall['items'][i]['copy_history']:
                    owner_id = item['owner_id']
                    if owner_id < 0:
                        for group in self.dataWall['groups']:
                            if group['id'] == (owner_id * -1):
                                downloader(group['photo_50'], repost.setNameLayout, 'wallAtt', group['name'], '.')

                    elif owner_id > 0:
                        for profile in self.dataWall['profiles']:
                            if profile['id'] == (owner_id):
                                downloader(profile['photo_50'], repost.setNameLayout, 'wallAtt', profile['first_name'],
                                           profile['last_name'])

                record.repostLayout.addWidget(repost)

            self.myForm.addRow(record)

        # Append btn for load more records
        self.myForm.addRow(self.btn_load_more_records)

        # mark allPhotos
        masLabelImg = [self.labelImg1, self.labelImg2, self.labelImg3, self.labelImg4]
        for nLabelImg in range(len(masLabelImg)):
            try:
                urlPhoto = self.dataAllPhotos['items'][nLabelImg]['photo_604']
                downloader(urlPhoto, masLabelImg[nLabelImg], 'allPhotosAtt')
            except:
                pass

        # mark avatar
        masAvatar = []
        for item in self.dataAllPhotos['items']:
            if item['album_id'] == -6:
                masAvatar.append([item['photo_604'], item['id']])

        masAvatar.sort(key=lambda mas: mas[1], reverse=1)

        try:
            downloader(masAvatar[0][0], 'None', 'avatarPhoto')
        except:
            pass

        download = downloader.download()

        for item in download:

            if item[2] == 'wallAtt':
                if item[3] == ():
                    seter = item[1]
                    photo = item[0]
                    seter(photo.content)
                elif item[3] != ():
                    mas = []
                    for i in item[3]:
                        mas.append(i)
                    seter = item[1]
                    photo = item[0]
                    seter(*mas, photo.content)

            if item[2] == 'allPhotosAtt':
                photo = item[0]
                self.pixmap.loadFromData(photo.content)
                myPixmap = self.pixmap.scaled(self.labelImg1.size(), Qt.KeepAspectRatio, Qt.FastTransformation)
                labelImg = item[1]
                labelImg.setPixmap(myPixmap)

            if item[2] == 'avatarPhoto':
                photo = item[0]
                self.pixmap.loadFromData(photo.content)
                myPixmap = self.pixmap.scaled(self.avatarImg.size(), Qt.KeepAspectRatio, Qt.FastTransformation)
                self.avatarImg.setPixmap(myPixmap)

    def loadMoreRecords(self):
        downloader = DownloadDecorator(self.session)
        offset = self.curCountRecords + 1
        self.curCountRecords = self.curCountRecords + 50

        url = self.createApi.wall.get(extended=1, count=50, offset=offset)
        response = requests.get(url, proxies=self.session.proxies)
        self.dataWall = json.loads(response.text)['response']

        # mark reckords wall
        for i in range(len(self.dataWall['items'])):
            record = RecordWall(session=self.session, token=self.token)

            # Set post ID
            record.post_id = self.dataWall['items'][i]['id']

            # Set name
            if self.dataWall['items'][i]['from_id'] == self.dataWall['items'][i]['owner_id']:
                record.setNameLayout('Я', '.', 'src/icon.png')
            else:

                record.setNameLayout(str(self.dataWall['items'][i]['from_id']), '.', 'src/icon.png')

            # Post source
            if 'data' in self.dataWall['items'][i]['post_source']:
                record.setPostSource(self.dataWall['items'][i]['post_source']['data'])

            # Set data
            record.setDateLayout(self.dataWall['items'][i]['date'])

            # Set text
            record.setText(self.dataWall['items'][i]['text'])

            # Attechments
            if 'attachments' in self.dataWall['items'][i]:
                for item in self.dataWall['items'][i]['attachments']:
                    if item['type'] == 'photo':
                        downloader(item['photo']['photo_130'], record.setAttachments, 'wallAtt')

            # Information
            if 'views' in self.dataWall['items'][i]:
                record.setInfo(self.dataWall['items'][i]['likes']['count'],
                               self.dataWall['items'][i]['reposts']['count'],
                               self.dataWall['items'][i]['views']['count'])
            else:
                record.setInfo(self.dataWall['items'][i]['likes']['count'],
                               self.dataWall['items'][i]['reposts']['count'])

            # Repost
            if 'copy_history' in self.dataWall['items'][i]:
                repost = RecordWall()
                repost.deleteInformation()
                repost.delButton.deleteLater()
                repost.frame.setFrameShape(QFrame.StyledPanel)

                repost.setText(self.dataWall['items'][i]['copy_history'][0]['text'])
                repost.setDateLayout(self.dataWall['items'][i]['copy_history'][0]['date'])

                '''Set attachments'''
                if 'attachments' in self.dataWall['items'][i]['copy_history'][0]:
                    for item in self.dataWall['items'][i]['copy_history']:
                        for ite in item['attachments']:
                            if ite['type'] == 'photo':
                                downloader(ite['photo']['photo_604'], repost.setAttachments, 'wallAtt')

                '''Set profile info'''
                for item in self.dataWall['items'][i]['copy_history']:
                    owner_id = item['owner_id']
                    if owner_id < 0:
                        for group in self.dataWall['groups']:
                            if group['id'] == (owner_id * -1):
                                downloader(group['photo_50'], repost.setNameLayout, 'wallAtt', group['name'], '.')

                    elif owner_id > 0:
                        for profile in self.dataWall['profiles']:
                            if profile['id'] == (owner_id):
                                downloader(profile['photo_50'], repost.setNameLayout, 'wallAtt', profile['first_name'],
                                           profile['last_name'])

                record.repostLayout.addWidget(repost)

            self.myForm.addRow(record)

        # Append btn for load more records
        self.myForm.addRow(self.btn_load_more_records)

        download = downloader.download()

        for item in download:

            if item[2] == 'wallAtt':

                if item[3] == ():
                    seter = item[1]
                    photo = item[0]
                    seter(photo.content)
                elif item[3] != ():
                    mas = []
                    for i in item[3]:
                        mas.append(i)
                    seter = item[1]
                    photo = item[0]
                    seter(*mas, photo.content)

    def clearingGroups(self):
        getUrl = UrlAPI(self.token)
        requester = HRequester()

        responseGroups = requests.get(getUrl.groups.get(extended=1), proxies=self.session.proxies)
        items = json.loads(responseGroups.text)['response']['items']

        with open('files/cities', 'r') as f:
            lines = f.readlines()

        for item in items:
            for line in lines:
                result = re.search(line.lower().strip('\n'), item['name'].lower())

                if result:
                    leave = requests.get(getUrl.groups.leave(group_id=item['id']), proxies=self.session.proxies)
                    print(leave.text, item['name'])
                    #requester(getUrl.groups.leave(group_id=item['id']), self.session, item['name'])

    def settingPrivacy(self):
        requester = HRequester()
        con = sql.connect('db/db.sqlite3')
        cur = con.cursor()

        #Login
        responseLoginPage = self.session.get('https://m.vk.com', proxies=self.session.proxies)

        soup = BeautifulSoup(responseLoginPage.text)
        urlLogin = soup.find('form').get('action')

        with con:
            cur.execute('SELECT login, pass, user_id FROM accaunt WHERE token = ?', (self.token,))
            row = cur.fetchone()
            login = row[0]
            password = row[1]
            user_id = row[2]

            self.session.params.update(email=login)
            self.session.params.update({'pass': password})

            responseLogin = self.session.get(urlLogin, allow_redirects=False, proxies=self.session.proxies)

            params = ['mail_send', 'profile', 'audios', 'gifts', 'wall_send']

            for param in params:
                self.setting(param)

        # Close coments under wall post and display walls record
        url1 = self.createApi.account.setInfo(name='own_posts_default', value=0)
        url2 = self.createApi.account.setInfo(name='no_wall_replies', value=1)
        requester(url1, self.session)
        requester(url2, self.session)
        response = requester.request()
        for r in response:
            j = json.loads(r[0].text)
            if j['response'] == 1:
                print(
                    'Успешно включено отображение записей на стене пользователя и закрыты коментарии на стене')

    def setting(self, param):
        self.session.params.clear()
        self.session.params.update(_ref='settings')
        url = 'https://m.vk.com/settings?act=privacy&privacy_edit='+param
        responsePrivacy = self.session.get(url, proxies=self.session.proxies)
        soup = BeautifulSoup(responsePrivacy.text)
        f = lambda: re.split('&', soup.find('form').get('action'))[1]
        hash = re.split('=', f())[1]

        self.session.params.clear()

        if param == 'mail_send':
            self.session.params.update(val='3', _tstat='settings%2C0%2C0%2C1020%2C23', _ref='settings')
        else:
            self.session.params.update(val='0', _tstat='settings%2C0%2C0%2C1020%2C23', _ref='settings')

        url = 'https://m.vk.com/settings?act=save_privacy&hash=' + hash + '&key=' + param
        responseSave = self.session.get(url, allow_redirects=False, proxies=self.session.proxies)

        if responseSave.headers['Location'] == ('/settings?act=privacy#pv_' + param):
            print('Успешно', param)
        else:
            print('Неуспешно', param)







