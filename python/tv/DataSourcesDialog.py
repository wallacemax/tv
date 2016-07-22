from Dialog import Dialog
from Tkinter import *
import MDSTrace as mdst
import uuid

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
        datas = {'TDI': 'Tree Data Interface (from OMFIT)', 'tree': 'Tree Name', 'name': 'Trace Name',
                 'units': 'Units', 'scaling': 'Scaling Factor', 'label': 'Graph Label',
                 'x_label': 'X Dimension Label', 'y_label': 'Y Dimension Label'}

        #install dropdown
        self.dropdownkeys = [x['name'] for x in self.shotData.values()]

        self.selectedDataSource = StringVar(master)
        self.selectedDataSource.trace("w", self.loadDataSource)

        self.optionstate = StringVar(master)
        self.optionstate.set('normal')
        self.option = apply(OptionMenu, (master, self.selectedDataSource) + tuple(self.dropdownkeys))
        self.option.state = self.optionstate
        self.option.grid(row=0, column=0)

        self.addbuttontext = StringVar(master)
        self.addbuttontext.set('Add...')
        self.addsource = Button(textvariable=self.addbuttontext,
                                      command=self.addButtonClicked,
                                      master=master,
                                      font=displayfont)
        self.addsource.grid(row=0, column=1)

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
        #well, no required values, ergo, no validation.  wild.
        # so let's at least see if this hot garbage is named
        return (len(self.entries['name'].get()) > 0) or (self.addbuttontext.get() == 'Add...')

    def apply(self):
        thisData = [x for x in self.shotData.values() if x['name'] == self.selectedDataSource.get()][0]
        for key, e in self.entries.iteritems():
            thisData.prop[key] = e.get()

    def refreshOption(self):
        self.dropdownkeys = [x['name'] for x in self.shotData.values()]
        # Reset var and delete all old options
        self.option['menu'].delete(0, 'end')

        # Insert list of new options (tk._setit hooks them up to var)
        for key in self.dropdownkeys:
            self.option['menu'].add_command(label=key, command=lambda v=key: self.selectedDataSource.set(v))

        self.selectedDataSource.set(self.dropdownkeys[0])

    def addButtonClicked(self):
        if self.addbuttontext.get() == 'Add...':
            for key, e in self.entries.iteritems():
                e.delete(0, END)
            self.optionstate.set('disabled')
            self.addbuttontext.set('Save Changes')
            self.updatemsg.set('Adding new data source.')
        else:
            try:

                #do a save routine here
                if self.validate():
                    newdata = mdst.MDSTrace(-1, '', '', '', '', '', '', '', '')
                    for key, e in self.entries.iteritems():
                        newdata[key] = e.get()
                    self.shotData[uuid.uuid4().get_hex()] = newdata
                    self.addbuttontext.set('Add...')
                    self.optionstate.set('normal')
                    self.updatemsg.set('Created data source {}'.format(newdata['name']))
                    self.refreshOption()
                else:
                    self.updatemsg.set('Unable to create data source, please check inputs.')
            except Exception as e:
                self.updatemsg.set('Unable to create new data source.')