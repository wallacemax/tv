from unittest import TestCase
import pickle

import numpy as np

import shelf

__author__ = 'maxwallace'


class TestShelf(TestCase):
    poly = shelf.Shelf

    def setUp(self):
        self.poly = self.create_shelf(self.loadpickle('args'))
        self.poly.photoelectrons()

    def create_shelf(self, args):
        """the routine that is multiprocessed, the true guts of the program"""
        # a list is passed since multiprocessing.pool only accepts a single argument per processes
        shelf_id, SHOT, param, calib, voltage, vdac, times = args
        poly = shelf.Shelf(shelf_id, SHOT, param, calib, voltage, vdac, times)
        return poly

    def test_photon_fit_Ne_valuesForAccuracy(self):
        knownNe = np.genfromtxt('nef.csv', delimiter=',', dtype='float')

        self.poly.photon_fit()

        print('Ne:' + np.array_str(self.poly.ne) + '\n' + 'Kn:' + np.array_str(knownNe))
        self.assertTrue(np.allclose(self.poly.ne, knownNe))

    def test_photon_fit_Ne_error_valuesForAccuracy(self):
        knownNe_error = np.genfromtxt('dnef.csv', delimiter=',', dtype='float')
        self.poly.photon_fit()

        self.assertTrue(np.allclose(self.poly.ne_error, knownNe_error))

    def test_photon_fit_Te_valuesForAccuracy(self):
        knownTe = np.genfromtxt('tef.csv', delimiter=',', dtype='float')

        self.poly.photon_fit()

        self.assertTrue(np.allclose(self.poly.Te, knownTe))

    def test_photon_fit_Te_error_valuesForAccuracy(self):
        knownTe_error = np.genfromtxt('dtef.csv', delimiter=',', dtype='float')

        self.poly.photon_fit()

        self.assertTrue(np.allclose(self.poly.Te_error, knownTe_error))

    def test_photon_fit_Pe_valuesForAccuracy(self):
        knownPe = np.genfromtxt('pef.csv', delimiter=',', dtype='float')

        self.poly.photon_fit()

        self.assertTrue(np.allclose(self.poly.Pe, knownPe))

    def test_photon_fit_Pe_error_valuesForAccuracy(self):
        knownPe_error = np.genfromtxt('dpef.csv', delimiter=',', dtype='float')

        self.poly.photon_fit()

        self.assertTrue(np.allclose(self.poly.Pe_error, knownPe_error))

    def load_args(self):
        return self.loadpickle('args')

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

    def loadpickle(self, varname):
        """
        :type varname: basestring
        """
        filename = (varname.lower() + '.pic')
        f = open(filename, 'rb')
        foo = pickle.load(f, encoding='iso-8859-1')
        f.close()
        return foo
