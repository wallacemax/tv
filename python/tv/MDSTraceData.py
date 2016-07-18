import sys

import numpy as np
import math

from util import *


class MDSTraceData:

    def __init__(self, panelID, TDI, tree, name, units, scaling, label, x_label, y_label):

        self.server = 'NSTX'

        self.panelID = panelID
        self.TDI = TDI
        self.tree = tree
        self.name = name
        self.units = units
        self.scaling = scaling
        self.label = label
        self.x_label = x_label
        self.y_label = y_label

        self.data = Ellipsis

    def updateUnits(self, newUnits):
        self.units = newUnits

    def updateScaling(self, newscaling):
        self.scaling = newscaling

    def updateLabel(self, newlabel):
        self.label = newlabel

    def updatex_label(self, newxlabel):
        self.x_label = newxlabel

    def updatey_label(self, newylabel):
        self.y_label = newylabel

    def updateData(self, newData):
        self.data = newData

    def scaleData(self, newexponent):
        #this is going to be a mess
        pass

    def cutData(self, lastThomsonTime):
        # cut data before first Thomson value at t=0 and after last Thomson value - the rest of any other signal is unimportant
        #TODO: use last gradiant = 0 for final cut value instead of last Thomson timestamp

        for l in [self.data]:
            firstThomsonIndex = find_idx_nearest_value(l[0], 0)
            lastThomsonIndex = find_idx_nearest_value(l[0], lastThomsonTime) + 1
            for foo in [0, 4]:
                l[foo] = l[foo][firstThomsonIndex:lastThomsonIndex]

    def roundtohundred(self, x):
        return int(math.ceil(x / 100.0)) * 100

    def find_idx_nearest_value(self, target, val):
        idx = (np.abs(target - val)).argmin()
        return idx

    def reject_outliers(self, data, m=2.):
        d = np.abs(data - np.median(data))
        mdev = np.median(d)
        s = d / mdev if mdev else 0.
        return data[s < m]