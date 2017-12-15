import re,requests,os


class Proxy:

    proxiesUsedList = []

    # Получаем поочередно прокси из файла, проверяем их и если нашелся рабочий, то возвращаем его. Если нет рабочего прокси, то хз что произойдет
    @staticmethod
    def getProxy (proxiesUsedList=proxiesUsedList):

        with open('./files/proxy.txt', 'r') as proxyFile:
            for line in proxyFile:
                chekProxy = re.sub(r'\n', '', line)

                try:
                    response = requests.get('http://ident.me/', proxies={'http':chekProxy} , timeout=(3)).status_code
                except requests.exceptions.ConnectTimeout:
                    continue
                except requests.exceptions.ReadTimeout:
                    continue
                except requests.exceptions.ProxyError:
                    continue

                if response == 200:
                    if chekProxy not in proxiesUsedList:
                        proxy = chekProxy             #рабочий прокси
                        break

        proxiesUsedList.append(proxy)
        return proxy

