import re


class Accaunt:

   # Создаем loginList(массив) и в него поочередно записываем логины
   @staticmethod
   def getLogin ():
      loginList = []
      filepath = './files/accaunts.txt'
      with open(filepath, 'r') as fileAccounts:
          for line in fileAccounts:
             splitsLine = re.split(r':', line)
             login = splitsLine[0]
             loginList.append(login)

      fileAccounts.close()
      return loginList


   # Создаем passList(массив) и в него поочередно записываем логины
   @staticmethod
   def getPass():
       passwordList = []
       filepath = './files/accaunts.txt'
       with open(filepath, 'r') as fileAccounts:
           for line in fileAccounts:
               splitsLine = re.split(r':', line)
               password = re.sub(r'\n', '', splitsLine[1])
               passwordList.append(password)

       fileAccounts.close()
       return passwordList
