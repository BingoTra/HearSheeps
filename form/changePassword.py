import random
import re
import sqlite3 as sql

from bs4 import BeautifulSoup


class ChangePassword:
    def __init__(self, parent=None):

        self.parent = parent
        self.con = sql.connect('db/db.sqlite3')
        self.cur = self.con.cursor()
        self.chil = [item for item in self.parent.itemList if item.b.checkState() == 2 and item.frozen == 0]

        for acc in self.chil:
            self.changePrivacy(acc)


    def changePrivacy(self, acc):
        # Login
        responseLoginPage = acc.session.get('https://m.vk.com', proxies=acc.session.proxies)

        soup = BeautifulSoup(responseLoginPage.text)
        urlLogin = soup.find('form').get('action')

        acc.session.params.update(email=acc.login)
        acc.session.params.update({'pass': acc.password})

        responseLogin = acc.session.get(urlLogin, allow_redirects=False, proxies=acc.session.proxies)

        #params = ['mail_send', 'profile', 'audios', 'gifts', 'wall_send']

        #for param in params:
            #self.setting(param)

        self.changePassword(acc)

    def setting(self, acc, param):
        acc.session.params.clear()
        acc.session.params.update(_ref='settings')
        url = 'https://m.vk.com/settings?act=privacy&privacy_edit=' + param
        responsePrivacy = acc.session.get(url, proxies=acc.session.proxies)
        soup = BeautifulSoup(responsePrivacy.text)
        f = lambda: re.split('&', soup.find('form').get('action'))[1]
        hash = re.split('=', f())[1]

        acc.session.params.clear()
        acc.session.params.update(val='0', _tstat='settings%2C0%2C0%2C1020%2C23', _ref='settings')
        url = 'https://m.vk.com/settings?act=save_privacy&hash=' + hash + '&key=' + param
        responseSave = acc.session.get(url, allow_redirects=False, proxies=acc.session.proxies)

        if responseSave.headers['Location'] == ('/settings?act=privacy#pv_' + param):
            print('Успешно', param)
        else:
            print('Неуспешно', param)

    def changePassword(self,acc):
        new_password = self.getPassword()
        print(acc.password, 'Старый')
        print(new_password, 'Новый')

        acc.session.params.clear()
        acc.session.params.update(_ref='settings', _tstat='settings%2C0%2C0%2C615%2C22')
        url = 'https://m.vk.com/settings'
        responseSettings = acc.session.get(url, proxies=acc.session.proxies)

        url = 'https://m.vk.com/settings?act=change_password'
        responseSettingsChangePass = acc.session.get(url, proxies=acc.session.proxies)
        #print(responseSettingsChangePass.text)

        soup = BeautifulSoup(responseSettingsChangePass.text)
        hashSavePass = soup.find('input', class_='Input__native').get('value')

        acc.session.params.clear()
        acc.session.params.update(phash=hashSavePass,
                                  old_password=acc.password, new_password=new_password, confirm_password=new_password)
        url = 'https://login.vk.com/?act=changepass&role=pda&_origin=https://m.vk.com'
        responseSave = acc.session.get(url, allow_redirects=False, proxies=acc.session.proxies)

        acc.session.params.clear()
        urlConfirm = responseSave.headers['Location']
        responseConfirm = acc.session.get(urlConfirm, allow_redirects=False, proxies=acc.session.proxies)

        if responseConfirm.headers['Location'] == ('/settings?m=141'):

            with self.con:
                self.cur.execute("UPDATE accaunt SET pass=? WHERE user_id=?", (new_password, acc.user_id))
                self.con.commit()
            print('Успешно сменен пароль')
        else:
            print('Неуспешно сменен пароль')

        print(acc.user_id)


    def getPassword(self):
        pas = ''
        for x in range(16):  # Количество символов (16)
            pas = pas + random.choice(list('1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ'))

        return pas