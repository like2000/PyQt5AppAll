import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from scipy.constants import pi

from mplwidget import MatplotlibWidget
from spssimulator import SpsSimulator


class RfBucket:

    def __init__(self, window, simulator: SpsSimulator = None):
        self.simulator = simulator
        self.cycle = simulator.cycle
        self.rfbunch = simulator.rfbunch

        self.mpl_widget = window.ui.mpl_bunch
        self.figure = self.mpl_widget.figure
        try:
            self.axes = self.mpl_widget.axes.flatten()
        except AttributeError:
            self.axes = self.mpl_widget.axes

        self.initTab(window)
        # self.plotSettings(self.simulator.cycle)

    def createMplWidget(self):
        widget = MatplotlibWidget(nrows=1, ncols=1, tight_layout=True)

        # widget.figure.clf()
        # gs = gridspec.GridSpec(2, 2)
        # widget.figure.add_subplot(gs[0, 0])
        # widget.figure.add_subplot(gs[0, 1])
        # widget.figure.add_subplot(gs[1, :])
        # widget.axes = widget.figure.axes

        return widget

    def initTab(self, window):
        # mplWidget = window.ui.mplwidget
        # tabLayout = window.ui.tab_1.layout()
        # tabLayout.replaceWidget(mplWidget, self.mpl_widget, Qt.FindChildrenRecursively)

        button = window.ui.pb_compute
        button.clicked.connect(self.plotBunch)

        # slider: QSlider = window.ui.bucketSlider
        # slider.setMaximum(self.simulator.cycle_length)
        # slider.setSingleStep(50)
        # slider.setPageStep(50)
        # slider.valueChanged.connect(self.plotCycle)

    def plotSettings(self, cycle):
        data = self.simulator.data_cycles[cycle]

        self.axes[0].plot(data['MOMENTUM_time'], data['MOMENTUM_value'])
        self.axes[1].plot(data['VOLTAGE_time'], data['VOLTAGE_value'])

        self.lines = [ax.axvline(0, c='k') for ax in self.axes]

    def plotCycle(self, time):
        self.simulator.updateCycle(time)

        [l.set_xdata(time) for l in self.lines]

        n_points = 500
        dd, pp = np.linspace(-1.5 * pi, 2.5 * pi, n_points), np.linspace(-5e-3, 5e-3, n_points)
        DD, PP = np.meshgrid(dd, pp)

        HH = self.rfbucket.hamiltonian(PP, DD)
        # HH = np.sqrt(np.abs(HH))
        self.axes[2].cla()
        self.axes[2].contourf(DD, PP, HH, levels=30, cmap='cividis', alpha=0.7)
        self.axes[2].contour(DD, PP, HH, levels=[0], colors=['darkred'])
        self.axes[2].plot(dd, +self.rfbucket.dp(dd), c='orange')
        self.axes[2].plot(dd, -self.rfbucket.dp(dd), c='orange')
        self.axes[2].set_xlim(-pi, 2.5 * pi)
        self.axes[2].set_ylim(-5e-3, 5e-3)
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def runCycle(self):
        step = 10
        counter = 1400

        while counter < 2000:
            counter += step
            self.plotCycle(counter)

    def plotBunch(self, epsn_z):
        self.simulator.updateCycle(10000)
        figure = self.mpl_widget.figure
        axes = self.mpl_widget.axes
        epsn_z = 0.2

        n_points = 500
        dd, pp = np.linspace(-1.5 * pi, 2.5 * pi, n_points), np.linspace(-5e-3, 5e-3, n_points)
        DD, PP = np.meshgrid(dd, pp)

        QApplication.setOverrideCursor(Qt.WaitCursor)

        EE = self.rfbunch.get_contour_for_emittance(epsn_z=epsn_z)
        HH = self.rfbunch.hamiltonian(PP, DD)
        # HH = np.sqrt(np.abs(HH))
        axes.cla()
        axes.contourf(DD, PP, HH, levels=30, cmap='cividis', alpha=0.7)
        axes.contour(DD, PP, HH, levels=[0], colors=['darkred'])
        axes.contour(DD, PP, HH, levels=[EE], colors=['darkblue'])
        # axes.plot(dd, +self.rfbunch.dp(dd), c='orange')
        # axes.plot(dd, -self.rfbunch.dp(dd), c='orange')
        # axes.plot(dd, +self.rfbunch.dp_bunch_for_emittance(dd, epsn_z=epsn_z), c='purple')
        # axes.plot(dd, -self.rfbunch.dp_bunch_for_emittance(dd, epsn_z=epsn_z), c='purple')
        axes.set_xlim(-pi, 2.5 * pi)
        axes.set_ylim(-5e-3, 5e-3)
        figure.canvas.draw()
        figure.canvas.flush_events()

        QApplication.restoreOverrideCursor()
