import json
import random
import sqlite3 as sql

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QShortcut, QWidget, QVBoxLayout, QFormLayout, QScrollArea
from requests import Session

import MyData
from api import UrlAPI
from customWidget.recordWall import RecordWall
from hRequester import HRequester


class RepostsForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)

        self.reposts = []
        self.requester = HRequester()

        self.ui()
        self.getRepostsFromBD()
        self.downloadReposts()

        QShortcut(QtGui.QKeySequence(Qt.Key_Escape), self).activated.connect(self.close)

    def getRepostsFromBD(self):
        con = sql.connect('./db/db.sqlite3')
        cur = con.cursor()

        with con:
            cur.execute('SELECT proxy,user_agent,token FROM accaunt')
            random_acc = random.choice(cur.fetchall())
            self.proxy = random_acc[0]
            self.user_agent = random_acc[1]
            self.token = random_acc[2]

            cur.execute('SELECT group_post_id FROM repost')
            reposts = cur.fetchall()
            reposts.reverse()
            [self.reposts.append(r[0]) for r in reposts]

            if not self.reposts:
                self.deleteLater()
                return print('Нет репостов')

    def getLine(self, n):
        self.numberOfCall += 10
        masPosts = []

        for i in range(self.numberOfCall - 500, self.numberOfCall):
            try:
                masPosts.append(self.mas_ids[i])
            except Exception as exeption:
                print(exeption)
                return '''var posts'''+ str(n) +'''= API.wall.getById({"posts":"''' + ",".join(self.reposts) + '''", "fields":"photo_id"});'''

        return '''var friends'''+ str(n) +'''= API.users.get({"user_ids":"''' + ",".join(masUsers) + '''"});'''

    def downloadReposts(self):
        con = sql.connect('./db/db.sqlite3')
        cur = con.cursor()

        s = Session()
        s.proxies.update(http=self.proxy, https=self.proxy, all=self.proxy)
        s.headers.update({'User-Agent': self.user_agent, 'Accept': MyData.ACCEPT, 'Accept-Language': MyData.ACCEPT_LANGUAGE})

        getUrl = UrlAPI(self.token)

        for i in range(divmod(len(self.reposts), 20)[0] + 1):


                if i > divmod(len(self.reposts),20)[0]:
                    url = getUrl.wall.getById(posts=','.join([self.reposts[j] for j in range(i*20, i*20+divmod(len(self.reposts),20)[1])]))
                    self.requester(url, s)
                elif i <= divmod(len(self.reposts),20)[0]:
                    # try:
                        url = getUrl.wall.getById(posts=','.join([self.reposts[j] for j in range(i*20, i*20+20)]))
                        self.requester(url, s)
                    # except Exception as e:
                    #     print(e)
                        print(i, i*20)

        response = self.requester.request()
        for r in response:

            try:
                records = json.loads(r[0].text)['response']
            except Exception as e:
                print(e)
                print(r[0].text)
                return

            for record in records:
                repostWidget = RepostWidget()
                repostWidget.users = []
                repostWidget.group_post_id = str(record['owner_id']) + '_' + str(record['id'])

                # set information
                if 'views' in record:
                    repostWidget.setInfo(record['likes']['count'], record['reposts']['count'], record['views']['count'])
                else:
                    repostWidget.setInfo(record['likes']['count'], record['reposts']['count'])

                # set text
                repostWidget.setText(record['text'])

                # set attachments
                if 'attachments' in record:

                    for attach in record['attachments']:

                        if attach['type'] == 'photo':
                            self.requester(attach['photo']['photo_604'], s, repostWidget)

                # Append users in recordWidget
                with con:
                    cur.execute('SELECT user_id FROM accaunt_repost WHERE group_post_id=?',
                                (str(record['owner_id']) + '_' + str(record['id']),))
                    [repostWidget.users.append(user[0]) for user in cur.fetchall()]

                self.myForm.addWidget(repostWidget)

            responseImg = self.requester.request()
            for item in responseImg:
                recordWidget = item[2][0]
                recordWidget.setAttachments(item[0].content)

    def ui(self):
        a = QApplication.desktop().availableGeometry()
        self.setGeometry(300, 100, a.width() / 2, a.height() / 2)

        # Create scroll and put in general layout
        self.myForm = QFormLayout()

        scrollWidget = QWidget()
        scrollWidget.setLayout(self.myForm)
        scroll = QScrollArea()
        scroll.setWidget(scrollWidget)
        scroll.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

        self.show()


