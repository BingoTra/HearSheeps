import json
import random
import re
import sqlite3 as sql
import time

import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QHBoxLayout

from api import UrlAPI
from form.surveyForm import SurveyForm
from hRequester import HRequester


class LikeMachine(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.con = sql.connect('db/db.sqlite3')
        self.cur = self.con.cursor()

        self.ui()
        self.parent = parent

        self.btn_avatar.clicked.connect(self.avatar)
        self.btn_numRecord.clicked.connect(self.numRecord)
        self.btn_specificRecord.clicked.connect(self.specificRecord)

        self.chil = [item for item in self.parent.itemList if item.b.checkState() == 2 and item.frozen == 0]
        self.lenght = len(self.chil)
        self.requester = HRequester()

    def ui(self):
        self.btn_avatar = QPushButton('Аватар')

        self.line_numberRevord = QLineEdit()
        self.btn_numRecord = QPushButton('Запись по счету')
        numRecLay = QHBoxLayout()
        numRecLay.addWidget(self.line_numberRevord)
        numRecLay.addWidget(self.btn_numRecord)

        self.lineType = QLineEdit()
        self.lineEditOwner = QLineEdit()
        self.lineEditItem = QLineEdit()
        self.lineEditOwner.setText('Owner id')
        self.lineEditItem.setText('Item id')
        self.btn_specificRecord = QPushButton('Конкретная запись')
        specRecLay = QHBoxLayout()
        specRecLay.addWidget(self.lineType)
        specRecLay.addWidget(self.lineEditOwner)
        specRecLay.addWidget(self.lineEditItem)
        specRecLay.addWidget(self.btn_specificRecord)

        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self.btn_avatar)
        mainLayout.addLayout(numRecLay)
        mainLayout.addLayout(specRecLay)

    def numRecord(self):

        for item in self.chil:
            getUrl = UrlAPI(item.token)
            self.requester(getUrl.wall.get(count=1, offset=self.line_numberRevord.text()), item.session, item)

        response = self.requester.request()
        for r in response:
            record = json.loads(r[0].text)['response']['items'][0]
            acc = r[2][0]
            acc.item_id = record['id']

        self.run('post')

    def avatar(self):
        getMainUrl = UrlAPI(self.chil[0].token)

        url = getMainUrl.users.get(user_ids=','.join([str(item.user_id) for item in self.chil]), fields='photo_id')
        responseMain = requests.get(url, proxies=self.chil[0].session.proxies)

        data = json.loads(responseMain.text)['response']

        for acc in data:
            try:
                info = acc['photo_id'].strip('photo')
            except KeyError:
                print(acc)

                for i in range(len(self.chil)):
                    if int(self.chil[i].user_id) == int(acc['id']):
                        self.chil.pop(i)
                        break

                self.lenght = len(self.chil)

                continue

            info = re.split('_', info)
            owner_id = info[0]
            item_id = info[1]

            item = [item for item in self.chil if int(item.user_id) == int(owner_id)]
            item[0].item_id = item_id

        self.run('photo')

    def run(self, type_record):

        for i in range(self.lenght):

            with self.con:
                self.cur.execute('SELECT * FROM like')
                likeTable = self.cur.fetchall()

            for j in range(self.lenght):
                getUrl = UrlAPI(self.chil[j].token)

                if j + i > len(self.chil) - 1:
                    index_owner_id = i - (self.lenght - 1 - j) - 1

                    if index_owner_id < 0:
                        index_owner_id = 0

                else:
                    index_owner_id = j + i

                owner_item_id = str(self.chil[index_owner_id].user_id) + '_' + str(self.chil[index_owner_id].item_id)

                # Проверям есть ли запить о данном юзере с итемом, если нету, то создаем
                if not [row for row in likeTable if row[1] == owner_item_id]:
                    with self.con:
                        self.cur.execute('INSERT INTO like (user_id, owner_item_id) VALUES (?,?)',
                                         (self.chil[index_owner_id].user_id, owner_item_id))
                        self.con.commit()

                #Смотрим есть ли данный лайк, если нето, то продолжаем
                with self.con:
                    self.cur.execute('SELECT * FROM accaunt_like WHERE owner_item_id=? and liker=?',
                                     (owner_item_id, self.chil[j].user_id))
                    rowAL = self.cur.fetchone()

                    if not rowAL:
                        urlLikeAdd = getUrl.likes.add(type=type_record,
                                                      owner_id=self.chil[index_owner_id].user_id,
                                                      item_id=self.chil[index_owner_id].item_id)
                        self.requester(urlLikeAdd, self.chil[j].session, self.chil[j], self.chil[index_owner_id])

            if not self.requester.taskList:
                print('pass')
                continue
            else:
                response = self.requester.request()
                for r in response:
                    countUnsuccessfulLike = 0

                    try:
                        jResponse = json.loads(r[0].text)['response']
                        liker = r[2][0]
                        owner = r[2][1]
                    except KeyError:
                        print(KeyError, r[0].text)
                        countUnsuccessfulLike += 1
                        continue

                    if 'likes' in jResponse:
                        with self.con:
                            cur = self.con.cursor()
                            owner_item_id = str(owner.user_id) + '_' + str(owner.item_id)
                            cur.execute('INSERT INTO accaunt_like (owner_item_id, liker) VALUES(?,?)',
                                        (owner_item_id, liker.user_id))
                    else:
                        countUnsuccessfulLike += 1
                        print(r[0].text)

                if countUnsuccessfulLike == 0:
                    print('Лайки поставлены')
                else:
                    print('Кол-во не поставленных:', countUnsuccessfulLike)

                time.sleep(random.randint(120, 200))


            print('Выполнено:', str(i) + '/' + str(self.lenght))
            if i == 25:
                self.deleteLater()


    def specificRecord(self):
        errorListAcc = []

        for i in range(self.lenght):
            getUrl = UrlAPI(self.chil[i].token)
            urlLikeAdd = getUrl.likes.add(type=self.lineType.text(), owner_id=self.lineEditOwner.text(),
                                             item_id=self.lineEditItem.text())
            self.requester(urlLikeAdd, self.chil[i].session, self.chil[i])

        response = self.requester.request()
        for r in response:
            acc = r[2][0]
            j = json.loads(r[0].text)

            if 'response' in j:

                if j['response'] == 1:
                    pass
                else:
                    print(j)

            elif 'error' in j:
                print(j)
                acc.responseError = j
                errorListAcc.append(acc)

        if len(errorListAcc) == 0:
            self.parent.statusBar.showMessage('Лайки поставлены')
        else:
            self.parent.statusBar.showMessage('Лайки поставлены с ошибками')
            self.parent.widgetsConductor(SurveyForm(self.parent, errorListAcc), show=True)
