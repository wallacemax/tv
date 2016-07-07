__author__ = 'maxwallace'
try:
    from MDSplus import *
except ImportError:
    raise

import pickle

class pickle_mds_data:  ### (1)
    def __init__(self, treename, shotid):
        self.treename = treename
        self.shotid = shotid

        self.tree = Tree(self.treename, self.shotid)

        print('connected to {} tree for shot {}'.format(treename, shotid))

    def get_tree_data(self, nodeid):
        mynode = self.tree.getNode(nodeid)
        data = mynode.record
        return data.data()

    def pickle_data(self, nodeid, var_name):
        fileName = var_name + '.pk'
        file = open(fileName, 'wb')
        foo = self.get_tree_data(nodeid)
        pickle.dump(foo, file)
        file.close()
        print('pickled {} into {}'.format(nodeid, fileName))

    def test(self):
        print('init')
        print('try getting *other* plasma current')
        self.pickle_data('\EFIT01::TOP.RESULTS.GEQDSK:CPASMA', 'CPLASMA')
        print('try getting stored energy')
        self.pickle_data('\EFIT01::TOP.RESULTS.AEQDSK:WMHD', 'WMHD')
        print('yay!')

if __name__ == '__main__':
    foo = pickle_mds_data('efit01', 130000)
    foo.test()