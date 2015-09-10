__author__ = 'maxwallace'
import pickle
import sys
import pdb

class mock_shot_data:  ### (1)
    def __init__(self, treename, shotid):

        self.treename = treename
        self.shotid = shotid

    def get_tree_data(self, nodeid):
        if len(nodeid) == 0:
            pass

        foo = self.get_pickled(nodeid.replace('\\', '').replace('::', ''))

        return foo[0], foo[1], foo[2].decode('utf-8'), foo[3].decode('utf-8')

    def get_pickled(self, var):
        file = open(str(self.shotid) + '_' + var + '.pk', 'rb')
        data = pickle.load(file)
        file.close()
        return data

    def does_shot_exist(self, shotid):
        return shotid == 130000

    def test(self):
        foo = mock_shot_data('nstx', 130000)
        current = foo.get_tree_data('\\ip')
        stored_energy = foo.get_tree_data('\\EFIT01::WMHD')
        nef = foo.get_tree_data('\\NEF')
        pef = foo.get_tree_data('\\PEF')
        tef = foo.get_tree_data('\\TEF')
        pdb.set_trace()

if __name__ == '__main__':
    foo = mock_shot_data('nstx', 130000)
    foo.test()
