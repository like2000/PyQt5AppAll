from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class LedButton(QWidget):
    def __init__(self, parent=None):
        super(LedButton, self).__init__(parent)

        self.initLayout()

    def initLayout(self):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignVCenter)
        layout.setContentsMargins(5, 0, 5, 0)
        self.setLayout(layout)

        self.button = QPushButton()
        self.button.setText("Enable")
        self.button.setMinimumWidth(60)

        self.led = QPushButton()
        self.led.setFixedWidth(20)
        self.led.setFixedHeight(20)

        layout.addWidget(self.button)
        layout.addWidget(self.led)

        self.toggled = False
        self.button.clicked.connect(self.toggle)

    def toggle(self):
        if self.toggled is False:
            self.toggled = True
        elif self.toggled is True:
            self.toggled = False

    @property
    def toggled(self):
        return self._toggled

    @toggled.setter
    def toggled(self, value):
        if value is True:
            color = "green"

        elif value is False:
            color = "red"

        self.led.setStyleSheet("""
        background: qradialgradient(cx:0.1, cy:0.1, radius: 0.75
                fx:0.25, fy:0.25, stop:0 white, stop:1 dark{color});
        border-color: dark{color};
        border-style: solid;
        border-radius: 10;
        border-width: 0px;
        """.format(color=color))
        glow = QGraphicsDropShadowEffect()
        glow.setOffset(0, 0)
        glow.setBlurRadius(10)
        glow.setColor(QColor("{:s}".format(color)))
        self.led.setGraphicsEffect(glow)

        self._toggled = value
