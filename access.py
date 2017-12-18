import requests
import MyData
from bs4 import BeautifulSoup
import getAccaunt

myData = MyData.MyData
acc = getAccaunt.Accaunt

login = acc.getLogin()
password = acc.getPass()

session = requests.session()

# Beautiful Soup
with session.get(myData.OAUTH, headers=myData.USERAGENT) as get:
    soup = BeautifulSoup(get.text, 'lxml')
    ip_h = soup.find('div', {'class':'oauth_form_login'}).find('input',{'name':'ip_h'}).get('value').__str__()
    lg_h = soup.find('div', {'class':'oauth_form_login'}).find('input',{'name':'lg_h'}).get('value').__str__()
    origin = soup.find('div', {'class':'oauth_form_login'}).find('input',{'name':'_origin'}).get('value').__str__()
    to = soup.find('div', {'class':'oauth_form_login'}).find('input',{'name':'to'}).get('value').__str__()
    expire = soup.find('div', {'class':'oauth_form_login'}).find('input',{'id':'expire'}).get('value').__str__()

auth = 'ip_h='+ip_h+'&lg_h='+lg_h+'&_origin=https%3A%2F%2Foauth.vk.com&to='+to+'&expire='+expire+'&email=danil.mordasow@mail.ru&pass=xervzlomal123'

contentType = 'Content-Type: application/x-www-form-urlencoded Content-Length: '+str(auth.__len__())

print(auth)
print(auth.__len__())
post = session.post('https://login.vk.com/?act=login&soft=1&utf8=1', headers=myData.USERAGENT, {'Content-Type: application/x-www-form-urlencoded Content-Length: 359 ip_h=888abde36df74058ed&lg_h=afd775a0c4a8ec346f&_origin=https%3A%2F%2Foauth.vk.com&to=aHR0cHM6Ly9vYXV0aC52ay5jb20vYXV0aG9yaXplP2NsaWVudF9pZD02MjkwOTMyJnJlZGlyZWN0X3VyaT1odHRwcyUzQSUyRiUyRm9hdXRoLnZrLmNvbSUyRmJsYW5rLmh0bWwmcmVzcG9uc2VfdHlwZT10b2tlbiZzY29wZT00MDg3MzQmdj01LjY5JnN0YXRlPSZkaXNwbGF5PXBhZ2U-&expire=0&email=danil.mordasow@mail.ru&pass=xervzlomal123'.encode()})
print(post.text)