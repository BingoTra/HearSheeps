import base64
import io
import json
import re
import tempfile

import time
from PIL import Image
import requests
import sys
from hRequester import HRequester, HPostRequester
from PyQt5.QtWidgets import QApplication


class Captcha:

    def __init__(self):
        self.token = '9627bca19d9c7d222898cd68c9e6e085'
        self.urlPost = 'http://rucaptcha.com/in.php'
        self.urlGet = 'http://rucaptcha.com/res.php'

    def solve(self, session, captcha_url):
        captcha_id = 0
        captcha_result = ''
        captcha_url = re.sub('[\\\]', '', captcha_url)
        requester = HRequester()
        requester(captcha_url, session)
        response = requester.request()

        for r in response:

            with tempfile.NamedTemporaryFile(suffix='.jpg') as temp:
                temp.write(r[0].content)
                temp.flush()
                # Отправляем на рукапча изображение капчи
                captcha_id = self.postCaptcha(session, temp.name)
                break

        while True:
            captcha_result = self.getResult(session, captcha_id)

            if captcha_result == 'CAPCHA_NOT_READY':
                print('captcha_class', captcha_result)
                pass

            elif captcha_result == 'error':
                print('captcha_class', captcha_result)
                return 'error'

            else:
                print('captcha_class', captcha_result)
                return captcha_result

    def postCaptcha(self, session, captcha):
        postRequester = HPostRequester()
        session.headers.update(Accept='multipart/form-data')

        data = {
            'key':self.token,
            'regsense':'1',
            'json':'1'
        }

        postRequester(self.urlPost, session, None, data=data, files={'file': open(captcha, 'rb')})
        response = postRequester.request()

        for r in response:
            j = json.loads(r[0].text)
            print('captcha get id', j)

            if 'request' in j:
                return j['request']

    def getResult(self, session, captcha_id):
        requester = HRequester()

        dataGet = {
            'key':self.token,
            'action':'get',
            'id':captcha_id,
            'json':'1'
        }

        time.sleep(5)

        requester(self.urlGet, session, params=dataGet)
        requester(self.urlGet, session, )
        response = requester.request()

        for r in response:
            j = json.loads(r[0].text)

            if j['request'] == 'CAPCHA_NOT_READY':
                return 'CAPCHA_NOT_READY'

            elif j['status'] == 1:
                return j['request']

            elif j['request'] == 'ERROR_ZERO_BALANCE':
                print('Нет денег на балансе')
                return 'error'
            
            else:
                print(j)
                return 'error'