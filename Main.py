import vk
import proxy
import getAccaunt
import MyData
import requests

p = proxy.Proxy().__class__
passList = getAccaunt.Accaunt.getPass()
loginList = getAccaunt.Accaunt.getLogin()



response = requests.get('https://oauth.vk.com/authorize?client_id=6290932&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends&response_type=token&v=5.52')
print(response.text)








