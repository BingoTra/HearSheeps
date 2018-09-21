import sqlite3 as sql
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QVBoxLayout, QLabel, QPlainTextEdit


class InfoFrozenForm(QWidget):
    def __init__(self, parent=None, acc=None):
        QWidget.__init__(self, parent)

        self.acc = acc
        self.parent = parent

        self.ui()
        self.loadInfo()

        self.btn_save.clicked.connect(self.save)
        self.btn_close.clicked.connect(lambda: self.parent.widgetsConductor(self, delete=True))

    def ui(self):
        self.btn_close = QPushButton('Закрыть')
        self.btn_save = QPushButton('Сохранить')
        self.plain_text = QPlainTextEdit()

        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self.btn_close, alignment=Qt.AlignRight)
        mainLayout.addWidget(self.plain_text)
        mainLayout.addWidget(self.btn_save)

    def save(self):
        con = sql.connect('db/db.sqlite3')

        with con:
            cur = con.cursor()
            cur.execute("UPDATE frozen_accaunt SET note=? WHERE user_id=?", (self.plain_text.toPlainText(), self.acc.user_id))
            con.commit()

    def loadInfo(self):
        con = sql.connect('db/db.sqlite3')

        with con:
            cur = con.cursor()
            cur.execute('SELECT note FROM frozen_accaunt WHERE user_id=?', (self.acc.user_id, ))
            row = cur.fetchone()

        if row:
            self.plain_text.setPlainText(row[0])

        else:
            with con:
                cur = con.cursor()
                cur.execute('INSERT INTO frozen_accaunt(user_id,note) VALUES(?, NULL)', (self.acc.user_id, ))
                con.commit()

