import glob
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import *
from scipy.interpolate import interp1d

from algos.rfbucket import RfBucket
from algos.rfbunches import RfBunch


class SpsSimulator:

    def __init__(self, window):
        selector: QComboBox = window.ui.comboBox
        selector.currentTextChanged.connect(lambda c: print(c))
        self.cycle = selector.currentText()

        splitter: QSplitter = window.ui.splitter
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([100, 900])

        self.rfbucket = RfBucket()
        self.rfbunch = RfBunch()

        self.readLsaData()
        self.getSettings(self.cycle)

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

    def updateCycle(self, time=0):
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
