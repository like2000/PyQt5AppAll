import glob
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

from algos.rfbucket import RfBucket
from algos.rfbunches import RfBunch


class SpsSimulator:

    def __init__(self, window):
        self.cycle = "LHC"

        # self.mplwidget = self.createMplWidget()
        self.mpl_widget = window.ui.mpl_bunch
        self.rfbucket = RfBucket()
        self.rfbunch = RfBunch()

        self.readLsaData()
        self.getSettings(self.cycle)
        # self.plotSettings(self.cycle)
        # self.updateCycle(2000)
        # self.injectMplWidget(window, self.mplwidget)

    # def createMplWidget(self):
    #     widget = MatplotlibWidget(nrows=1, ncols=1, tight_layout=True)
    #
    #     widget.figure.clf()
    #     gs = gridspec.GridSpec(2, 2)
    #     widget.figure.add_subplot(gs[0, 0])
    #     widget.figure.add_subplot(gs[0, 1])
    #     widget.figure.add_subplot(gs[1, :])
    #     widget.axes = widget.figure.axes
    #
    #     return widget
    #
    # def injectMplWidget(self, window, widget):
    #     mplWidget = window.ui.mplwidget
    #     tabLayout = window.ui.tab1Layout
    #     tabLayout.replaceWidget(mplWidget, widget, Qt.FindChildrenRecursively)
    #
    #     button: QPushButton = window.ui.pb_area
    #     button.clicked.connect(self.computeBucketArea)
    #     button: QPushButton = window.ui.pb_voltage
    #     button.clicked.connect(self.computeVoltage)
    #     button: QPushButton = window.ui.pb_launch
    #     button.clicked.connect(self.runCycle)

    def readLsaData(self):
        self.data_cycles = dict()
        self.functions_cycles = dict()
        self.filelist = glob.glob("lsa/*.csv")
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

    def getSettings(self, cycle):
        self.data = self.data_cycles[cycle]
        self.functions = self.functions_cycles[cycle]
        self.cycle_length = self.data["MOMENTUM_time"].max()

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
