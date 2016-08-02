__author__ = 'maxwallace'

omfitpath = "/p/omfit/OMFIT-source/src"

import sys
import os.path
sys.path.insert(0, omfitpath)

try:
    from omfit_tree import *
except ImportError:
    raise

import pdb
import pickle

class OMFIT_shot_data:  ### (1)
    def __init__(self, shotid):
        self.server = 'NSTX'
        self.shotid = int(shotid)

    def does_shot_exist(self, shotid):
        isThomson = OMFITmdsValue(server=self.server, treename='ACTIVESPEC', shot=shotid,
                                  TDI='MPTS.OUTPUT_DATA.BEST.FIT_NE', quiet=True).units() is not None
        isIP = OMFITmdsValue(server=self.server, treename='WF', shot=shotid,
                                    TDI='IP', quiet=True).units() is not None

        return isThomson and isIP

    def get_tree_data(self, server, treename, requestedTDI):
        #foo = OMFITmdsValue(server='NSTX', treename='ACTIVESPEC', shot='205088', TDI='MPTS.OUTPUT_DATA.BEST.FIT_NE')

        #pdb.set_trace()

        data = OMFITmdsValue(server=server, treename=treename, shot=self.shotid, TDI=requestedTDI)

        units = data.units()

        signal = data.data()

        time_signal = data.dim_of(0) # for NEF PEF TEP IP WMHD maybe not others
        time_units = data.units_dim_of(0)

        radial_signal = data.dim_of(1)
        radial_units = data.units_dim_of(1)

        bar = [time_signal, time_units, radial_signal, radial_units, signal, units]
        return bar


    def pickle_data(self, paramdata):
        var_name = str(paramdata[0])
        treename = str(paramdata[1])
        tdi = str(paramdata[2])

        fileName = str(self.shotid) + '_' + var_name + '.pk'
        file = open(fileName, 'wb')
        foo = self.get_tree_data(self.server, treename, tdi)
        pickle.dump(foo, file)
        file.close()
        print('pickled {} into {}'.format(tdi, fileName))

    def test(self):
        # foo = OMFITmdsValue(server='NSTX', treename='ACTIVESPEC', shot='205088', TDI='MPTS.OUTPUT_DATA.BEST.FIT_NE')
        # foo = OMFITmdsValue(server='NSTX', treename='WF', shot='205088', TDI='IP')
        # bar = OMFITmdsValue(server='NSTX', treename='EFIT01', shot='205088', TDI='RESULTS.AEQDSK.WMHD')

        pdb.set_trace()
        tags = [['NEF', 'ACTIVESPEC', 'MPTS.OUTPUT_DATA.BEST.FIT_NE'],
                ['PEF', 'ACTIVESPEC', 'MPTS.OUTPUT_DATA.BEST.FIT_PE'],
                ['TEF', 'ACTIVESPEC', 'MPTS.OUTPUT_DATA.BEST.FIT_TE'],
                ['IP', 'WF', 'IP'],
                ['WMHD', 'EFIT01', 'RESULTS.AEQDSK.WMHD'],
                ['ENGIP', 'ENGINEERING', 'PPCC.PCS.RA.RA_AUC_IPL'],
                ['betap', 'EFIT01', 'RESULTS.AEQDSK.BETAP']
                ]

        for fetchtag in tags:
            print('pickling {} from {} into {}'.format(fetchtag[0], fetchtag[1], fetchtag[2]))
            self.pickle_data(fetchtag)

        # self.pickle_data('\\TEF', 'TEF')

if __name__ == '__main__':
    shotno = sys.argv[1]
    foo = OMFIT_shot_data(shotno)
    doesshotexist = foo.does_shot_exist(shotno)
    print("Shot exists: {}".format(doesshotexist))
    if doesshotexist:
        foo.test()