from Dialog import Dialog
from Tkinter import *
import MDSTrace as mdst
import uuid

import matplotlib as mpl
import matplotlib.pyplot as py
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import numpy as np

class DataSourcesDialog(Dialog):
    def __init__(self, parent, pref, shotData, omfitdata):
        self.shotData = shotData
        self.omfitdata = omfitdata
        self.preferences = pref
        self.entries = {}
        self.updatemsg = StringVar()
        self.updatemsg.set("Please select a data source or choose 'Custom' to add.")
        Dialog.__init__(self, parent, "MDS Data")

    def body(self, master):
        displayfont = {'family': 'Bitstream Vera Sans', 'size': self.preferences['font_size'][1]}
        #panelID not displayed, b/c we don't want the user to set it here
        datas = {'tdi': 'Tree Data Interface (from OMFIT)', 'tree': 'Tree Name', 'name': 'Trace Name',
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

        numberofrows = 1
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

            Label(master, text=datas[key], font=displayfont).grid(row=numberofrows, column=0)
            e = Entry(master, font=displayfont, justify='center')
            e.grid(row=numberofrows, column=1)
            #can't insert yet, don't have a data source picked
            #e.insert(END, self.shotData[key])
            self.entries[key] = e
            #TODO: tooltips?
            numberofrows += 1

        l = Label(master, textvariable=self.updatemsg)
        l.grid(row=numberofrows, column=0, sticky=NS, columnspan=2)

        self.numberofrows = numberofrows

        #set update event for preview pane
        #self.entries['tdi'].trace("w", self.loadPreview)
        #self.entries['tree'].trace("w", self.loadPreview)

        #and refresh
        self.selectedDataSource.set(self.dropdownkeys[0])

    def loadPreview(self):
        #pull preview data, if ready

        if not (len(self.entries['tdi'].get()) > 0) and (len(self.entries['tree'].get()) > 0):
            pass

        try:
            if self.omfitdata.shotid is None:
                self.omfitdata.shotid = '204062'
            MDSTracePreview = self.omfitdata.get_tree_data('nstx', self.entries['tree'].get(), self.entries['TDI'].get())

            #TODO: refactor and push this out to a generator
            self.figure_prev = Figure(figsize=(6,
                                               6), dpi=100, facecolor='white')

            self.ax_prev = self.figure_prev.add_subplot(2, 1, 1)
            self.ax_prev.set_ylabel(self.entries['y_label'].get())

            self.ax_prev.set_ylim([0, np.amax(MDSTracePreview[4])])
            self.ax_prev.set_xlim([0, np.amax(MDSTracePreview[0])])
            self.ax_prev.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
            self.ax_prev.set_title(self.entries['x_label'].get())
            self.fig_prev = self.ax_prev.plot(MDSTracePreview[0], MDSTracePreview[4],
                                              marker='.', linestyle='None', markersize=12)

            self.canvas_prev = FigureCanvasTkAgg(self.figure_prev, master=self.master)

            self.canvas_prev.show()
            self.canvas_prev.get_tk_widget().grid(row=1, column=2, sticky=NSEW, columnspan=self.numberofrows)
        except Exception as e:
            self.updatemsg.set('Unable to preview.  Please check TDI and tree name.')


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