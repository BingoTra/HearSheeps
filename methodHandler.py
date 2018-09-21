import re

from bs4 import BeautifulSoup

import MyData
from api import API


class MethodHandler:

    def __init__(self, session, token):
        self.session = session
        self.api = API(session, token)

    def dialogHistory(self, user_id):
        '''Метод получения сообщенийвыбраного пользоателя'''
        messages = self.api.messages.getHistory(user_id=user_id)
        return messages

    @staticmethod
    def getAccessToken(session, login, password):

        s = session

        request = s.get(
            'https://oauth.vk.com/authorize?client_id=5490057&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=' + MyData.SCOPE + '&response_type=token&v=5.73',
            proxies=s.proxies)

        soup = BeautifulSoup(request.text)

        ip_h = soup.find('input', {'name': 'ip_h'}).get('value')
        lg_h = soup.find('input', {'name': 'lg_h'}).get('value')
        _origin = soup.find('input', {'name': '_origin'}).get('value')
        to = soup.find('input', {'name': 'to'}).get('value')
        expire = soup.find('input', {'name': 'expire'}).get('value')

        s.params.update(ip_h=ip_h, lg_h=lg_h, _origin=_origin, to=to, expire=expire, email=login)
        s.params.update({'pass': password})
        request2 = s.get('https://login.vk.com/?act=login&soft=1', proxies=s.proxies)

        soup = BeautifulSoup(request2.text)
        scripts = soup.findAll('script')

        location_href = ''

        for script in scripts:
            result = re.findall(r'.', str(script))

            i = 0
            while i in range(len(result)):

                if result[i] == '"':
                    string = ''
                    while True:
                        i += 1
                        if result[i] != '"':
                            string += result[i]
                        else:
                            break

                    endchar = re.findall(r'.......$', string)
                    if endchar[0] == 'https=1':
                        location_href = string

                i += 1
        try:
            request3 = s.get(location_href, proxies=s.proxies)
            finalyurl = request3.url
            print(finalyurl)
            location_href_char = re.findall(r'\w+', finalyurl)
            access_token = location_href_char[7]
            user_id = location_href_char[11]
            print(location_href_char)

            return access_token, user_id

        except:
            finalyurl = request2.url
            location_href_char = re.findall(r'\w+', finalyurl)
            access_token = location_href_char[7]
            user_id = location_href_char[11]
            print(request2.url)
            print(location_href_char, 'finalyurl')
            return access_token, user_id

    def saveProfileInfo(self, **dict):
        save = self.api.account.saveProfileInfo(**dict)
        print(save)

    def deleteWallPost(self, post_id):
        response = self.api.wall.delete(post_id=post_id)
        return response
