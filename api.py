import MyData
import urllib
import json
from urllib import parse


class API(object):
    def __init__(self, session, token):
        self.session = session
        self.token = token

    def __getattr__(self, method_name):
        return Request(self.session, self.token, method_name)



class Request(object):

    def __init__(self, session, token, method_name):
        self.session = session
        self.token = token
        self.method_name = method_name

    def __getattr__(self, item):
        self.item = item
        return Request(self.session, self.token, self.method_name + '.' + self.item)

    def __call__(self, *args, **method_args):
        self.method_args = method_args

        if method_args == {}:
            url = MyData.METHOD + self.method_name + MyData.V_API + self.token
        elif method_args != {}:
            data = urllib.parse.urlencode(method_args)
            url = MyData.METHOD + self.method_name + '?' + data + MyData.V1_API + self.token

        if 'getUrl' in args:
            return url

        print('Параметры сессии', self.session.params, self.method_name)
        print(url)
        r = self.session.get(url, proxies=self.session.proxies)
        j = json.loads(r.text)
        return j


class UrlAPI(object):
    def __init__(self, token):
        self.token = token

    def __getattr__(self, method_name):
        return UrlRequest(self.token, method_name)



class UrlRequest(object):

    def __init__(self, token, method_name):
        self.token = token
        self.method_name = method_name

    def __getattr__(self, item):
        self.item = item
        return UrlRequest(self.token, self.method_name + '.' + self.item)

    def __call__(self, **method_args):
        self.method_args = method_args

        if method_args == {}:
            url = MyData.METHOD + self.method_name + MyData.V_API + self.token
        elif method_args != {}:
            data = urllib.parse.urlencode(method_args)
            url = MyData.METHOD + self.method_name + '?' + data + MyData.V1_API + self.token

        return url


