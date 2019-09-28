import typing

from PyQt5 import QtGui
from PyQt5 import QtWidgets


class SButton(QtWidgets.QPushButton):

    def __init__(self, parent=None):
        super(SButton, self).__init__(parent)

        self.setStyle()

    # Just for PyCharm
    # print(resources)

    # def paintEvent(self, pe):
    #     opt = QtGui.Qst()
    #     opt.init(self)
    #     p = QtGui.QPainter(self)
    #     s = self.style()
    #     s.drawPrimitive(QtWidgets.QStyle.PE_Widget, opt, p, self)

    def setStyle(self):
        self.setCheckable(True)
        self.setText("Inactive")
        self.setObjectName("inactive")
        # with open(":res/button_stylesheet.qss", "r") as fh:
        # pass
        # print(fh)
        # self.setStyleSheet(fh.read())

    # def connectSignalsSlots(self):
    #     self.toggled.connect(self.toggle)

    def toggle(self, checked):
        if checked:
            glow = QtWidgets.QGraphicsDropShadowEffect()
            glow.setOffset(0, 0)
            glow.setBlurRadius(10)
            glow.setColor(QtGui.QColor("green"))
            self.setGraphicsEffect(glow)
            self.setText(self.text_on)
            self.setObjectName("enabled")
            self.setStyle(self.style())
        else:
            self.setGraphicsEffect(None)
            self.setText(self.text_off)
            self.setObjectName("disabled")
            self.setStyle(self.style())
