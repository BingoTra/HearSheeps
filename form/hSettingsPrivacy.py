import json
import re
from api import UrlAPI

from bs4 import BeautifulSoup

from hRequester import HRequester
import sqlite3 as sql



class SettingsPrivacy:
    def __init__(self, parent=None):
        self.parent = parent
        self.chil = [item for item in self.parent.itemList if item.b.checkState() == 2 and item.frozen == 0]

        for acc in self.chil:
            self.settingPrivacy(acc)

    def settingPrivacy(self, acc):
        requester = HRequester()
        con = sql.connect('db/db.sqlite3')
        cur = con.cursor()

        #Login
        responseLoginPage = acc.session.get('https://m.vk.com', proxies=acc.session.proxies)

        soup = BeautifulSoup(responseLoginPage.text)
        urlLogin = soup.find('form').get('action')

        acc.session.params.update(email=acc.login)
        acc.session.params.update({'pass': acc.password})

        responseLogin = acc.session.get(urlLogin, allow_redirects=False, proxies=acc.session.proxies)

        params = ['mail_send', 'profile', 'audios', 'gifts', 'wall_send']

        for param in params:
            self.setting(acc, param)

        # Close coments under wall post and display walls record
        getUrl = UrlAPI(acc.token)
        url1 = getUrl.account.setInfo(name='own_posts_default', value=0)
        url2 = getUrl.account.setInfo(name='no_wall_replies', value=1)
        requester(url1, acc.session)
        requester(url2, acc.session)
        response = requester.request()
        for r in response:
            j = json.loads(r[0].text)
            if j['response'] == 1:
                print(
                    'Успешно включено отображение записей на стене пользователя и закрыты коментарии на стене')

        con.close()

    def setting(self, acc, param):
        acc.session.params.clear()
        acc.session.params.update(_ref='settings')
        url = 'https://m.vk.com/settings?act=privacy&privacy_edit='+param
        responsePrivacy = acc.session.get(url, proxies=acc.session.proxies)
        soup = BeautifulSoup(responsePrivacy.text)
        f = lambda: re.split('&', soup.find('form').get('action'))[1]
        hash = re.split('=', f())[1]

        acc.session.params.clear()

        if param == 'wall_send':
            acc.session.params.update(val='3', _tstat='settings%2C0%2C0%2C1020%2C23', _ref='settings')
        else:
            acc.session.params.update(val='0', _tstat='settings%2C0%2C0%2C1020%2C23', _ref='settings')

        url = 'https://m.vk.com/settings?act=save_privacy&hash=' + hash + '&key=' + param
        responseSave = acc.session.get(url, allow_redirects=False, proxies=acc.session.proxies)

        if responseSave.headers['Location'] == ('/settings?act=privacy#pv_' + param):
            print('Успешно', param)
        else:
            print('Неуспешно', param)


