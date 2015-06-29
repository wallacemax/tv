__author__ = 'mwallace'

import pickle
import pdb

import shelf
import mpts_data

data = mpts_data.MPTS_data()


class PhotonFitting:
    def main(self):
        SHOT, calib, calib_year, nchannel, param, times, vdac, voltage, scaling, ip_data, ip_zeroes = self.load_data()
        """perfect is the enemy of the good."""

        data.scaling = scaling
        data.ip_zeroes = ip_zeroes
        data.ip_data = ip_data

        self.run_mpts(SHOT, calib_year, nchannel, param, times, vdac, voltage)

    def load_data(self):
        SHOT = self.loadpickle('SHOT')
        calib = self.loadpickle('calib')
        calib_year = self.loadpickle('calib_year')
        nchannel = self.loadpickle('nchannel')
        param = self.loadpickle('param')
        times = self.loadpickle('times')
        vdac = self.loadpickle('vdac')
        voltage = self.loadpickle('voltage')
        scaling = self.loadpickle('scaling')
        ip_data = self.loadpickle('ip_data')
        ip_zeroes = self.loadpickle('ip_zeroes')
        return SHOT, calib, calib_year, nchannel, param, times, vdac, voltage, scaling, ip_data, ip_zeroes

    def mpts(self, args):
        """the routine that is multiprocessed, the true guts of the program"""
        # a list is passed since multiprocessing.pool only accepts a single argument per processes
        shelf_id, SHOT, param, calib, voltage, vdac, times = args
        poly = shelf.Shelf(shelf_id, SHOT, param, calib, voltage, vdac, times)
        poly.photoelectrons()
        poly.photon_fit()
        pdb.set_trace()
        return poly

    def run_mpts(self, SHOT, calib, nchannel, param, times, vdac, voltage):
        args = [[i, SHOT, param[str(i)], calib, voltage[i], vdac[i], times] for i in range(nchannel)]
        ind = 2
        # poly = Shelf(ind, SHOT, param[str(ind)], calib, voltage[ind], vdac[ind], times)
        poly = self.mpts(args[ind])
        print(poly)
        poly.shelf_plot(data.scaling, data.ip_zeroes, data.ip_data)
        for i in range(poly.channels):
            poly.photon_volt_plot(i)
            poly.photon_plot(i)

    @staticmethod
    def drivepickle(varname, variable):
        """

        :type varname: basestring
        """
        filename = (varname + '.pic')
        f = open(filename, 'wb')
        pickle.dump(variable, f)
        f.close()

    @staticmethod
    def loadpickle(varname):
        """
        :type varname: basestring
        """
        filename = (varname.lower() + '.pic')
        f = open(filename, 'rb')
        foo = pickle.load(f)
        f.close()
        return foo


foo = PhotonFitting()
foo.main()
