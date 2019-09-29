from functools import partial

import numpy as np
from scipy.constants import c, e, m_p, pi
from scipy.integrate import cumtrapz, dblquad
from scipy.interpolate import interp1d
from scipy.optimize import brentq


class RfBucket:

    def __init__(self):

        # Constants
        # =========
        self.Z = 82.
        self.A = 207.
        self.Z = 1.
        self.A = 1.
        self.h = 4620.
        self.C = 6911.
        self.rho = 741.
        # self.gamma_t = 22.8
        self.conv = 2 * pi * self.h / self.C
        self.mass = self.A * m_p * c ** 2 / e

        # # Generate functions
        # # ==================
        # if self.lsa_data.beam_type == "LHC":
        #     self.time = np.linspace(0, 17000, 100)
        # elif self.lsa_data.beam_type == "LHCION":
        #     self.time = np.linspace(0, 6500, 100)
        # else:
        #     self.time = np.linspace(0, 9200, 200)
        #
        # self.momentum = self.lsa_data.f_momentum(self.time) * 1e9
        # self.gamma = np.sqrt(1 + (self.Z * self.momentum / self.mass) ** 2)
        # self.eta = self.gamma_t ** -2 - self.gamma ** -2
        # self.beta = np.sqrt(1 - self.gamma ** -2)
        #
        # self.voltage = self.lsa_data.f_voltage(self.time) * 1e6
        # self.bdot = self.lsa_data.f_BDot(self.time)
        # self.BA = self.lsa_data.f_BA(self.time)
        #
        # self.phi_s = np.arcsin(self.bdot * self.C * self.rho / self.voltage)

        # State values
        # =============
        self.V0 = None
        self.eta = None
        self.beta = None
        self.gamma = None
        self.phi_s = None
        self.phi_left = -pi
        self.phi_right = pi

    def update_parameters_at(self, momentum, pdot, gamma_tr, ratio=0, voltage=None, area=None):

        self.p0 = momentum * 1e9
        self.gamma = np.sqrt(1 + (self.Z * self.p0 / self.mass) ** 2)
        self.eta = gamma_tr ** -2 - self.gamma ** -2
        self.beta = np.sqrt(1 - self.gamma ** -2)

        self.V0 = voltage * 1e6
        self.pdot = pdot * 1e12
        self.ratio = ratio
        self.area = area

        self.dE = self.pdot * self.C / c
        self.phi_s = np.arcsin(self.dE / self.V0)
        self.phi_left, self.phi_right = self.get_separatrix_points(self.phi_s, self.ratio)

    # def update_parameters_at(self, t, r0=0):
    #
    #     self.p0 = self.lsa_data.f_momentum(t) * 1e9
    #     self.gamma0 = np.sqrt(1 + (self.Z * self.p0 / self.mass) ** 2)
    #     self.beta0 = np.sqrt(1 - self.gamma0 ** -2)
    #     self.eta0 = self.gamma_t ** -2 - self.gamma0 ** -2
    #
    #     self.V0 = self.lsa_data.f_voltage(t) * 1e6
    #     self.epsn_z0 = self.lsa_data.f_BA(t)
    #     self.BDot0 = self.lsa_data.f_BDot(t)
    #     self.r0 = r0
    #
    #     self.phi_s0 = np.arcsin(self.BDot0 * self.C * self.rho / self.V0)
    #
    #     # Prepare new voltage function and bucket limits!
    #     #         self.U_func = self.build_U_function(self.phi_s0, self.r0)
    #     self.phi_left, self.phi_right = self.get_separatrix_points(self.phi_s0, self.r0)

    def get_separatrix_points(self, phi_s, ratio):
        phi_right = self.get_phi_right(phi_s, ratio)
        phi_left = self.get_phi_left(phi_s, ratio)

        return phi_left, phi_right

    def get_phi_right(self, phi_s, ratio):
        phi = np.linspace(-1.1 * pi, 1.1 * pi, 100)
        zv = self._get_roots(partial(self.V, phi_s=phi_s, ratio=ratio), phi)

        try:
            ix = (zv >= phi_s).argmax()
            phi_right = zv[ix + 1]
        except ValueError as err:
            phi_right = pi
        except IndexError as err:
            phi_right = zv[ix]

        return phi_right

    def get_phi_left(self, phi_s, ratio):
        phi = np.linspace(-1.1 * pi, 1.1 * pi, 100)
        zu = self._get_roots(partial(self.U, phi_s=phi_s, ratio=ratio), phi)

        try:
            ix = (zu <= phi_s).argmax()
            phi_left = zu[ix + 0]
        except ValueError as err:
            phi_left = -pi
        except IndexError as err:
            phi_left = -pi

        return phi_left

    # Bucket functions
    # ================
    def V(self, phi, phi_s, ratio):
        harmonic_ratio = 4
        res = (np.sin(phi) - np.sin(phi_s)) + ratio * (np.sin(harmonic_ratio * (phi - phi_s)))

        return res

    def U(self, phi, phi_s, ratio):

        pp = np.linspace(-4 * pi, 4 * pi, 1000)

        v = self.V(pp, phi_s, ratio)
        u = np.cumsum(v) * np.diff(pp)[0]

        u = interp1d(pp, u)
        phi_right = self.get_phi_right(phi_s, ratio)

        res = u(phi) - u(phi_right)

        return res

    # Actual dp curve
    # ===============
    def dp(self, phi, norm=True):
        if norm:
            Vn = np.sqrt(2. / (np.abs(self.eta) * self.beta * c)) * np.sqrt(c * self.V0 / (2 * pi * self.p0 * self.h))
        else:
            Vn = 1

        # TODO: check this!
        phi_s = self.phi_s
        res = np.sqrt(np.abs(self.U(phi, phi_s, self.ratio))) * Vn

        return res

    def hamiltonian(self, delta, phi):

        if self.eta > 0:
            U = self.U(phi, self.phi_s, self.ratio) - self.U(self.phi_s, self.phi_s, self.ratio)
            sign = -1
        else:
            U = self.U(phi, self.phi_s, self.ratio)
            sign = +1

        res = sign * (1 / 2. * self.eta * self.beta * c * delta ** 2 - c * self.V0 / (2 * pi * self.p0 * self.h) * U)

        return res

    # Emittances etc.
    # ===============
    def get_emittance(self, V0):

        dE = self.pdot * self.C / c
        if V0 < dE:
            V0 = np.random.uniform(dE, 1e8)

        self.phi_s = float(np.arcsin(dE / V0))
        self.phi_left, self.phi_right = self.get_separatrix_points(self.phi_s, self.ratio)

        Vn = 2 / (self.eta * self.beta * c) * c * V0 / (2 * pi * self.p0 * self.h)
        res = self._emittance_cumtrapz(partial(self.dp, norm=False), self.phi_left, self.phi_right) \
              * np.sqrt(np.abs(Vn))
        #         print("phi_s: {:g}, V0: {:g}".format(self.phi_s0, float(V0)))

        return float(res)

    def get_voltage(self, epsn_z):
        g = lambda v: self.get_emittance(v) - epsn_z
        f = lambda v: np.abs(self.get_emittance(v) - epsn_z)

        lower = self.pdot * self.C / c + 1e-6
        V0 = brentq(g, lower, 1e8, maxiter=100000, xtol=1e-16)

        #         const = ({'type': 'ineq', 'fun': lambda x: x - self.BDot0 * self.C * self.rho})
        # #         def g(v):
        # #             eps = self.get_emittance(v)
        # #             diff = eps - epsn_z
        # # #             print(v, eps, diff)
        # #             return diff
        #         try:
        # #             V0 = brentq(g, 1e5, 1e8)
        # #             V0 = newton(f, 1e6, maxiter=1000, tol=1e-12)
        # #             method = 'Powell'
        #             res = minimize(f, 1, method='Nelder-Mead', tol=1e-6)
        # #             res = minimize(f, x0=[4e6], constraints=const)
        #             V0 = res.x

        #             print(res)
        #             BA = self.get_emittance(V0)
        #             print("BA: {:g}, BA_ext: {:g}, difference {:g}\n".format(BA, epsn_z, np.abs(BA-epsn_z)))
        #         except RuntimeError:
        # #             print(self.phi_s0)
        #             V0 = 0 # np.nan

        return V0

    # Computed functions
    # ==================
    def emittance_cycle(self):
        emittance = []
        for t in self.time:
            self.update_parameters_at(t)
            emittance.append(self.get_emittance(self.V0))

        return emittance

    def voltage_cycle(self):
        voltage = []
        for t in self.time:
            self.update_parameters_at(t)
            voltage.append(self.get_voltage(self.area))  # self.get_emittance(self.V0)))

        return voltage

    # Convenience functions
    # =====================
    def _get_roots(self, f, x):
        y = f(x)
        ix = np.where(np.abs(np.diff(np.sign(y))) == 2)[0]
        x0 = np.array([brentq(f, x[i], x[i + 1]) for i in ix])

        return x0

    def _quad2d(self, f, ylimits, xmin, xmax):
        Q, error = dblquad(lambda y, x: f(x, y), xmin, xmax,
                           lambda x: -ylimits(x), lambda x: ylimits(x))

        return Q

    def _emittance(self, f, x0, x1):
        Q, error = dblquad(lambda y, x: 1, x0, x1,
                           lambda x: 0, f)

        return Q * 2 * self.p0 / c * 1 / self.conv

    def _emittance_trapz(self, f, x0, x1):
        x = np.linspace(x0, x1, 100)
        y = f(x)
        Q = np.trapz(y, x)

        return Q * 2 * self.p0 / c * 1 / self.conv

    def _emittance_cumtrapz(self, f, x0, x1):
        x = np.linspace(x0, x1, 100)
        y = f(x)
        Q = cumtrapz(y, x, initial=0)[-1]

        return Q * 2 * self.p0 / c * 1 / self.conv
