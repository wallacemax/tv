from unittest import TestCase

import scipy.stats

import shelf

__author__ = 'maxwallace'


class TestShelf(TestCase):
    poly = shelf.Shelf
    testData = [9, 10, 12, 11, 8, 10]

    def test_curveFit_knownData_knownChisquare(self):
        chi2, p = scipy.stats.chisquare(self.testData)

        self.assertTrue(chi2 == 1.0)

    def test_shelfFit_knownData_knownChisquare(self):
