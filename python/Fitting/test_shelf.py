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

    def test_photon_fit_Ne_valuesAsExpected(self):
        knownNe = [3.97988057e+12, 4.11835281e+12, 5.58449743e+12,
                   6.40817706e+12, 9.19949227e+12, 1.10746767e+13,
                   1.39967603e+13, 1.43354654e+13, 1.66479582e+13,
                   1.59293090e+13, 1.96541527e+13, 2.00978410e+13,
                   2.39626552e+13, 2.32517587e+13, 2.69264436e+13,
                   2.26802328e+13, 2.52800592e+13, 2.17260446e+13,
                   2.55272835e+13, 2.20264548e+13, 2.34591488e+13,
                   2.05990239e+13, 2.35990964e+13, 1.74606725e+13,
                   1.98292599e+13, 1.75320991e+13, 1.93718237e+13,
                   1.71432204e+13, 1.95083539e+13, 1.69346191e+13,
                   1.89623989e+13, 1.70500039e+13, 1.80182366e+13,
                   1.53638005e+13, 1.98079839e+13, 1.88804488e+13,
                   2.37843675e+13, 2.30203964e+13, 2.54769258e+13,
                   3.12058832e+13, 2.40031135e+13, 2.44984516e+13]
        self.poly.photon_fit()

        self.assertTrue(np.allclose(self.poly.ne, knownNe))

    def test_photon_fit_Ne_error_valuesAsExpected(self):
        knownNe_error = [2.11227220e+11, 1.86210242e+11, 3.06474335e+11,
                         3.54638815e+11, 2.19072064e+11, 6.32862269e+11,
                         8.20374247e+11, 5.91668305e+11, 5.43931758e+11,
                         6.04540070e+11, 5.67031123e+11, 6.01230973e+11,
                         7.76371648e+11, 4.27578895e+11, 5.86317254e+11,
                         5.18568977e+11, 4.99883779e+11, 4.69643707e+11,
                         7.30810591e+11, 4.26678379e+11, 5.77200134e+11,
                         4.20256075e+11, 4.54356043e+11, 4.81834660e+11,
                         4.79704137e+11, 2.93935396e+11, 5.29228665e+11,
                         4.23550805e+11, 3.57205869e+11, 3.80602000e+11,
                         4.22107811e+11, 4.52455140e+11, 4.88320842e+11,
                         2.85027967e+11, 5.38248252e+11, 3.38958995e+11,
                         5.36362992e+11, 5.00059298e+11, 5.04157547e+11,
                         3.41652845e+12, 7.23113437e+11, 1.92266278e+12]
        self.poly.photon_fit()

        self.assertTrue(np.allclose(self.poly.ne_error, knownNe_error))

    def test_photon_fit_Te_valuesAsExpected(self):
        knownTe = [0.01482608, 0.04693883, 0.07952711, 0.13255483, 0.19272205,
                   0.27245635, 0.31518656, 0.31813617, 0.36190176, 0.41702812,
                   0.47470818, 0.46878968, 0.56646724, 0.68485457, 0.95937591,
                   0.81477321, 0.8994289, 0.99806146, 1.25236959, 1.10766692,
                   1.21275341, 1.16588101, 1.15755014, 1.06352596, 1.09668084,
                   1.07304799, 1.14706717, 1.14334928, 1.28352763, 1.3785052,
                   1.37833247, 1.29647209, 0.73493836, 0.76650927, 1.01987109,
                   1.10760717, 1.1420678, 1.1262104, 1.07685441, 0.0632094,
                   0.24434756, 0.07132272]
        self.poly.photon_fit()

        self.assertTrue(np.allclose(self.poly.Te, knownTe))

    def test_photon_fit_Te_error_valuesAsExpected(self):
        knownTe_error = [0.00087947, 0.0031695, 0.00660954, 0.00850789, 0.00416641,
                         0.02108479, 0.02668821, 0.01846838, 0.0154779, 0.02176412,
                         0.01429641, 0.01562843, 0.01569309, 0.0068087, 0.01449045,
                         0.01304054, 0.01076518, 0.0152891, 0.03343677, 0.01393408,
                         0.02544942, 0.01705251, 0.01465602, 0.02511195, 0.02126247,
                         0.00819722, 0.02734183, 0.02367624, 0.01496886, 0.02672297,
                         0.02615037, 0.03179662, 0.01524802, 0.00794177, 0.02279461,
                         0.01125635, 0.02003201, 0.01835617, 0.01399347, 0.01202627,
                         0.00845562, 0.00669983]

        self.poly.photon_fit()

        self.assertTrue(np.allclose(self.poly.Te_error, knownTe_error))

    def test_photon_fit_Pe_valuesAsExpected(self):
        knownPe = [0.00945276, 0.03096837, 0.07114785, 0.13607946, 0.2840258,
                   0.48338203, 0.70673684, 0.73061293, 0.96519305, 1.06420377,
                   1.49466392, 1.50935001, 2.17456429, 2.55103653, 4.13837951,
                   2.96037524, 3.64256605, 3.47376522, 5.12152889, 3.90855567,
                   4.55771605, 3.84736493, 4.3762054, 2.97489452, 3.48376838,
                   3.01380793, 3.55976943, 3.14003033, 4.01132971, 3.73978257,
                   4.18706572, 3.54119763, 2.12141538, 1.88659459, 3.23629475,
                   3.35012169, 4.3515703, 4.15331473, 4.39507736, 0.31599534,
                   0.93958936, 0.27991685]

        self.poly.photon_fit()

        self.assertTrue(np.allclose(self.poly.Pe, knownPe))

    def test_photon_fit_Pe_error_valuesAsExpected(self):
        knownPe_error = [0.0007524, 0.00251662, 0.00708596, 0.0115325, 0.0091351,
                         0.0465013, 0.07278043, 0.05204036, 0.05194693, 0.06867177,
                         0.06233544, 0.06760692, 0.09269845, 0.05332818, 0.10966884,
                         0.08262273, 0.08419445, 0.09203471, 0.20048829, 0.09027753,
                         0.14738721, 0.09658031, 0.10084181, 0.10804367, 0.10800441,
                         0.05552618, 0.12906431, 0.10122541, 0.08708187, 0.11099739,
                         0.12246529, 0.12795977, 0.07240657, 0.04008839, 0.11386664,
                         0.06911235, 0.12432145, 0.1127932, 0.10404923, 0.06936497,
                         0.04310926, 0.03426368]

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
