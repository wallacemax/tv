__author__ = 'maxwallace'

"""06/2015 WWallace wallace.max@gmail.com
Refactor of code.  Separation of concerns, dry, testability.  a variety of calculations, previously held in shelf, timing, etc.  extracted for testability
  ***The chi-square error we are running down is only here.***
"""

import numpy as np


class mpts_calculations:
    def find_gain(self, cl, ct, channels, vdac, mode=0):
        """finds the APD gain given the Vdac of the Digital to Analog converter"""
        if mode == 1:
            # linear mode
            coeff = cl
        else:
            # temperature mode
            coeff = ct

        vdac_zero = np.zeros([channels, 4])
        vdac_zero[:, 0] = vdac

        # (c0 - vdac) + c1 g + c2 g^2 + c3 g^3 = 0
        # Gain = exp(g)
        vc = coeff - vdac_zero
        # the coefficients in cl and ct are stored in reverse order compared to what
        # np.roots wants. flip them. (0, 1, 2, 3) --> (3, 2, 1, 0)
        vc = vc[:, ::-1]
        vroots = [np.roots(i) for i in vc]

        # this is some ugly code, since the np.roots function only works with 1d arrays
        # need to find the real roots, of which there should be only one
        possible_r = [np.real(np.extract(np.logical_and(np.imag(i) == 0, np.real(i) >= 0), i)) for i in vroots]
        possible_g = np.exp(possible_r)

        # gain should be close to 70 for the last four channels for phases 1 2 and 4, or all for phase 3
        # is a kluge, but there is no better way to filter when there are 3 viable real roots
        Gain = np.array([i[np.argmin(abs(i - 70))] for i in possible_g])

        return Gain
