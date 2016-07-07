import sys
sys.path.append("/usr/pppl/mdsplus/v5.0/mdsobjects")
import python as MDSplus         # python is a sub-directory in mdsobjects 

shot = 139047

tree = MDSplus.Tree('nstx', shot, 'Readonly')   # MDSplus.tree.Tree

ipNode = tree.getNode('\\ip')                   # MDSplus.treenode.TreeNode
                                                # \\ip prints \ip

signal = ipNode.getData()               # MDSplus.compound.Signal
                                            # can also access by ipNode.record
print(signal.units)                      # MDSplus String type, not just str

a = signal.data()                       # numpy.ndarray

for i in range(len(a)):
        print(i, a[i])