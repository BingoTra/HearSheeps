import vk,requests
from MyData import MyData


p1 = 'https://api.vk.com/method/auth.confirm'

response = requests.get(p1,
                        {'first_name':'Данила', 'last_name':'Мордасов', 'birthday':'10.1.1996', 'client_id':'6290932',
                        'client_secret':'Mc44qJxW33fHMUHRTMzp', 'phone':'+79167046981', 'password':'Zwer1996',
                        'test_mode':'0','sex=':'2', 'code':'99247', 'sid':'a1312029ed49ee5e9af5d8238e8d7f7a '},
                        proxies={'http':'178.213.248.110:8080'})
print(response.text)