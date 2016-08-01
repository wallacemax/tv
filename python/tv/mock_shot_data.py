__author__ = 'maxwallace'
import pickle
import sys
import pdb

class mock_shot_data:  ### (1)
    def __init__(self, shotid):

        self.server = 'NSTX'
        self.shotid = shotid

    def get_tree_data(self, server, treename, requestedTDI):
        if len(requestedTDI) == 0:
            pass

        foo = [['NEF', 'ACTIVESPEC', 'MPTS.OUTPUT_DATA.BEST.FIT_NE'],
             ['PEF', 'ACTIVESPEC', 'MPTS.OUTPUT_DATA.BEST.FIT_PE'],
             ['TEF', 'ACTIVESPEC', 'MPTS.OUTPUT_DATA.BEST.FIT_TE'],
             ['IP', 'WF', 'IP'],
             ['WMHD', 'EFIT01', 'RESULTS.AEQDSK.WMHD']
             ]

        nodeid = ''
        for key, tree, tdi in foo:
            if tree == treename and tdi == requestedTDI:
                nodeid = key

        bar = self.get_pickled(nodeid.replace('\\', '').replace('::', ''))

        #bar = [time_signal, time_units, radial_signal, radial_units, signal, units]
        return bar

    def does_shot_exist(self, shotid):
        return shotid in ['130000', '205088', '204062']

    def get_pickled(self, var):
        file = open('sample_data/' + str(self.shotid) + '_' + var + '.pk', 'rb')
        data = pickle.load(file)
        file.close()
        return data

    def test(self):
        foo = mock_shot_data(self.shotid)
        current = foo.get_tree_data('\\ip')
        stored_energy = foo.get_tree_data('\\EFIT01::WMHD')
        nef = foo.get_tree_data('\\NEF')
        pef = foo.get_tree_data('\\PEF')
        tef = foo.get_tree_data('\\TEF')
        pdb.set_trace()

if __name__ == '__main__':
    foo = mock_shot_data(130000)
    foo.test()

#091515 latest shot is 201287