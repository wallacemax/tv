__author__ = 'maxwallace'
try:
    from MDSplus import *
except ImportError:
    NO_MDS_TREE = True

class MDS_shot_data:  ### (1)
    def __init__(self, treename, shotid):
        self.treename = treename
        self.shotid = shotid

        self.tree = Tree(self.treename, self.shotid)

    def get_tree_data(self, nodeid):
        mynode = self.tree.getNode(nodeid)
        data = mynode.record
        return data.data()

    def test(self):
        print('init')
        foo = MDS_shot_data('nstx', 130000)
        print('try getting Ne')
        print(foo.get_tree_data('\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_NE'))
        print('try getting Pe')
        print(foo.get_tree_data('\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_PE'))
        print('try getting Te')
        print(foo.get_tree_data('\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_TE'))

if __name__ == '__main__':
    foo = MDS_shot_data('nstx', 130000)
    foo.test()