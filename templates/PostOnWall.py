import vk
from MyData import MyData

session = vk.AuthSession(app_id=MyData.APP_ID, user_login=MyData.MY_LOGIN, user_password=MyData.MY_PASS, scope='wall' )
vkapi = vk.API(session)

MESSAGE = 'Hello world'
vkapi.wall.post(message=MESSAGE)