__author__ = 'maxwallace'
import pickle
import sys

class mock_shot_data:  ### (1)
    def __init__(self, treename, shotid):

        self.treename = treename
        self.shotid = shotid

    def get_tree_data(self, nodeid):

        foo = []

        if 'CPASMA' in nodeid:
            foo = self.get_pickled('CPLASMA')
        elif 'WMHD' in nodeid:
            foo = self.get_pickled('WMHD')
        else:
            foo = self.get_pickled(str(nodeid[-2:]).lower() + '_fit')

        return foo

    def get_pickled(self, var):
        file = open(var + '.pk', 'rb')
        data = pickle.load(file, encoding='latin1')
        file.close()
        return data

    def does_shot_exist(self, shotid):
        return shotid == 130000

    def test(self):
        print('init')
        foo = mock_shot_data('nstx', 130000)
        print('try getting Ne')
        print(foo.get_tree_data('\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_NE'))
        print('try getting Pe')
        print(foo.get_tree_data('\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_PE'))
        print('try getting Te')
        print(foo.get_tree_data('\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_TE'))
        print('try switching to EFIT01 tree')
        foo = mock_shot_data('EFIT01', 130000)
        print('try getting plasma current')
        print(foo.get_tree_data('\EFIT01::TOP.RESULTS.GEQDSK:CPASMA'))
        print('try getting stored energy')
        print(foo.get_tree_data('\EFIT01::TOP.RESULTS.AEQDSK:WMHD'))
        print('yay!')

if __name__ == '__main__':
    foo = mock_shot_data('nstx', 130000)
    foo.test()
