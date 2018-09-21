import sqlite3 as sql
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton


class ChangeReadinessWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.value = 0
        self.parent = parent

        self.ui()

        self.sld.valueChanged[int].connect(self.changeValue)
        self.btn_save.clicked.connect(self.save)

    def ui(self):
        self.color = QLabel()
        self.sld = QSlider(Qt.Horizontal)
        self.btn_save = QPushButton('Сохранить')

        m = QVBoxLayout(self)
        m.addWidget(self.color)
        m.addWidget(self.sld)
        m.addWidget(self.btn_save)

    def changeValue(self, value):
        r = 0
        g = 0
        b = 0
        m = int(255 / 25)
        self.value = value

        if value <= 25:
            r = 255 - m * value
            g = 255
            b = 0


        elif 25 < value <= 50:
            r = 0
            g = 255
            b = m * (value-25)

        elif 50 < value <= 75:
            r = 0
            g = 255 - m * (value-50)
            b = 255

        elif 75 < value <= 100:
            r = m * (value-75)
            g = 0
            b = 255

        if value == 99:
            r = 207
            g = 0
            b = 222

        hexColor = "#{:02x}{:02x}{:02x}".format(r, g, b)

        self.color.setStyleSheet("background-color:" + hexColor + ";")

    def save(self):
        self.chil = [item for item in self.parent.itemList if item.b.checkState() == 2 and item.frozen == 0]
        self.con = sql.connect('db/db.sqlite3')

        for acc in self.chil:

            with self.con:
                cur = self.con.cursor()
                cur.execute("UPDATE accaunt SET readiness=? WHERE user_id=?", (self.value, acc.user_id))
                self.con.commit()

        self.parent.loadAccaunts()




