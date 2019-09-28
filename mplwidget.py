import matplotlib.pyplot as plt
import seaborn as sns
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

background_color = "whitesmoke"
# background_color = "gainsboro"

sns.set(context='notebook', style='darkgrid',  # palette='tab10',
        font='serif', font_scale=1, color_codes=True,
        rc={'axes.edgecolor': '0.4',
            'axes.linewidth': 1.5,
            'axes.facecolor': background_color,
            'figure.facecolor': background_color,
            'figure.edgecolor': 'red',
            'figure.subplot.top': 0.90,  # the top of the subplots of the figure
            'figure.subplot.left': 0.15,  # the left side of the subplots of the figure
            'figure.subplot.right': 0.90,  # the right side of the subplots of the figure
            'figure.subplot.bottom': 0.10,  # the bottom of the subplots of the figure
            'figure.subplot.wspace': 0.20,  # the amount of width reserved for blank space between subplots,
            'figure.subplot.hspace': 0.20,
            'grid.color': '0.8',
            # 'font.family': 'sans-serif',
            # 'font.sans-serif': 'helvetica',
            'lines.linewidth': 1.5,
            'lines.markersize': 4,
            'lines.markeredgewidth': 0.1,
            'savefig.transparent': False,
            })


class MatplotlibCanvas(Canvas):
    def __init__(self, parent=None, **kwargs):
        self.figure, self.axes = plt.subplots(**kwargs)

        # self.figure.suptitle(title)
        # self.axes = self.figure.add_subplot(111)
        # self.axes.set_title(title)
        # self.axes.set_xlabel(xlabel)
        # self.axes.set_ylabel(ylabel)
        # if xscale is not None:
        #     self.axes.set_xscale(xscale)
        # if yscale is not None:
        #     self.axes.set_yscale(yscale)
        # if xlim is not None:
        #     self.axes.set_xlim(*xlim)
        # if ylim is not None:
        #     self.axes.set_ylim(*ylim)

        super(MatplotlibCanvas, self).__init__(self.figure)
        self.setParent(parent)
        super(MatplotlibCanvas, self).setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        super(MatplotlibCanvas, self).updateGeometry()

    def sizeHint(self):
        try:
            return QSize(*self.get_width_height())
        except ValueError:
            pass

    def minimumSizeHint(self):
        try:
            return QSize(10, 10)
        except ValueError:
            pass


class MatplotlibWidget(QGraphicsView):

    def __init__(self, parent=None, nav_bar=True, **kwargs):
        # QWidget.__init__(self, parent)  # Inherit from QWidget
        super(MatplotlibWidget, self).__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.canvas = MatplotlibCanvas(parent=parent, **kwargs)
        layout.addWidget(self.canvas)
        if nav_bar:
            self.navBar = NavigationToolbar(self.canvas, self)
            layout.addWidget(self.navBar)

        self.figure = self.canvas.figure
        self.axes = self.canvas.axes
