import numpy as np
import math

def roundtohundred(x):
    return int(math.ceil(x / 100.0)) * 100

def find_idx_nearest_value(target, val):
    idx = (np.abs(target - val)).argmin()
    return idx

def reject_outliers(data, m=2.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / mdev if mdev else 0.
    return data[s < m]
