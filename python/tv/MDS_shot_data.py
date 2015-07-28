__author__ = 'maxwallace'
try:
    from MDSplus import *
except ImportError:
    raise

class MDS_shot_data:  ### (1)
    def __init__(self, treename, shotid):
        self.treename = treename
        self.shotid = shotid

        self.tree = Tree(self.treename, self.shotid)

    def get_tree_data(self, nodeid):
        mynode = self.tree.getNode(nodeid)
        data = mynode.record
        return data.data()

    def does_shot_exist(self, shotid):
        pass

    def test(self):
        print('init')
        foo = MDS_shot_data('nstx', 130000)
        print('try getting Ne')
        print(foo.get_tree_data('\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_NE'))
        print('try getting Pe')
        print(foo.get_tree_data('\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_PE'))
        print('try getting Te')
        print(foo.get_tree_data('\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_TE'))
        print('try switching to EFIT01 tree')
        foo = MDS_shot_data('EFIT01', 130000)
        print('try getting plasma current')
        print(foo.get_tree_data('\EFIT01::TOP.RESULTS.GEQDSK:CPASMA'))
        print('try getting stored energy')
        print(foo.get_tree_data('\EFIT01::TOP.RESULTS.AEQDSK:WMHD'))
        print('yay!')

if __name__ == '__main__':
    foo = MDS_shot_data('nstx', 130000)
    foo.test()