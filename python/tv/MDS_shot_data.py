__author__ = 'maxwallace'

import sys
sys.path.append("/usr/pppl/mdsplus/v5.0/mdsobjects")

try:
    import python as MDSplus
except ImportError:
    raise

import pdb
import pickle

class MDS_shot_data:  ### (1)
    def __init__(self, treename, shotid):
        self.treename = treename
        self.shotid = shotid

        self.tree = MDSplus.Tree(self.treename, self.shotid, 'Readonly')

    def get_1d_tree_data(self, nodeid):
        mynode = self.tree.getNode(nodeid)

        data = mynode.record

        return data.data()

    def get_tree_data(self, nodeid):
        mynode = self.tree.getNode(nodeid)

        data = mynode.getData()

        units = data.units

        signal = data.data()

        dim_signal = []
        dim_units = ''

        try:
            xAxis = data.dim_of()
            axis = xAxis.getAxis()
            dim_units = axis.units
            descs = axis.getDescs()
            xIncr = descs[2].value

            foo = 0.
            for i in range(len(signal)):
                foo = round(foo, 4)
                dim_signal.append(foo)
                foo += xIncr

        except:
            xIncr = -1
            dim_signal = data.dim_of().data()
            dim_units = data.dim_of().units

        return dim_signal, signal, str(units), str(dim_units)


    def does_shot_exist(self, shotid):
        pass

    def pickle_data(self, nodeid, var_name):
        fileName = var_name + '.pk'
        file = open(fileName, 'wb')
        foo = self.get_tree_data(nodeid)
        pickle.dump(foo, file)
        file.close()
        print('pickled {} into {}'.format(nodeid, fileName))

    def test(self):
        foo = MDS_shot_data('nstx', 130000)
        #bar = foo.get_timed_tree_data('\\ip')

        current = foo.get_tree_data('\\ip')
        stored_energy = foo.get_tree_data('\\WMHD')
        nef = foo.get_tree_data('\\NEF')
        pef = foo.get_tree_data('\\PEF')
        tef = foo.get_tree_data('\\TEF')
        pdb.set_trace()

if __name__ == '__main__':
    foo = MDS_shot_data('nstx', 130000)
    foo.test()