class RepostWidget(RecordWall):

    def deletePost(self):
        requester = HRequester()
        con = sql.connect(MyData.CWD + '/db/db.sqlite3')
        cur = con.cursor()

        with con:
            query = '''
            select
            accaunt.user_id, accaunt.proxy, accaunt.user_agent, accaunt.token, accaunt_repost.post_id
            from accaunt, accaunt_repost
            where
            accaunt.user_id = accaunt_repost.user_id and accaunt_repost.group_post_id = ?
            '''
            cur.execute(query, (self.group_post_id,))
            #query = 'select proxy, user_agent, token from accaunt where user_id in (%s)' % ', '.join(['?'] * len(self.users_posts))
            #cur.execute(query, [user[0] for user in self.users_posts])
            accaunts = cur.fetchall()

        for acc in accaunts:
            user_id = acc[0]
            proxy = acc[1]
            user_agent = acc[2]
            token = acc[3]
            post_id = acc[4]

            session = Session()
            session.proxies.update(http=proxy, https=proxy, all=proxy)
            session.headers.update({'User-Agent': user_agent})

            getUrl = UrlAPI(token)
            requester(getUrl.wall.delete(post_id=post_id), session, user_id, post_id)

        response = requester.request()
        for r in response:
            user_id = r[2][0]
            post_id = r[2][1]
            j = json.loads(r[0].text)

            print(user_id, post_id)

            try:
                if j['response'] == 1:
                    cur.execute('DELETE FROM accaunt_repost WHERE user_id = ? and post_id = ?', (user_id, post_id))
                    con.commit()
                else:
                    print('Ошибка удаления поста у', user_id, 'post_id', post_id)
            except KeyError:
                print(KeyError, j)

        print('Удаление завершено')

        cur.execute('SELECT * FROM accaunt_repost WHERE group_post_id = ?', (self.group_post_id,))
        rezult = cur.fetchall()
        print(rezult, rezult)

        if not rezult:
            cur.execute('DELETE FROM repost WHERE group_post_id = ?', (self.group_post_id,))
            con.commit()
            self.deleteLater()

    def mouseDoubleClickEvent(self, QMouseEvent):
        requester = HRequester()
        con = sql.connect(MyData.CWD + '/db/db.sqlite3')
        cur = con.cursor()

        with con:
            query = '''
                    select
                    accaunt.user_id, accaunt.proxy, accaunt.user_agent, accaunt.token, accaunt_repost.post_id
                    from accaunt, accaunt_repost
                    where
                    accaunt.user_id = accaunt_repost.user_id and accaunt_repost.group_post_id = ?
                    '''
            cur.execute(query, (self.group_post_id,))
            # query = 'select proxy, user_agent, token from accaunt where user_id in (%s)' % ', '.join(['?'] * len(self.users_posts))
            # cur.execute(query, [user[0] for user in self.users_posts])
            accaunts = cur.fetchall()

        for acc in accaunts:
            user_id = acc[0]
            proxy = acc[1]
            user_agent = acc[2]
            token = acc[3]
            post_id = acc[4]

            session = Session()
            session.proxies.update(http=proxy, https=proxy, all=proxy)
            session.headers.update({'User-Agent': user_agent})

            getUrl = UrlAPI(token)
            requester(getUrl.wall.delete(post_id=post_id), session, user_id, post_id)

        response = requester.request()
        for r in response:
            user_id = r[2][0]
            post_id = r[2][1]
            j = json.loads(r[0].text)

            print(user_id, post_id)

            try:
                if j['response'] == 1:
                    cur.execute('DELETE FROM accaunt_repost WHERE user_id = ? and post_id = ?', (user_id, post_id))
                    con.commit()
                else:
                    print('Ошибка удаления поста у', user_id, 'post_id', post_id)
            except KeyError:
                print(KeyError, j)

        print('Удаление завершено')

        cur.execute('SELECT * FROM accaunt_repost WHERE group_post_id = ?', (self.group_post_id,))
        rezult = cur.fetchall()
        print(rezult, rezult)

        if not rezult:
            cur.execute('DELETE FROM repost WHERE group_post_id = ?', (self.group_post_id,))
            con.commit()
            self.deleteLater()




















