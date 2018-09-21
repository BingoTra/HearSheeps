from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mouseDoubleClickEvent(self, QMouseEvent):
        self.clicked.emit()