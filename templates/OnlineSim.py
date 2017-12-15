import requests


response = requests.get('https://onlinesim.ru/api/getServiceList.php?apikey=9546fbd6857643922a3648d13d53ffb5')
print(response.text)

#Незакончено