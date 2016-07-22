import sys

import numpy as np
import math

from util import *

class MDSTraceData:

    def __init__(self, time_signal, time, radial_signal, radial_units, signal, units):

        self.time_signal = time_signal
        self.time = time
        self.radial_signal = radial_signal
        self.radial_units = radial_units
        self.signal = signal
        self.units = units

    def time_signal(self):
        return self.time_signal

    def time(self):
        return self.time

    def radial_signal(self):
        return self.radial_signal

    def radial_units(self):
        return self.radial_units

    def signal(self):
        return self.signal

    def units(self):
        return self.units