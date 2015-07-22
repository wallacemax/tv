__author__ = 'maxwallace'
import pickle

class mock_shot_data:  ### (1)
    def __init__(self, treename, shotid):
        self.treename = treename
        self.shotid = shotid

    def get_tree_data(self, nodeid):
        return self.get_pickled(str(nodeid[-2:]).lower() + '_fit')
        pass

    def get_pickled(self, var):
        file = open(var + '.pk', 'rb')
        data = pickle.load(file)
        file.close()
        return data

    def test(self):
        print('init')
        foo = mock_shot_data('nstx', 130000)
        print('try getting Ne')
        print(foo.get_tree_data('\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_NE'))
        print('try getting Pe')
        print(foo.get_tree_data('\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_PE'))
        print('try getting Te')
        print(foo.get_tree_data('\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_TE'))

if __name__ == '__main__':
    foo = mock_shot_data('nstx', 130000)
    foo.test()
