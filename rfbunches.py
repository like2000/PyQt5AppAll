from functools import partial

import numpy as np
from scipy.constants import c, pi
from scipy.optimize import minimize

from rfbucket import RfBucket


class RfBunch(RfBucket):

    def __init__(self):
        super().__init__()

    def get_bunch_edges(self, Hc):
        phi = np.linspace(-1.1 * pi, 2.1 * pi, 1000)
        zd = self._get_roots(partial(self.V_bunch, Hc=Hc), phi)

        if len(zd) < 2:
            return 0, 0

        ix = np.argmin((zd - self.phi_s) > 0)
        phi_left = zd[ix]

        ix = np.argmin((zd - self.phi_s) < 0)
        phi_right = zd[ix]

        return phi_left, phi_right

    # Bunch emittances
    # ================
    def V_bunch(self, phi, Hc):
        U = self.U(phi, self.phi_s, self.ratio) + 0 * self.U(self.phi_s, self.phi_s, self.ratio)

        res = Hc + c * self.V0 / (2 * pi * self.p0 * self.h) * U

        return res

    def dp_bunch(self, phi, Hc, norm=True):
        if norm:
            Vn = 2 / (self.eta * self.beta * c)  # * (c*self.V0/(2*pi*self.p0*self.h))

            if self.eta > 0:
                #                 V = self.V_bunch(phi, Hc) - self.V_bunch(self.phi_s0, 2*Hc)
                V = self.V_bunch(phi, 0) - self.V_bunch(self.phi_s, Hc)
            else:
                V = self.V_bunch(phi, Hc)
        else:
            Vn = 1 / (c * self.V0 / (2 * pi * self.p0 * self.h))
            V = self.V_bunch(phi, Hc)
        #         V = self.V_bunch(phi, Hc)

        #         res = (c*self.V0 / (2*pi*self.p0*self.h) * V) * Vn
        res = V * Vn
        res = np.sqrt(np.abs(res))

        return res

    def dp_bunch_for_emittance(self, phi, epsn_z, norm=True):
        Hc = self.get_contour_for_emittance(epsn_z)
        print(Hc)

        return self.dp_bunch(phi, Hc, norm)

    def get_emittance_bunch(self, Hc):

        phi_left, phi_right = self.get_bunch_edges(Hc)

        Vn = 2 / (self.eta * self.beta * c) * c * self.V0 / (2 * pi * self.p0 * self.h)
        res = self._emittance_cumtrapz(partial(self.dp_bunch, Hc=Hc, norm=False), phi_left, phi_right) \
              * np.sqrt(np.abs(Vn))

        return res

    def get_contour_for_emittance(self, epsn_z):
        root = lambda v: np.abs(self.get_emittance_bunch(v) - epsn_z)
        res = minimize(root, np.array([0]), method='Powell')

        return res.x
