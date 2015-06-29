"""06/2015 WWallace wallace.max@gmail.com
Refactor of code.  Separation of concerns, dry, testability.
"""

import numpy as np


class Timing:
    def __init__(self, max_phase, data):

        self.max_phase = max_phase
        times = data.find_times(max_phase)
        if type(times) == tuple:
            # time indices
            self.times, self.index_laser1, self.index_laser2, self.index_dark, self.ip_start, self.ip_end, self.int_sph \
                = times
            self.status = 1
            self.index_laser = np.union1d(self.index_laser1, self.index_laser2)
            self.index_before = np.where(self.times <= -0.25)[0]
            self.ip_extension = 0  # TEMPORARY
            # find the time indices when lasers fire from plasma current start to end
            self.index_laser_cut = np.extract(
                np.logical_and(self.ip_start <= self.index_laser, self.index_laser <= self.ip_end + self.ip_extension),
                self.index_laser)
            self.index_laser1_cut = np.extract(np.logical_and(self.ip_start <= self.index_laser1,
                                                              self.index_laser1 <= self.ip_end + self.ip_extension),
                                               self.index_laser1)
            self.index_laser2_cut = np.extract(np.logical_and(self.ip_start <= self.index_laser2,
                                                              self.index_laser2 <= self.ip_end + self.ip_extension),
                                               self.index_laser2)

            self.laser_id = np.zeros_like(self.index_laser_cut)
            ind_laser2 = np.searchsorted(self.index_laser_cut, self.index_laser2_cut)
            self.laser_id[ind_laser2] = 1

            # date
            self.year = data.get_year()

            # shutters
            self.shutters = data.get_shutters()

        else:
            self.status = 0

    def __getitem__(self, index):
        return self.times[index]

    def __repr__(self):
        s = "TIMES: " + str(self.times[self.ip_start]) + "s to " + str(
            self.times[self.ip_end + self.ip_extension]) + "s with current cut at " + str(
            self.times[self.ip_end]) + "s\n"
        s += str(len(self.index_laser1_cut)) + " laser 1 pulses and " + str(
            len(self.index_laser2_cut)) + " laser 2 pulses"
        return s

    def laser_energy_scale(self, calib):
        """calculates the laser energy scaling factors"""
        e_dark_avg = np.mean(self.int_sph[self.index_dark])

        e_laser1, e_laser2 = calib["elsrsp_ram_avg"]
        laser1_times = self.times[self.index_laser1_cut]
        laser2_times = self.times[self.index_laser2_cut]

        laser1_energy = self.int_sph[self.index_laser1_cut]
        laser2_energy = self.int_sph[self.index_laser2_cut]

        laser1_factor = (laser1_energy - e_dark_avg) / e_laser1
        laser2_factor = (laser2_energy - e_dark_avg) / e_laser2

        laser_times = np.concatenate([laser1_times, laser2_times])
        laser_factor = np.concatenate([laser1_factor, laser2_factor])[np.argsort(laser_times)]

        self.laser_factor = laser_factor

        return laser_factor
