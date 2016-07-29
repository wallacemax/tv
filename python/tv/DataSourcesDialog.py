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

        self.frame = master

        displayfont = {'family': 'Bitstream Vera Sans', 'size': self.preferences['font_size'][1]}
        datas = {'panelID': 'panelID', 'tdi': 'Tree Data Interface (from OMFIT)', 'tree': 'Tree Name', 'name': 'Trace Name',
                 'units': 'Units', 'scaling': 'Scaling Factor', 'label': 'Graph Label',
                 'x_label': 'X Dimension Label', 'y_label': 'Y Dimension Label'}

        #install data source dropdown
        self.dropdownkeys = [x['name'] for x in self.shotData.values()]

        self.selectedDataSource = StringVar(self.frame)
        self.selectedDataSource.trace("w", self.loadDataSource)

        self.optionstate = StringVar(self.frame)
        self.optionstate.set('normal')
        self.option = apply(OptionMenu, (self.frame, self.selectedDataSource) + tuple(self.dropdownkeys))
        self.option.state = self.optionstate
        self.option.grid(row=0, column=0)

        self.addbuttontext = StringVar(self.frame)
        self.addbuttontext.set('Add...')
        self.addsource = Button(textvariable=self.addbuttontext,
                                      command=self.addButtonClicked,
                                      master=self.frame,
                                      font=displayfont)
        self.addsource.grid(row=0, column=1)

        numberofrows = 1
        for key in sorted(datas, key=datas.__getitem__):
            #so here we'll do panelID
            if key == 'panelID':
                continue
            Label(self.frame, text=datas[key], font=displayfont).grid(row=numberofrows, column=0)
            e = Entry(self.frame, font=displayfont, justify='center')
            e.grid(row=numberofrows, column=1)
            self.entries[key] = e
            #TODO: tooltips?
            numberofrows += 1

        Label(self.frame, text='Display in Panel', font=displayfont).grid(row=numberofrows, column=0)
        self.panelDisplayKeys = {'': 0, 'top': 4, 'bottom': 5}
        self.selectedPanelSource = StringVar(self.frame)
        self.selectedPanelSource.set('')

        self.panelstate = StringVar(self.frame)
        self.panelstate.set('normal')
        self.panelOption = apply(OptionMenu, (self.frame, self.selectedPanelSource) + tuple(self.panelDisplayKeys))
        self.panelOption.state = self.panelstate
        self.panelOption.grid(row=numberofrows, column=1)
        numberofrows += 1

        self.previewButton = Button(self.frame, font=displayfont, command=self.loadPreview, text='Preview Data')
        self.previewButton.grid(row=numberofrows, column=0, sticky=NSEW, columnspan=2)

        l = Label(self.frame, textvariable=self.updatemsg)
        l.grid(row=numberofrows+1, column=0, sticky=NSEW, columnspan=2)

        self.numberofrows = numberofrows+1

        #and refresh
        self.selectedDataSource.set(self.dropdownkeys[0])

    def loadDataSource(self, *args):

        thisData = [x for x in self.shotData.values() if x['name'] == self.selectedDataSource.get()][0]

        #and fill
        for key in self.entries:
            self.entries[key].delete(0, END)
            self.entries[key].insert(END, thisData[key])

        if thisData['panelID'] in [4, 5]:
            self.selectedPanelSource.set([key for key, val in
                                          self.panelDisplayKeys.items() if val == thisData['panelID']][0])
        else:
            self.selectedPanelSource.set('')

        self.updatemsg.set("Loaded {}".format(self.selectedDataSource.get()))

    def loadPreview(self):
        # pull preview data, if ready

        if (len(self.entries['tdi'].get()) == 0) and (len(self.entries['tree'].get()) == 0):
            return

        try:
            if self.omfitdata.shotid is None:
                self.omfitdata.shotid = '204062'
            MDSTracePreview = self.omfitdata.get_tree_data('nstx',
                                                           self.entries['tree'].get(), self.entries['tdi'].get())
            # bar = [time_signal, time_units, radial_signal, radial_units, signal, units]
            if not MDSTracePreview[2] is None:
                self.updatemsg.set("{} is not a time-based signal.".format(self.entries['label'].get()))
                return

            xdata = MDSTracePreview[0]
            maxscale = np.amax(xdata)
            # adjust
            scalingfactor = pow(10, int(self.entries['scaling'].get().lower().replace('1e', '')))
            ydata = [x * scalingfactor for x in MDSTracePreview[4]]

            # TODO: refactor and push this out to a generator
            self.figure_prev = Figure(figsize=(6,
                                               6), dpi=100, facecolor='white')

            self.ax_prev = self.figure_prev.add_subplot(2, 1, 1)

            self.ax_prev.set_xlabel(self.entries['x_label'].get())
            self.ax_prev.set_ylabel(self.entries['y_label'].get())

            self.ax_prev.set_xlim([0, maxscale])
            self.ax_prev.set_ylim([0, 1])

            self.ax_prev.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
            self.ax_prev.set_title(self.entries['label'].get())
            self.fig_prev = self.ax_prev.plot(xdata, ydata,
                                              marker='.', linestyle='None', markersize=12)

            self.canvas_prev = FigureCanvasTkAgg(self.figure_prev, master=self.frame)

            self.canvas_prev.show()
            self.canvas_prev.get_tk_widget().grid(row=1, column=2, sticky=NSEW, rowspan=self.numberofrows)

        except Exception as e:
            self.updatemsg.set('Unable to preview.  Please check TDI and tree name.')

    def validate(self):
        ret = False
        msg = ''

        # so let's at least see if this hot garbage is named
        msg = 'Please check that this signal is named.'
        ret = (len(self.entries['name'].get()) > 0) or (self.addbuttontext.get() == 'Add...')

        #scaling factors all over 0
        msg = 'Please check that the scaling factor is > 0'
        ret = eval(self.entries['scaling'].get()) > 0

        #y axis labeled
        msg = 'Please check that a Y axis label is specified.'
        ret = self.entries['y_label'].get() != ''

        #there's a problem here in that the sources update individually, so a customer may be able to set
        #two panels for the same position.  i don't wanna fix it right now.

        if not ret:
            self.updatemsg.set(msg)

        return ret

    def apply(self):
        thisData = [x for x in self.shotData.values() if x['name'] == self.selectedDataSource.get()][0]
        for key, e in self.entries.iteritems():
            thisData.prop[key] = e.get()

        thisData.prop['panelID'] = self.panelDisplayKeys[self.selectedPanelSource.get()]

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
                    newdata = mdst.MDSTrace(self.selectedPanelSource.get(), '', '', '', '', '', '', '', '')
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