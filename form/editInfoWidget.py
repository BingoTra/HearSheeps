import json
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QVBoxLayout, QLabel, QCheckBox, QBoxLayout, QHBoxLayout

from hRequester import HRequester
from api import UrlAPI


class EditInfoWidget(QWidget):
    def __init__(self, parent=None, masAccaunt=None):
        QWidget.__init__(self, parent)

        self.chil = masAccaunt
        self.parent = parent

        self.ui()

        self.btn_save.clicked.connect(self.save)
        self.closeBtn.clicked.connect(lambda: self.parent.widgetsConductor(self, delete=True))

    def ui(self):
        self.lineName = QLineEdit()
        self.lineLastName = QLineEdit()
        self.lineBD = QLineEdit()
        self.lineVisibleBD = QCheckBox()
        self.lineCityId = QLineEdit()
        self.lineStatus = QLineEdit()
        self.BDLayout = QHBoxLayout()
        self.BDLayout.addWidget(self.lineBD)
        self.BDLayout.addWidget(self.lineVisibleBD)
        self.closeBtn = QPushButton('Закрыть')
        self.btn_save = QPushButton('Сохранить')

        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self.closeBtn, alignment=Qt.AlignRight)
        mainLayout.addWidget(QLabel('Имя'))
        mainLayout.addWidget(self.lineName)
        mainLayout.addWidget(QLabel('Фамилия'))
        mainLayout.addWidget(self.lineLastName)
        mainLayout.addWidget(QLabel('Дата рождения | Показывать дату рождения'))
        mainLayout.addLayout(self.BDLayout)
        mainLayout.addWidget(QLabel('Id города'))
        mainLayout.addWidget(self.lineCityId)
        mainLayout.addWidget(QLabel('Статус'))
        mainLayout.addWidget(self.lineStatus)
        mainLayout.addWidget(self.btn_save)


    def save(self):
        requester = HRequester()
        dic = {}

        if self.lineName.text() == '':
            pass
        else:
            dic.update(first_name=self.lineName.text())

        if self.lineLastName.text() == '':
            pass
        else:
            dic.update(last_name=self.lineLastName.text())

        if self.lineBD.text() == '':
            pass
        else:
            dic.update(bdate=self.lineBD.text())

        if self.lineCityId.text() == '':
            pass
        else:
            dic.update(city_id=self.lineCityId.text())

        if self.lineStatus.text() == '':
            pass
        else:
            dic.update(status=self.lineStatus.text())

        if self.lineVisibleBD.checkState() == 2:
            dic.update(bdate_visibility=1)
        else:
            dic.update(bdate_visibility=0)


        for acc in self.chil:
            getUrl = UrlAPI(acc.token)

            # Close coments under wall post and display walls record
            url1 = getUrl.account.setInfo(name='own_posts_default', value=0)
            url2 = getUrl.account.setInfo(name='no_wall_replies', value=1)

            requester(url1, acc.session)
            requester(url2, acc.session)
            requester(getUrl.account.saveProfileInfo(**dic), acc.session)


        response = requester.request()
        for r in response:
            j = json.loads(r[0].text)

            print(j)
