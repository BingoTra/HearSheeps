from PyQt5.QtCore import Qt
from api import API
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QFrame, QTabWidget, QGroupBox

class AddPost(QWidget):

    def __init__(self, parent=None, session=None, token=None):
        super().__init__(parent, Qt.Window)
        self.ui()

        self.api = API(session, token)

        self.btn_addRepost.clicked.connect(self.repost)

        self.show()

    def ui(self):
        #Repost tab
        repostLayout = QVBoxLayout()
        self.lineRepost = QLineEdit()
        self.btn_addRepost = QPushButton('Добавить')
        repostLayout.addWidget(self.lineRepost)
        repostLayout.addWidget(self.btn_addRepost)
        frame = QFrame()
        frame.setLayout(repostLayout)

        #Record tab
        recordLayout = QVBoxLayout()
        frame1 = QFrame()
        frame1.setLayout(recordLayout)

        #Tabs
        tab = QTabWidget()
        tab.addTab(frame, "Репост")  # вкладки
        tab.addTab(frame1, "Запись")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(tab)

        self.setLayout(mainLayout)

    def repost(self):

        repost = self.api.wall.repost(object=self.lineRepost.text())

        try:
            if repost['response']['success'] == 1:
                print('Успешно')
        except:
            print('Ошибка')
