from Dialog import Dialog
from Tkinter import *

class DataSourcesDialog(Dialog):
    def __init__(self, parent, pref, shotData):
        self.shotData = shotData
        self.preferences = pref
        self.entries = {}
        self.updatemsg = StringVar()
        self.updatemsg.set("Please select a data source or choose 'Custom' to add.")
        Dialog.__init__(self, parent, "MDS Data")

    def body(self, master):
        displayfont = {'family': 'Bitstream Vera Sans', 'size': self.preferences['font_size'][1]}
        #panelID not displayed, b/c we don't want the user to set it here
        datas = {'TDI': 'Tree Data Interface (from OMFIT)', 'tree': 'Tree Name', 'name': 'Trace Label',
                 'units': 'Units', 'scaling': 'Scaling Factor', 'label': 'Graph Label',
                 'x_label': 'X Dimension Label', 'y_label': 'Y Dimension Label'}


        #install dropdown
        self.dropdownkeys = [x['name'] for x in self.shotData.values()]

        self.selectedDataSource = StringVar(master)
        self.selectedDataSource.trace("w", self.loadDataSource)
        self.option = apply(OptionMenu, (master, self.selectedDataSource) + tuple(self.dropdownkeys))
        self.option.grid(row=0, column=0, columnspan=2)

        foo = 1
        for key in sorted(datas, key=datas.__getitem__):
            #okay, this is all weird now.
            # {'NEF': mdstd.MDSTraceData(panelID=1,
            #                            TDI='MPTS.OUTPUT_DATA.BEST.FIT_NE',
            #                            tree='ACTIVESPEC',
            #                            name='Electron Temperature',
            #                            units='keV',
            #                            scaling=-1,
            #                            label='Electron Temperature',
            #                            x_label='',
            #                            y_label='$n_e\;[10^{20}\;m^{-3}]$'),

            Label(master, text=datas[key], font=displayfont).grid(row=foo, column=0)
            e = Entry(master, font=displayfont, justify='center')
            e.grid(row=foo, column=1)
            #can't insert yet, don't have a data source picked
            #e.insert(END, self.shotData[key])
            self.entries[key] = e
            #TODO: tooltips?
            foo += 1

        l = Label(master, textvariable=self.updatemsg)
        l.grid(row=foo, column=0, sticky=NS, columnspan=2)

        #and refresh
        self.selectedDataSource.set(self.dropdownkeys[0])

    def loadDataSource(self, *args):
        thisData = [x for x in self.shotData.values() if x['name']==self.selectedDataSource.get()][0]
        #and fill
        for key in self.entries:
            self.entries[key].delete(0, END)
            self.entries[key].insert(END, thisData[key])

        self.updatemsg.set("Loaded {}".format(self.selectedDataSource.get()))
        pass

    def validate(self):
        pass

    def apply(self):
        pass