import sys

import numpy as np
import math

from util import *


class MDSTrace:

    def __init__(self, panelID, TDI, tree, name, units, scaling, label, x_label, y_label):

        self.server = 'NSTX'
        self.prop = {'panelID': panelID, 'tdi': TDI, 'tree': tree, 'name': name, 'units': units, 'scaling': scaling,
                     'label': label, 'x_label': x_label, 'y_label': y_label}

        self.data = ''

    def __getitem__(self, item):
        if item == 'data':
            ret = self.data
        else:
            ret = self.prop[item]
        return ret

    def __setitem__(self, key, value):
        if key == 'data':
            self.data = value
        else:
            self.prop[key] = value

    def reject_outliers(self, data, m=2.):
        d = np.abs(data - np.median(data))
        mdev = np.median(d)
        s = d / mdev if mdev else 0.
        return data[s < m]