"""06/2015 WWallace wallace.max@gmail.com
Refactor of code.  Separation of concerns, dry, testability.  The chi-square error we are running down is only here.
"""

import math
import os

from scipy import optimize, integrate
import scipy.stats
import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mpts_calculations


class Shelf:
    """a single polychromator shelf"""

    def __init__(self, shelf_id, shot, param, calib_total, voltage, vdac, times):
        """load configuration parameters and the voltage signal into the shelf"""
        sid = str(shelf_id)
        self.shot = shot
        self.times = times

        # general parameters
        self.shelf_id = int(shelf_id)
        self.shelf_num = int(shelf_id) + 1
        self.multiplexed = bool(param["multiplexed"])
        self.phase = param["phase"]
        self.radius = np.array(param["radius"])
        self.radius_error = np.array(param["radius_error"])
        self.scat_angle = param["scat_angle"]
        self.channels = param["channels"]
        self.fiber_len = np.array(param["fiber_len"])
        self.fiber_num = np.array(param["fiber_num"])
        self.mdspath = param["mdspath"]

        # For testing/debugging only
        self.IDL_CONSTANTS = True

        # detectors that are raman for later analysis
        if self.phase == "3":
            self.pos = [0, 1, 2, 3]
        else:
            self.pos = [0, 1, 3, 4, 5]

        # =====================

        # detector parameters
        self.apd_id = param["apd_id"]
        self.preamp_id = param["preamp_id"]

        # voltage
        self.breakdown_volt = np.array(param["breakdown_volt"])
        self.max_volt = np.array(param["max_volt"])
        self.oper_volt = np.array(param["oper_volt"])

        # wavelength parameters
        self.focus_wave = np.array(param["focus_wave"])
        self.focus_wave_error = np.array(param["focus_wave_error"])

        # =====================

        # qt calibration -- quantum transmission of the APD's
        self.qt = np.array(param["qt"])
        self.qt_error = np.array(param["qt_error"])
        self.qt_fiber = np.array(param["qt_fiber"])
        self.qt_fiber_error = np.array(param["qt_fiber_error"])
        self.qt_laser = param["qt_laser"]
        self.qt_laser_error = param["qt_laser_error"]
        self.qt_raman = np.array(param["qt_raman"])
        self.qt_raman_error = np.array(param["qt_raman_error"])

        # wavelength divisions
        self.qt_wave_div = np.array(param["qt_wave_div"])
        self.wave_div = param["wave_div"]

        # perform a roll on qt_wave_div, used for the fractional error calculation
        self.qt_wave_div_roll = self.roll_qt_wave_div()

        # temperature coefficients
        self.qt_cg = np.array(param["qt_cg"])
        self.qt_rg = np.array(param["qt_rg"])

        # =====================
        # voltage
        self.set_voltage(voltage)

        # =====================
        # gain
        self.set_gain(param, vdac)

        # =====================

        # Year/Shutter calibration parameters
        # calib_year = calib_total[self.times.get_year()]
        # calib = calib_year[self.times.shutters]
        calib = calib_total[self.times.shutters]

        # RAYLEIGH
        if self.phase != "3":
            self.ray_sp = np.array(calib["ray_sp"])[:, shelf_id]
            self.ray_st = np.array(calib["ray_st"])[:, shelf_id]
            self.ray_sp_error = np.array(calib["ray_sp_error"])[:, shelf_id]
            self.ray_st_error = np.array(calib["ray_st_error"])[:, shelf_id]

            self.ray_gain = calib["m_ray"][shelf_id]

            self.ray_p_laser_avg = np.array(calib["elsrsp_ray_avg"])
            self.ray_t_laser_avg = np.array(calib["elsrst_ray_avg"])

            self.pressure_ray = calib["pressure_ray"]

        # RAMAN
        self.ram_sp = np.array(calib["ram_sp"])[:, shelf_id]
        self.ram_st = np.array(calib["ram_st"])[:, shelf_id]
        self.ram_sp_error = np.array(calib["ram_sp_error"])[:, shelf_id]
        self.ram_st_error = np.array(calib["ram_st_error"])[:, shelf_id]

        self.ram_gain = calib["m_ram"][shelf_id]

        self.ram_p_laser_avg = np.array(calib["elsrsp_ram_avg"])
        self.ram_t_laser_avg = np.array(calib["elsrst_ram_avg"])

        self.pressure_ram = calib["pressure_ram"]

        # fcor/gcor
        self.set_fcor_gcor(calib_total, shelf_id)

        # calculate the geometric factor (nfactor)
        self.geometric_factor()

        # calculate the laser factor (lfactor)
        self.times.laser_energy_scale(calib)

    def roll_qt_wave_div(self):
        u1 = self.qt_wave_div - np.roll(self.qt_wave_div, 1)
        u2 = np.roll(self.qt_wave_div, -1) - self.qt_wave_div
        u1[0] = 0
        u2[-1] = 0
        return (u1 + u2) / 2.0

    def set_fcor_gcor(self, calib_year, shelf_id):
        if self.phase == "3":
            self.fcor = np.array(calib_year["fcor"])[shelf_id - 20]
            self.fcor_error = np.array(calib_year["fcor_error"])[shelf_id - 20]

            self.gcor = np.array(calib_year["gcor"])[:, shelf_id - 20].T
            self.gcor_error = np.array(calib_year["gcor_error"])[:, shelf_id - 20].T

    def __repr__(self):
        """handle casting the shelf to a string (includes the print function)"""
        s = ""
        s += "Shelf #" + str(self.shelf_num) + " (index " + str(self.shelf_id) + ")\n\t"
        s += "channels = " + str(self.channels) + "\n\tradius = " + str(self.radius) + "\n\tangle = " + str(
            self.scat_angle) + "\n\t"
        s += "Path = " + self.mdspath
        return s

    def volt_plot(self, channel):
        """"plots the fast and slow signal for a specific channel"""
        path = "img/" + str(self.shot)
        if not os.path.exists(path):
            os.mkdir(path)
        ipend = self.times.ip_end
        ipstart = self.times.ip_start
        trange = self.times[ipstart:(ipend + 50)]
        fig = plt.figure()
        ax = fig.add_subplot(111)
        il = np.extract(np.logical_and(self.times.index_laser >= ipstart, self.times.index_laser <= ipend + 50),
                        self.times.index_laser)
        ax.axvline(x=trange[ipend - ipstart - 1], color='r')
        for i in il:
            ax.axvline(x=self.times[i], color='y')

        ax.plot(trange, self.fast[channel][ipstart:ipend + 50], label="fast")
        ax.plot(trange, self.slow[channel][ipstart:ipend + 50], label="slow")

        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("APD voltage (V)")
        ax.set_title("Fast and Slow signal (shelf " + str(self.shelf_num) + " channel " + str(channel) + ", " + str(
            self.focus_wave[channel]) + " nm)")

        print(path + "/volt_plot_" + str(self.shelf_num) + "_" + str(channel) + ".png")
        fig.savefig(path + "/volt_plot_" + str(self.shelf_num) + "_" + str(channel) + ".png", bbox_inches="tight")

    def fast_plot(self, channel):
        """"plots the fast signal for a specific channel"""
        path = "img/" + str(self.shot)
        if not os.path.exists(path):
            os.mkdir(path)
        ipend = self.times.ip_end
        ipstart = 0
        trange = self.times[ipstart:(ipend + 50)]
        fig = plt.figure()
        ax = fig.add_subplot(111)
        il = np.extract(np.logical_and(self.times.index_laser >= ipstart, self.times.index_laser <= ipend + 50),
                        self.times.index_laser)
        ax.axvline(x=trange[ipend - ipstart - 1], color='r')
        ax.axvline(x=0, color='black')
        # MW now think this type conversion error is cool.  we're filtering the array by the bool val
        ax.axhline(y=np.mean(np.extract(self.times.times <= -.25, self.fast[channel])), color='black')
        for i in il:
            ax.axvline(x=self.times[i], color='y')

        ax.plot(trange, self.fast[channel][ipstart:ipend + 50], label="fast")

        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("APD voltage (V)")
        ax.set_title("Fast signal (shelf " + str(self.shelf_num) + " channel " + str(channel) + ", " + str(
            self.focus_wave[channel]) + " nm)")
        ax.set_ylim(np.min(self.fast[channel]), np.max(self.fast[channel]))

        print(path + "/fast_plot_" + str(self.shelf_num) + "_" + str(channel) + ".png")
        fig.savefig(path + "/fast_plot_" + str(self.shelf_num) + "_" + str(channel) + ".png", bbox_inches="tight")

    def shelf_plot(self, scaling, ip_zeroes, ip_data):
        """plots a single shelf"""

        fig = plt.figure()
        taxis = self.times[self.times.index_laser_cut]

        # density
        axd = fig.add_subplot(221)
        axd.errorbar(taxis, self.ne, color='blue', yerr=self.ne_error, ecolor='black')
        axd.set_xlabel("time (seconds)")
        axd.set_ylabel("density (1/cm^3)")
        axd.set_title("Electron Density")

        # temperature
        axt = fig.add_subplot(222)
        axt.errorbar(taxis, self.Te, color='blue', yerr=self.Te_error, ecolor='black')
        axt.set_xlabel("time (seconds)")
        axt.set_ylabel("temperature (keV)")
        axt.set_title("Electron Temperature")

        # pressure
        axp = fig.add_subplot(223)
        axp.errorbar(taxis, self.Pe, color='blue', yerr=self.Pe_error, ecolor='black')
        axp.set_xlabel("time (seconds)")
        axp.set_ylabel("pressure (kPa)")
        axp.set_title("Electron Pressure")

        # plasma current
        # ip_taxis = poly.times.scaling * np.arange(poly.times.ip_zeroes[0], poly.times.ip_zeroes[1])
        ip_taxis = scaling * np.arange(ip_zeroes[0], ip_zeroes[1])
        axi = fig.add_subplot(224)
        axi.set_xlim([ip_taxis[0], ip_taxis[-1]])
        # axi.plot(ip_taxis, poly.times.ip_data)
        axi.plot(ip_taxis, ip_data)
        axi.set_title("Plasma Current")
        axi.set_xlabel("time (seconds)")
        axi.set_ylabel("current (A)")

        plt.tight_layout()
        plt.subplots_adjust(top=0.9)

        suptitle = "Shot " + str(self.shot) + ", Shelf " + str(self.shelf_id + 1) + \
                   ", radius = " + "%.3f" % self.radius + "cm"
        fig.suptitle(suptitle, fontsize=16)

        num_str = str(self.shelf_id)
        if len(num_str) == 1: num_str = "0" + num_str

        print("Writing " + "img/" + str(self.shot) + "/mpts_out_" + num_str + ".png")
        fig.savefig("img/" + str(self.shot) + "/mpts_out_" + num_str + ".png", bbox_inches="tight")

        # plt.show()

    def photoelectrons(self, offset=0):
        """finds the number of photons that hit each APD"""
        ind_before = self.times.index_before
        ind_laser = self.times.index_laser_cut

        # constants
        if self.IDL_CONSTANTS:
            ec = 1.6022e-19
        else:
            ec = 1.60217657e-19  # electron charge, Coulombs
        Rfb = 5e4  # Ohms
        tau = 50e-9  # ?

        # standard deviation of DC offset, used in finding error
        dl0_fast = np.std(self.fast[:, ind_before], axis=1)
        dl0_slow = np.std(self.slow[:, ind_before], axis=1)

        # subtract DC offset (first background noise)

        dl_fast = self.fast[:, ind_laser + offset] - np.mean(self.fast[:, ind_before], axis=1)[:, None]
        dl_slow = self.slow[:, ind_laser + offset] - np.mean(self.slow[:, ind_before], axis=1)[:, None]

        # dl_fast = self.fast[:, ind_laser]
        # dl_slow = self.slow[:, ind_laser]

        # a[:, None] is the same as a[:, np.newaxis]. Allows for array broadcasting over rows, rather than columns

        # find number of scattered photons
        Nsc_fast = dl_fast * (self.cfb / (self.Gfast * self.gain * ec))[:, None]
        Nsc_slow = dl_slow / (Rfb * self.gain * ec * self.Gslow)[:, None]

        Fex = self.cF[:, 0] + self.cF[:, 1] * self.gain  # excess noise

        # find error in number of scattered photons
        # dark readout noise + fast signal * excess noise + slow signal * excess noise

        c0 = (self.cfb / (self.gain * ec * self.Gfast))
        c1 = (Fex * self.cfb / (self.gain * ec * self.Gfast))
        c2 = (Fex * tau / (self.gain * Rfb * ec * self.Gslow))

        Nsc_error = np.sqrt(((dl0_fast * c0) ** 2)[:, None] + (dl_fast * c1[:, None]) + (dl_slow * c2[:, None]))
        Nsc_error_fast = np.sqrt(((dl0_fast * c0) ** 2)[:, None] + (dl_fast * c1[:, None]))

        # if offset == 0:
        #     desc = "(at laser)"
        # elif offset > 0:
        #     desc = "(" + str(offset) + " after laser)"
        # else:
        #     desc = "(" + str(offset) + " before laser)"

        self.Nsc_fast = Nsc_fast
        self.Nsc_slow = Nsc_slow
        self.Nsc_error_slow = Nsc_error
        self.Nsc_error_fast = Nsc_error_fast

        # Only the fast signal is important
        # time index is used for fitting
        self.Nsc = Nsc_fast
        self.Nsc_error = Nsc_error
        self.Nsc_weight = 1 / (self.Nsc_error ** 2)

        print("done with photoelectrons!")

        return Nsc_fast

    def geometric_factor(self):
        """finds the geometric factor 'g' and error, a function of the year and shutter configuration"""

        sigma_n2 = 3.81e-29  # cross section for N2 (cm^2)
        n0 = 3.27e16  # neutral gas factor for N2 at room temp (cm^3/torr)
        hc = 12398.42  # planck constant * speed of light (Angstrom eV)
        r0 = 2.8179e-13  # classical electron radius (cm)
        ec = 1.602e-19  # electron charge (Coulomb)
        lam = 10641.4  # Nd:YAG laser wavelength (Angstrom)
        Gfast = 10  # fast channel gain

        # Raman

        # must be multiplied by 4/7 to counteract the polarizer being in during detection, 1e-31 since N2 wasn't used (?)
        # I don't know, this is what the IDL does
        # for now,  qt raman and error are scalar quantities, just like qt laser down below
        qt_raman = self.qt_raman[0] * 4 / 7 * 1e-31
        qt_raman_error = self.qt_raman_error[0] * 4 / 7 * 1e-31

        if self.phase != "3":
            cfb = self.cfb[3]
            cfb_error = self.cfb_error[3]
        else:
            cfb = self.cfb[0]
            cfb_error = self.cfb_error[3]

        # ram_p_laser_avg is the same as Elaser_R in the IDL code

        ram_g = (self.ram_sp) * cfb / ((self.ram_p_laser_avg / hc) * qt_raman * self.ram_gain)
        ram_g /= n0 * self.pressure_ram * ec * Gfast
        # g = np.outer(ram_g, self.cfb) #2 x 6

        # error_2_1 = (self.ram_sp_error/self.ram_sp)**2 + 0.01**2 + (qt_raman_error/qt_raman)**2
        # error_channel_1 = (self.cfb_error/self.cfb)**2

        # g_error = g * np.sqrt(np.tile(error_2_1, (self.channels, 1)).T + np.tile(error_channel_1, (2, 1)))

        ram_g_error = ram_g * np.sqrt(
            (self.ram_sp_error / self.ram_sp) ** 2 + 0.01 ** 2 + (qt_raman_error / qt_raman) ** 2 + (
                cfb_error / cfb) ** 2)

        self.ram_g = ram_g
        self.ram_g_error = ram_g_error

        self.ram_nfactor = r0 * r0 * self.ram_g * self.ram_p_laser_avg / hc
        self.ram_nfactor_error = r0 * r0 * self.ram_g_error * self.ram_p_laser_avg / hc

        self.nfactor = self.ram_nfactor
        self.nfactor_error = self.ram_nfactor_error

        # Rayleigh
        if self.phase != "3":
            ray_g = (self.ray_sp * self.cfb[2]) / ((self.ray_p_laser_avg / hc) * self.qt_laser * self.ray_gain)
            ray_g /= sigma_n2 * n0 * self.pressure_ray * lam * ec * Gfast
            # self.ray_g = ray_g

            # error = variance from measured signal + fast/slow calibration + torus pressure + spectral calibration
            ray_g_error = ray_g * np.sqrt(
                (self.ray_sp_error / self.ray_sp) ** 2 + (self.cfb_error[2] / self.cfb[2]) ** 2 + 0.01 ** 2 + (
                    self.qt_laser_error / self.qt_laser) ** 2)
            # self.ray_g_error = ray_g_error

            self.ray_g = ray_g
            self.ray_g_error = ray_g_error

            self.ray_nfactor = r0 * r0 * self.ray_g * self.ray_p_laser_avg / hc
            self.ray_nfactor_error = r0 * r0 * self.ray_g_error * self.ray_p_laser_avg / hc

    def photon_plot(self, channel):
        """"plots the fast and slow signal for a specific channel"""
        path = "img/" + str(self.shot)
        if not os.path.exists(path):
            os.mkdir(path)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.axvline(x=self.times[self.times.ip_end], color='red')
        ax.axhline(y=0, color='black')
        trange = self.times[self.times.index_laser_cut]
        ax.errorbar(trange, self.Nsc_fast[channel], label="fast", color='blue', yerr=self.Nsc_error_fast[channel],
                    ecolor='black')

        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Number of photons")
        ax.set_title("Fast number of photons (" + str(self.shelf_num) + " channel " + str(channel) + ", " + str(
            self.focus_wave[channel]) + " nm)")
        print(path + "/photon_plot_" + str(self.shelf_num) + "_" + str(channel) + ".png")
        fig.savefig(path + "/photon_plot_" + str(self.shelf_num) + "_" + str(channel) + ".png", bbox_inches="tight")

    def photon_volt_plot(self, channel):
        """plots the fast voltage and fast number of photons for a specific channel side by side"""
        path = "img/" + str(self.shot)
        if not os.path.exists(path):
            os.mkdir(path)

        trange = self.times[self.times.index_laser_cut]
        """
        fig = plt.figure()
        axv = fig.add_subplot(211)
        axp = fig.add_subplot(212)
        """

        fig, (axv, axp) = plt.subplots(2, sharex=True)
        axv.set_xlim([trange[0], trange[-1]])
        axp.set_xlim([trange[0], trange[-1]])

        # voltage (self.fast)
        axv.axhline(y=np.mean(self.fast[channel, self.times.index_before]), color='black')
        axv.plot(trange, self.fast[channel, self.times.index_laser_cut], color='blue')
        axv.set_xlabel("Time (seconds)")
        axv.set_ylabel("Voltage (V)")
        # axv.set_title("APD Fast Voltage")
        axv.set_title("APD Fast Signal Voltage (shelf " + str(self.shelf_num) + " channel " + str(
            channel) + ", " + "{0:.2f}".format(self.focus_wave[channel]) + " nm)")

        # photon (self.Nsc)
        axp.errorbar(trange, self.Nsc[channel], color='blue', yerr=self.Nsc_error[channel], ecolor='black')
        axp.set_xlabel("Time (seconds)")
        axp.set_ylabel("Number of Photons")
        axp.set_title("APD Fast Number of Photons")

        plt.tight_layout()
        plt.subplots_adjust(top=0.9)

        fig.suptitle("Channel " + str(channel) + "(" + str(self.focus_wave[channel]) + " nm)")

        print("Writing " + path + "/photon_volt_plot_" + str(self.shelf_num) + "_" + str(channel) + ".png")
        fig.savefig(path + "/photon_volt_plot_" + str(self.shelf_num) + "_" + str(channel) + ".png",
                    bbox_inches="tight")

    def param_guess(self, Nsc):
        """creates an initial guess of ne and Te"""

        # this guess is implemented exactly like the IDL code.
        # it is not very accurate.
        # sometimes the chi squares are in the range of 1e5
        # Nsc is passed as an argument since in phase 3, Nsc is transformed by fcor

        ne0 = np.sum(Nsc, axis=0) / 1000.0

        # guess
        # Rguess is ratio of 964/7 nm divided by sum of values 964/7 to 1064.1 exclusive
        if self.phase == "3":
            # focus_wave = [1053.0, 1028.0, 967.0, 870.0]
            Rguess = Nsc[2] / (Nsc[0] + Nsc[1])
        else:
            # focus_wave = [820.0, 964.0, 1064.1, 1058.5, 1048.0, 1024.0],
            Rguess = Nsc[1] / (Nsc[3] + Nsc[4] + Nsc[5])

        # CG are coefficients of a quartic polynomial that approximates a gaussian.
        # They are stored in IDL format, so the coefficients are reversed for numpy polyval
        Te0 = np.polyval(self.qt_cg[::-1], Rguess)
        Te0[Te0 > 2.0] = 2.0  # set maximum value to 2.0
        Te0[Te0 < 1e-4] = 1e-4  # set minimum value to 1e-4

        # export ne0 and Te0 into an parameter array a, where a[time index] = [ne0, Te0]
        a = np.array([ne0, Te0]).T

        return a

    def photon_calc(self, pos, ne, Te):
        """calculates the number of photons that are received by the detector, used in least squares"""
        # pos - the indices (detector numbers) in which there is relevant data
        # ne  - electron density
        # Te  - electron temperature

        # penalize the algorithm from choosing values outside the limits
        # Limits:
        #    Ne > 0
        #    Te > 1e-5
        # penalty: absurdly huge number
        if ne >= 0 and Te >= 1e-4:
            ne = abs(ne)
            Te = abs(Te)
            Sc = self.ts_spectra(Te)

            z = Sc * self.qt_fiber * self.qt[pos]

            # IDL uses INT_TABULATE.pro to do integration
            # INT_TABULATE uses a 5-point newton-cotes formula
            # this formula requires an equally spaced grid
            # IDL imposes an equally spaced grid, and cubically
            # interpolates points that are not at the grid values
            # this raises further error in the code, due to interpolation

            # scipy.integrate.simps uses simpson's rule
            # which is equivalent to a 3-point weighted newton cotes
            # weights are introduced due to the irregular wavelength divisions
            p = integrate.simps(y=z, x=self.qt_wave_div, axis=1)

            f = ne * p
        else:
            f = np.zeros_like(pos) + 1e50

        return f

    def fractional_error(self, Te, pos):
        """used to refine the weights when the fit is done for the second time"""
        # tends to blow up and kill any hope for fitting properly
        if Te < 1e-4: Te = 1e-4

        Sc = self.ts_spectra(Te)

        z = Sc * self.qt_fiber * self.qt[pos]
        z[z < 0] = 0

        z_error = abs(z) * np.sqrt(
            (self.qt_error[pos] / self.qt[pos]) ** 2 + (self.qt_fiber_error / self.qt_fiber) ** 2)

        p = integrate.simps(y=z, x=self.qt_wave_div, axis=1)

        # p_error = root sum of squares of dlambda*dz
        p_error = np.sqrt(np.sum((self.qt_wave_div_roll * z_error) ** 2, axis=1))

        output = p_error / p

        if (output > 0).all():
            return np.sqrt(output)
        else:
            return 0

    def ts_spectra(self, Te):
        """evaluates the selden formula without integrating or adding in qt and qt_fiber"""
        llaser = 10640  # laser wavelength in angstroms
        x = self.qt_wave_div / llaser - 1
        ct = math.cos(self.scat_angle * math.pi / 180.0)

        alpha = 255.5 / Te  # (255.5 keV. boltzmann constant is ignored since Te is in units of keV)
        A = (1 + x) ** 2 * np.sqrt(2 * (1 - ct) * (1 + x) + x ** 2)
        B = np.sqrt(1 + x ** 2 / (2 * (1 - ct) * (1 + x))) - 1
        C = math.sqrt(alpha / math.pi) * (1 - 15.0 / (16.0 * alpha) + 345.0 / (512.0 * alpha ** 2))

        Sc = (C * np.exp(-2 * alpha * B)) / A

        return Sc

    def ts_spectra_alt(self, Te):
        """evaluates the selden formula without integrating or adding in qt and qt_fiber"""
        llaser = 10640  # laser wavelength in angstroms
        x = self.qt_wave_div / llaser - 1
        # x= wavelength (scattered) over wavelength(incidental) - 1
        ct = math.cos(self.scat_angle * math.pi / 180.0)

        alpha = 255.5 / Te  # (255.5 keV. boltzmann constant is ignored since Te is in units of keV)
        A = (1 + x) ** 2 * np.sqrt(2 * (1 - ct) * (1 + x) + x ** 2)
        B = np.sqrt(1 + x ** 2 / (2 * (1 - ct) * (1 + x))) - 1
        C = math.sqrt(alpha / math.pi) * (1 - 15.0 / (16.0 * alpha) + 345.0 / (512.0 * alpha ** 2))

        Sc = (C * np.exp(-2 * alpha * B)) / A

        # Sc2 = C/(A * np.exp(-2 * alpha * B))

        return Sc

    def ts_spectra_alt_param(self, Te, qt, scat_angle):
        """evaluates the selden formula without integrating or adding in qt and qt_fiber"""
        # nstxusr/user/mpts/source/tsspect.pro
        # plotts_time, 139047, rads=[0,1,2,3,4,5], /nb
        llaser = 10640  # laser wavelength in angstroms
        x = qt / llaser - 1
        ct = math.cos(scat_angle * math.pi / 180.0)

        alpha = 255.5 / Te  # (255.5 keV. boltzmann constant is ignored since Te is in units of keV)
        A = (1 + x) ** 2 * np.sqrt(2 * (1 - ct) * (1 + x) + x ** 2)
        B = np.sqrt(1 + x ** 2 / (2 * (1 - ct) * (1 + x))) - 1
        C = math.sqrt(alpha / math.pi) * (1 - 15.0 / (16.0 * alpha) + 345.0 / (512.0 * alpha ** 2))

        Sc = (C * np.exp(-2 * alpha * B)) / A

        Sc2 = C/(A * np.exp(-2 * alpha * B))

        return Sc2


    # fitting routines start here!
    # IMPORTANT!
    #  ne is not the electron density, but instead is the density * a collection of constants
    #  this collection of constants is contained in nfactor with an associated error
    #  in this way, the fitting routine only needs to divide by the constants once

    def photon_fit(self):
        """the main routine for fitting"""
        # the fit is calculated once, the weights are updated, and then the fit is conducted again
        ND, NT = self.Nsc.shape  # number of detectors, time steps

        # initialize the parameter output arrays
        ne = np.zeros(NT)
        Te = np.zeros(NT)
        ne_error = np.zeros(NT)
        Te_error = np.zeros(NT)
        chisq = np.zeros(NT)
        p = np.zeros(NT)

        # KILL THE NEGATIVE PHOTONS!!!
        # if a measurement has a negative number of photons,
        # completely exclude it from the fitting routine.
        # no more absurd chi squares! no more max iterations!
        # NO MORE PAIN!!!

        # phase 3 requires fcor corrections, do a deep copy to dodge possible reference errors
        Nsc = np.copy(self.Nsc)
        Nsc_error = np.copy(self.Nsc_error)

        if self.phase == "3":
            # fcor corrections, based on year
            Nsc /= self.fcor[:, None]
            Nsc_error = abs(Nsc) * np.sqrt((Nsc_error / Nsc) ** 2 + (self.fcor_error / self.fcor)[:, None] ** 2)

            Nsc *= self.fcor[0]
            Nsc_error *= self.fcor[0]

        # total pos is the array of possible indices, (0,1,2,3) for phase 3 or (0,1,2,3,4,5) if not
        total_detectors = np.arange(ND)

        # mask_pos contains the (boolean) mask of the indices used in each time step
        # The mask very much effects the result that is given by the least squares routine.
        # If the mask is set to Nsc >= 0, very wild results can occur, such as temp = 5000 keV.
        # Small negative numbers (such as >= -40) are acceptable, as long as Nsc + Nsc_error >= 0
        # The negative numbers are accounted for by the error bars one standard deviation up


        masked_detectors = np.array([True for i in range(ND)])
        if self.phase != "3":
            masked_detectors[2] = False

        # initial guesses
        guesses = self.param_guess(Nsc)

        # pdb.set_trace()
        for i in range(NT):
            # iterate over time index
            # i'm sure there is a more efficient and pythonic way to do this

            detector_indexes = total_detectors[masked_detectors]

            y = Nsc[detector_indexes, i]
            dy = Nsc_error[detector_indexes, i]

            # perform the first curve fit to get a more accurate Te estimate
            afit, acov = optimize.curve_fit(self.photon_calc, xdata=detector_indexes, ydata=y, p0=guesses[i], sigma=dy)

            secondguess = [afit[0], afit[1] if afit[1] > 1e-4 else 1e-4]
            frac_error = self.fractional_error(afit[1], detector_indexes)

            second_dy = np.abs(y) * np.sqrt((dy / y) ** 2 + frac_error ** 2)
            # w1 = 1/(dy**2)
            #
            # feed the new weights and previously found values into a second round of fitting
            # , Dfun = self.photon_jacobian
            afit, acov = optimize.curve_fit(self.photon_calc, xdata=detector_indexes, ydata=y, p0=secondguess,
                                             sigma=second_dy)

            ne[i] = afit[0]
            Te[i] = afit[1]

            # find the reduced chi squared. The degrees of freedom is N-2
            yfit = self.photon_calc(detector_indexes, afit[0], afit[1])

            chisq[i] = np.sum(((yfit - y) / second_dy) ** 2) / (detector_indexes.shape[0] - 2)

            # if type(acov) == float:
            # pdb.set_trace()
            ne_cov = acov[0, 0]
            Te_cov = acov[1, 1]

            # standard deviation = sqrt((co)variance)
            ne_error[i] = np.sqrt(ne_cov)
            Te_error[i] = np.sqrt(Te_cov)

            # print i, guesses[i][1], Te1, afit[1]


        # done with fitting, now do calculations and export the data to self (class attributes)

        # kill the constants in the selden equation by dividing by nfactor
        self.ne = ne / (self.nfactor[self.times.laser_id] * self.times.laser_factor)
        self.ne_error = abs(self.ne) * np.sqrt(
            (ne_error / ne) ** 2 + (self.nfactor_error[self.times.laser_id] / self.nfactor[self.times.laser_id]) ** 2)

        self.Te = Te
        self.Te_error = Te_error

        # pressure = temperature * density * convert MeV to Joule
        self.Pe = self.ne * self.Te * 1.602e-13
        self.Pe_error = abs(self.Pe) * np.sqrt((self.ne_error / self.ne) ** 2 + (Te_error / Te) ** 2)

        self.chisq = chisq

        if self.phase == "3":
            # add in fcor/gcor correction
            gcor_laser = self.gcor[self.times.laser_id]
            gcor_laser_error = self.gcor_error[self.times.laser_id]
            self.ne /= gcor_laser
            self.ne_error = abs(self.ne) * np.sqrt(
                (self.ne_error / self.ne) ** 2 + (gcor_laser_error / gcor_laser) ** 2)

            self.Pe /= gcor_laser
            self.Pe_error = abs(self.Pe) * np.sqrt(
                (self.Pe_error / self.Pe) ** 2 + (gcor_laser_error / gcor_laser) ** 2)

            # for i in range(NT):
            #    print i, [self.ne[i], self.ne_error[i]], [self.Te[i], self.Te_error[i]], chisq[i]

    def set_gain(self, param, vdac):
        # extra gain parameters
        if self.phase == "3":
            self.vdac = vdac[:4]
        else:
            self.vdac = vdac
        self.cfb = np.array(param["cfb"])
        self.cfb_error = np.array(param["cfb_error"])
        self.cl = np.array(param["gain_linear_coeff"])
        self.ct = np.array(param["gain_temp_coeff"])
        self.cF = np.array(param["gain_noise_coeff"])
        # actual gain
        if self.phase == "3":
            self.Gfast = np.array([10, 10, 10, 10])
            self.Gslow = np.array([40, 40, 40, 40])
        else:
            self.Gfast = np.array([10, 10, 10, 10, 10, 10])
            self.Gslow = np.array([20, 20, 40, 40, 40, 40])
        mptscalc = mpts_calculations.mpts_calculations()
        self.gain = mptscalc.find_gain(self.cl, self.ct, self.channels, self.vdac)

    def set_voltage(self, voltage):
        # voltage
        # the voltage is given as an argument
        # TODO: what are fast and slow when !(self.multiplexed)?
        fast = []
        slow = []
        if self.multiplexed:
            # each block = [6 fast voltages | 6 slow voltages]
            voltage = voltage.reshape(len(voltage) / 12, 12).T
            if self.phase == "3":
                # phase 3 has only 4 detectors and also adds an extra block on the end of the signal
                fast = voltage[:4, :-1]
                slow = voltage[6:10, :-1]
            else:
                fast = voltage[:6, :]
                slow = voltage[6:, :]
        self.fast = fast
        self.slow = slow

# def chisquare(self, Nsc_calc, pos):
#     """Finds the chi squared value over time, for testing purposes only"""
#
#     # I think this function is deprecated
#
#     res = self.Nsc[pos] - Nsc_calc.T
#     chisq_part = (res / self.Nsc_errors[pos]) ** 2
#     chisq = np.sum(chisq_part, axis=0) / (pos.shape[0] - 2)
#
#     # reduced chi squared, so divide by N - 2
#     return chisq


"""
NOT IMPLEMENTED!!!
for some reason the Dfun keyword is not working in scipy.optimize.curve_fit
curve_fit uses leastsq, and any excess keyword arguments should be passed
straight to leastsq.
def photon_jacobian(self, X, ne, Te):
    #approximates the jacobian matrix of photon_calc at (ne, Te)
    #used in deciding the direction of the next step
    p = self.photon_calc(X, ne, Te)
    dTe = Te/100
    if dTe < 0: dTe = 1e-5
    dp_dne = p/ne
    dp_dTe = (self.photon_calc(X, ne, Te + dTe) - p)/dTe

    jacobian = np.array([dp_dne, dp_dTe])

    return jacobian
"""
