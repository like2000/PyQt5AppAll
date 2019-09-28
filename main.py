import sys

from PyQt5 import QtWidgets

import mainwindow
from spssimulator import SpsSimulator


class ApplicationWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = ApplicationWindow()

    sps = SpsSimulator(win)

    sys.exit(app.exec_())
