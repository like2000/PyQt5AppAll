import glob
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from matplotlib import gridspec
from scipy.constants import pi
from scipy.interpolate import interp1d

from mplwidget import MatplotlibWidget
from rfbucket import RfBucket
from rfbunches import RfBunch


class SpsSimulator:

    def __init__(self, window):
        self.cycle = "LHC"

        self.mplwidget = self.createMplWidget()
        self.rfbucket = RfBucket()

        self.rfbunch = RfBunch()
        self.mplBunch = window.ui.mpl_bunch
        button = window.ui.pb_compute
        button.clicked.connect(self.plotBunch)

        self.readLsaData()
        self.plotSettings(self.cycle)
        # self.updateCycle(2000)
        self.injectMplWidget(window, self.mplwidget)

        slider: QSlider = window.ui.bucketSlider
        slider.setMaximum(self.cycle_length)
        slider.setSingleStep(50)
        slider.setPageStep(50)
        slider.valueChanged.connect(self.plotCycle)

    def createMplWidget(self):
        widget = MatplotlibWidget(nrows=1, ncols=1, tight_layout=True)

        widget.figure.clf()
        gs = gridspec.GridSpec(2, 2)
        widget.figure.add_subplot(gs[0, 0])
        widget.figure.add_subplot(gs[0, 1])
        widget.figure.add_subplot(gs[1, :])
        widget.axes = widget.figure.axes

        return widget

    def injectMplWidget(self, window, widget):
        mplWidget = window.ui.mplwidget
        tabLayout = window.ui.tab1Layout
        tabLayout.replaceWidget(mplWidget, widget, Qt.FindChildrenRecursively)

        button: QPushButton = window.ui.pb_area
        button.clicked.connect(self.computeBucketArea)
        button: QPushButton = window.ui.pb_voltage
        button.clicked.connect(self.computeVoltage)
        button: QPushButton = window.ui.pb_launch
        button.clicked.connect(self.runCycle)

    def readLsaData(self):
        self.data_cycles = dict()
        self.functions_cycles = dict()
        self.filelist = glob.glob("LSA/*.csv")
        self.cycles = set([re.split('/|\.|_', fl)[1] for fl in self.filelist])

        for cyc in self.cycles:
            self.data_cycles[cyc] = pd.DataFrame()
            self.functions_cycles[cyc] = dict()

        for fl in self.filelist:
            try:
                _, cycle, parameter, _ = re.split('/|\.|_', fl)
                dd = np.genfromtxt(fl, delimiter=',', skip_header=2)
                da = pd.DataFrame(data=dd, columns=[parameter + '_time', parameter + '_value'])
                self.data_cycles[cycle] = self.data_cycles[cycle].append(da, ignore_index=True, sort=False)

                ff = interp1d(*dd.T)
                self.functions_cycles[cycle][parameter] = ff

                if parameter == 'MOMENTUM':
                    tt, vv = dd.T
                    aa, bb = tt, np.gradient(vv, tt)
                    da = pd.DataFrame(data=np.array([aa, bb]).T, columns=['PDOT_time', 'PDOT_value'])
                    self.data_cycles[cycle] = self.data_cycles[cycle].append(da, ignore_index=True, sort=False)

                    ff = interp1d(aa, bb)
                    self.functions_cycles[cycle]["PDOT"] = ff
            except ValueError:
                raise
                # dd = np.genfromtxt(fl, delimiter=',', skip_header=2, skip_footer=2)

    def plotSettings(self, cycle):

        data = self.data_cycles[cycle]
        self.functions = self.functions_cycles[cycle]

        self.figure = self.mplwidget.figure
        try:
            self.axes = self.mplwidget.axes.flatten()
        except AttributeError:
            self.axes = self.mplwidget.axes

        self.cycle_length = data["MOMENTUM_time"].max()

        self.axes[0].plot(data['MOMENTUM_time'], data['MOMENTUM_value'])
        self.axes[1].plot(data['VOLTAGE_time'], data['VOLTAGE_value'])
        # self.axes[1].plot(data['PDOT_time'], data['PDOT_value'])
        # self.axes[2].plot(data['BA_time'], data['BA_value'])

        self.lines = [ax.axvline(0, c='k') for ax in self.axes]

    def updateCycle(self, time):
        momentum = self.functions['MOMENTUM'](time)
        voltage = self.functions['VOLTAGE'](time)
        ratio = 0  # self.functions['RATIO'](time)
        pdot = self.functions['PDOT'](time)
        area = self.functions['BA'](time)
        gamma_tr = 18.  # 23.2
        self.rfbucket.update_parameters_at(momentum=momentum, pdot=pdot, gamma_tr=gamma_tr, voltage=voltage, area=area,
                                           ratio=ratio)
        self.rfbunch.update_parameters_at(momentum=momentum, pdot=pdot, gamma_tr=gamma_tr, voltage=voltage, area=area,
                                          ratio=ratio)

    def plotCycle(self, time):
        self.updateCycle(time)

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

    def computeBucketArea(self):

        tt = range(0, 9000, 20)
        ba = []
        for t in tt:
            self.updateCycle(t)
            ba.append(self.rfbucket.get_emittance(self.rfbucket.V0))

        fig, ax = plt.subplots(1, 1, tight_layout=True)
        ax.plot(tt, ba)
        ax.plot(tt, self.functions['BA'](tt))
        ax.set_xlabel("Time [ms]")
        ax.set_ylabel("Bucket area [eVs]")
        fig.show()

    def computeVoltage(self):
        tt = range(0, 9000, 50)
        V0 = []
        for t in tt:
            self.updateCycle(t)
            V0.append(self.rfbucket.get_voltage(self.rfbucket.area) * 1e-6)

        fig, ax = plt.subplots(1, 1, tight_layout=True)
        ax.plot(tt, V0)
        ax.plot(tt, self.functions['VOLTAGE'](tt))
        ax.set_xlabel("Time [ms]")
        ax.set_ylabel("Voltage [V]")
        fig.show()

    def plotBunch(self, epsn_z):
        self.updateCycle(10000)
        figure = self.mplBunch.figure
        axes = self.mplBunch.axes
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
