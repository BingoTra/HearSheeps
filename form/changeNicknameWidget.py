import sqlite3 as sql
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QLineEdit


class ChangeNicknameWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.parent = parent

        self.ui()

        self.btn_save.clicked.connect(self.save)
        self.btn_close.clicked.connect(lambda: self.parent.widgetsConductor(self, delete=True))

    def ui(self):
        self.lineEdit_nickname = QLineEdit()
        self.btn_close = QPushButton('Закрыть')
        self.btn_save = QPushButton('Сохранить')

        m = QVBoxLayout(self)
        m.addWidget(self.lineEdit_nickname)
        m.addWidget(self.btn_save)
        m.addWidget(self.btn_close, alignment=Qt.AlignRight)


    def save(self):
        self.chil = [item for item in self.parent.itemList if item.b.checkState() == 2 and item.frozen == 0]
        self.con = sql.connect('db/db.sqlite3')

        for acc in self.chil:

            with self.con:
                cur = self.con.cursor()
                cur.execute("UPDATE accaunt SET nickname=? WHERE user_id=?", (self.lineEdit_nickname.text(), acc.user_id))
                self.con.commit()

        self.con.close()
        self.parent.loadAccaunts()




