import vk
import proxy
import getAccaunt
import MyData
import requests

p = proxy.Proxy().__class__
passList = getAccaunt.Accaunt.getPass()
loginList = getAccaunt.Accaunt.getLogin()



tik = 'https://oauth.vk.com/blank.html#access_token=8cacf2d3dd44a32b8b864b3626d9c2a811c805bea4051ea91e25b29a69aaa0d69daa202f61c9500343fb5&expires_in=86400&user_id=88230675'
response = requests.get('https://api.vk.com/method/wall.post', {'oauth':tik, 'message':'test', 'post_id':'wall-29573241_7735650', 'access_token':'8cacf2d3dd44a32b8b864b3626d9c2a811c805bea4051ea91e25b29a69aaa0d69daa202f61c9500343fb5'})
print(response.text)








