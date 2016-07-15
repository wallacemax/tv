__author__ = 'maxwallace'
import sys
import datetime
import os

# logfilename = '{}_Thomson.log'.format(datetime.datetime.isoformat(
#             datetime.datetime.today()).split('.')[0].replace('-', '').replace(':', ''))
# import logging
# logging.basicConfig(filename=logfilename, level=logging.ERROR)
# logger = logging.getLogger(__name__)

USE_MOCK_DATA = sys.platform == 'darwin'
if USE_MOCK_DATA:
    #running on macosx i.e., locally on a laptop, use mock
    import mock_shot_data as OMFITdata
    demoshotnumber = 205088
else:
    #running on the server, run full DAL
    import OMFIT_shot_data as OMFITdata
    demoshotnumber = 204062

try:
    # for Python2
    import Tkinter as tk
    # logger.debug('Using Tkinter for Python2')
except ImportError:
    # for Python3
    import tkinter as tk
    # logger.debug('Using tkinter for Python3')

import tkFont

import matplotlib
matplotlib.use('agg')
matplotlib.use('TkAgg')
from matplotlib.pyplot import *
import matplotlib.ticker as ticker

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from matplotlib.widgets import MultiCursor
from matplotlib.widgets import SpanSelector

import math

import pdb
import pickle

defaultdpi = 100
radialgraphwidth = 6.5
radialgraphratio = 1
timegraphwidth = 6
timegraphratio = 1
audittextsize=8

treename = 'nstx'
userid = os.getenv('LOGNAME')
userpath = '~/{}/'.format(userid)

include_csv = 0

plotfont = {'family': 'Bitstream Vera Sans', 'size': 12}
matplotlib.rc('font', **plotfont)

headerlogofilepath = "NSTX-U_logo_thick_font_transparent.gif"

import PreferencesDialog

class tvMain:
    def __init__(self, master):
        self.master = master

        self.update_text = tk.StringVar()
        self.update_text.set('Loading initial graphics.')

        self.loadPreferences()

        self.centerwindow(width=self.preferences['mainwindowwidth'][1], height=self.preferences['mainwindowheight'][1])

        self.selectedTimeIndex = -1

        self.InitUI()

        self.MDS_data_nodes = [['NEF', 'ACTIVESPEC', 'MPTS.OUTPUT_DATA.BEST.FIT_NE'],
                ['PEF', 'ACTIVESPEC', 'MPTS.OUTPUT_DATA.BEST.FIT_PE'],
                ['TEF', 'ACTIVESPEC', 'MPTS.OUTPUT_DATA.BEST.FIT_TE'],
                ['IP', 'WF', 'IP'],
                ['WMHD', 'EFIT01', 'RESULTS.AEQDSK.WMHD']
                ]

        self.MDS_data = {'NEF': Ellipsis,
                         'PEF': Ellipsis,
                         'TEF': Ellipsis,
                         'IP': Ellipsis,
                         'WMHD': Ellipsis}

        self.MDS_data_titles = {'NEF': 'Electron Density',
                                'PEF': 'Electron Pressure',
                                'TEF': 'Electron Temperature',
                                'IP': 'Plasma Current',
                                'WMHD': 'Stored Energy'}

        self.update_text.set('Please input shot number for visualization.')

    def centerwindow(self, width, height):
        # get screen width and height
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # calculate position x and y coordinates
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.master.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def InitUI(self):

        self.displayFont = tkFont.Font(family='Bitstream Vera Sans', size=int(self.preferences['font_size'][1]))

        self.drawShotHeader()

        self.drawFooter()

        self.txtShotNumber.focus_set()

    def drawShotHeader(self):
        # setup shot frame
        self.entryFrame = tk.Frame(self.master)
        self.entryFrame.grid(row=0, column=0, sticky=tk.NSEW)
        self.entryFrame.grid_rowconfigure(0, weight=1)

        self.lblShot = tk.Label(self.entryFrame, text='Shot Number:', font=self.displayFont)
        self.lblShot.grid(row=0, column=0, sticky=tk.NSEW)

        self.txtShotNumber = tk.Entry(self.entryFrame, width=12, fg='red', justify='center', font=self.displayFont)
        self.txtShotNumber.insert(0, demoshotnumber)
        self.txtShotNumber.bind("<Return>", lambda event: self.shotnumberInput())
        self.txtShotNumber.bind("b", lambda event: self.shotnumberInput())
        self.txtShotNumber.grid(row=0, column=1, sticky=tk.NSEW)

        self.headerLogo = tk.PhotoImage(file=headerlogofilepath)
        lblLogo = tk.Label(self.master, image=self.headerLogo)
        lblLogo.grid(row=0, column=1, sticky=tk.NSEW)

        self.update_text.set("Drew shot header.")

    def drawFooter(self):
        # footer

        self.exportFrame = tk.Frame(self.master)
        self.exportFrame.grid(row=3, column=0, sticky=tk.NSEW)
        self.exportFrame.grid_rowconfigure(0, weight=1)

        self.btnResetZoom = tk.Button(text="Reset Zoom",
                                      command=lambda:
                                      self.changeRadialRange(self.radialmachinexmin, self.radialmachinexmax),
                                      master=self.exportFrame,
                                      font=self.displayFont)

        self.btnResetZoom.grid(row=0, column=0, sticky=tk.NSEW)

        btnEPS = tk.Button(text="Print EPS", command=lambda: self.export_graphs(self.txtShotNumber.get(), 'EPS'),
                           master=self.exportFrame, font=self.displayFont)
        btnEPS.grid(row=0, column=1, sticky=tk.NSEW)
        btnPNG = tk.Button(text="Print PNG", command=lambda: self.export_graphs(self.txtShotNumber.get(), 'PNG'),
                           master=self.exportFrame, font=self.displayFont)
        btnPNG.grid(row=0, column=2, sticky=tk.NSEW)
        self.include_csv = tk.BooleanVar()
        self.chkCSV = tk.Checkbutton(text="Save CSV", variable=self.include_csv, master=self.exportFrame,
                                     font=self.displayFont)
        self.chkCSV.grid(row=0, column=3, sticky=tk.NSEW)

        self.lblOutput = tk.Label(self.master, textvariable=self.update_text, font=self.displayFont)
        self.lblOutput.grid(row=3, column=1, sticky=tk.NSEW)

        btnPreferences = tk.Button(text="Preferences...", command=lambda: self.showPreferences(),
                            font = self.displayFont)
        btnPreferences.grid(row=4, column=0, sticky=tk.NS + tk.E)

        self.update_text.set("Drew footer.")

    def createTimeGraphs(self):

        IP = self.MDS_data['IP']
        wmhd = self.MDS_data['WMHD']

        # bar = [time_signal, time_units, radial_signal, radial_units, signal, units]

        maxscale = np.amax([np.amax(IP[0]), np.amax(wmhd[0])])

        self.figure_a = Figure(figsize=(timegraphwidth,
                                        timegraphwidth * timegraphratio), dpi=defaultdpi, facecolor='white')
        self.ax_a = self.figure_a.add_subplot(2, 1, 1)
        self.ax_a.set_ylabel(IP[5])
        #TODO: revisit IP Y scaling when appropriate
        self.ax_a.set_ylim([0, 1])
        self.ax_a.set_xlim([0, maxscale])
        self.ax_a.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
        self.ax_a.set_title(self.MDS_data_titles['IP'])
        self.fig_a = self.ax_a.plot(IP[0], IP[4], marker='.', linestyle='None', markersize=12)

        self.ax_b = self.figure_a.add_subplot(2, 1, 2)
        self.ax_b.set_xlabel('Time [s]')
        self.ax_b.set_ylabel(wmhd[5])
        #self.ax_b.set_ylim([0, self.roundtohundred(np.amax(wmhd[4]))])
        self.ax_a.set_ylim([0, 1])
        self.ax_b.set_xlim([0, maxscale])
        self.ax_b.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2), )
        self.ax_b.set_title(self.MDS_data_titles['WMHD'])
        self.fig_b = self.ax_b.plot(wmhd[0], wmhd[4], marker='.', linestyle='None', markersize=12)

        self.figure_a.subplots_adjust(hspace=.7, bottom=0.13)

        self.canvas_a = FigureCanvasTkAgg(self.figure_a, master=self.master)

        self.multi = MultiCursor(self.canvas_a, (self.ax_a, self.ax_b), color='g', lw=2, horizOn=False, vertOn=True)

        self.canvas_a.mpl_connect('motion_notify_event', self.TimeGraphMove)
        self.canvas_a.mpl_connect('button_press_event', lambda event: self.canvas_a._tkcanvas.focus_set())

        self.canvas_a.show()
        self.canvas_a.get_tk_widget().grid(row=2, column=1, sticky=tk.E+tk.W+tk.N+tk.S)

    def TimeGraphMove(self, event):

        if event.xdata == None:
            return

        selected_time = event.xdata

        self.updateRadialGraphTime(selected_time)

    def updateTimeGraphKeypress(self, direction):
        if self.selectedTimeIndex == -1 or len(self.MDS_data['TEF'][0]) <= self.selectedTimeIndex + direction:
            selectedIndex = 0
        else:
            selectedIndex = self.selectedTimeIndex + direction

        self.updateRadialGraphTime(self.MDS_data['TEF'][0][selectedIndex])

    def createRadialGraphs(self, selected_time):

        # pdb.set_trace()

        self.figure_1 = Figure(figsize=(radialgraphwidth,
                                        radialgraphwidth * radialgraphratio), dpi=defaultdpi, facecolor='white')

        self.ax1 = self.figure_1.add_subplot(3, 1, 1)
        self.ax2 = self.figure_1.add_subplot(3, 1, 2)
        self.ax3 = self.figure_1.add_subplot(3, 1, 3)

        self.figure_1.subplots_adjust(hspace=.25)

        self.canvas_1 = FigureCanvasTkAgg(self.figure_1, master=self.master)

        self.span1 = SpanSelector(self.ax1, self.rangeOnSelect, 'horizontal', useblit=True,
                                  rectprops=dict(alpha=0.5, facecolor='red'))
        self.span2 = SpanSelector(self.ax2, self.rangeOnSelect, 'horizontal', useblit=True,
                                  rectprops=dict(alpha=0.5, facecolor='red'))
        self.span3 = SpanSelector(self.ax3, self.rangeOnSelect, 'horizontal', useblit=True,
                                  rectprops=dict(alpha=0.5, facecolor='red'))

        self.updateRadialGraphTime(selected_time)

        self.canvas_1.show()
        self.canvas_1.get_tk_widget().grid(row=2, column=0, sticky=tk.W + tk.E + tk.N + tk.S)

        self.update_text.set("Created radial plots.")

    def updateRadialGraphs(self, framenumber, time_difference = 0):

        self.framenumber = framenumber
        # logger.debug('Updating radial graphs for framenumber {} at time_difference {}'
        #              .format(framenumber, time_difference))
        ne = self.MDS_data['NEF']
        te = self.MDS_data['TEF']
        pe = self.MDS_data['PEF']

        # bar = [time_signal, time_units, radial_signal, radial_units, signal, units]

        selectedTime = '{0:.0f}'.format((ne[0][framenumber]+time_difference)*1000) + 'ms'
        self.displayedTime = '{0:.0f}'.format(ne[0][framenumber]*1000) + 'ms'
        displayedTimeDifference = '{0:.2f}'.format(time_difference*1000) + 'ms'
        self.figure_1.suptitle('$T_{TS}$' + ' = {}'.format(self.displayedTime) +
                               ', $\Delta T$={}'.format(displayedTimeDifference))
        #self.figure_1.suptitle('Data displayed for {}, {} different'
            # .format(displayedTime, displayedTimeDifference))  #3.1502ms

        self.ax1.clear()
        self.ax1.plot(ne[2], ne[4][:, framenumber], marker='.', linestyle='None', c='red', markersize=12)
        self.ax1.set_title(self.MDS_data_titles['NEF'])
        setp(self.ax1.get_xticklabels(), visible=False)
        self.ax1.set_ylabel(ne[5])

        self.ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: ('%.2f') % (x * 1e-20)))

        self.ax2.clear()
        self.ax2.plot(te[2], te[4][:, framenumber], marker='s', linestyle='None', c='blue', markersize=12)
        self.ax2.set_title(self.MDS_data_titles['TEF'])
        setp(self.ax2.get_xticklabels(), visible=False)
        self.ax2.set_ylabel(te[5])

        self.ax3.clear()
        self.ax3.plot(pe[2], pe[4][:, framenumber], marker='^', linestyle='None', c='green', markersize=12)
        self.ax3.set_title(self.MDS_data_titles['PEF'])
        self.ax3.set_ylabel(pe[5])

        self.ax3.set_xlabel("Radius (cm)")

        self.changeRadialRange(self.preferences['radialgraphxmin'][1], self.preferences['radialgraphxmax'][1])

        self.canvas_1.draw()

    def updateRadialGraphTime(self, selected_time):
        try:
            self.selectedTimeIndex = self.find_idx_nearest_value(self.MDS_data['TEF'][0], selected_time)

            # bar = [time_signal, time_units, radial_signal, radial_units, signal, units]
            # MPL MouseEvent: xy=(456,424) xydata=(0.796994851319,0.273058346212) button=None dblclick=False inaxes=Axes(0.125,0.614815;0.775x0.285185)
            nearest_frame = self.find_idx_nearest_value(self.MDS_data['NEF'][0], selected_time)
            nearest_time = self.MDS_data['NEF'][0][nearest_frame]
            timedelta = nearest_time - selected_time

            self.selectedTimeIndex = nearest_frame

            self.updateRadialGraphs(nearest_frame, timedelta)
            pass
        except Exception as e:
            self.update_text.set("An error was generated, and has been written to the log.")
            # logger.error(e.message)
            # logger.error(e.__doc__)

        self.update_text.set("Displayed closest Thomson data to {0:.2f}ms.".format(selected_time * 1000))

    def changeRadialRange(self, graphxmin, graphxmax):

        self.preferences['radialgraphxmin'][1], self.preferences['radialgraphxmax'][1] = \
            graphxmin, graphxmax
        self.savePreferences()

        self.ax1.set_xlim(graphxmin, graphxmax)
        self.ax2.set_xlim(graphxmin, graphxmax)
        self.ax3.set_xlim(graphxmin, graphxmax)
        self.radialgraphxmin, self.radialgraphxmax = graphxmin, graphxmax
        self.canvas_1.draw()

    def rangeOnSelect(self, xmin, xmax):

        rr = self.MDS_data['RR']
        indmin, indmax = np.searchsorted(rr, (xmin, xmax))
        indmax = min(self.radialgraphxmax, indmax)

        thisx = rr[indmin:indmax]

        self.radialgraphxmin, self.radialgraphxmax = thisx[0], thisx[-1]

        self.update_text.set("Redrew radial plot boundaries.")

        self.changeRadialRange(self.radialgraphxmin, self.radialgraphxmax)

    def shotnumberInput(self):

        try:
            self.txtShotNumber['fg'] = 'green'
            self.shotnumber = self.txtShotNumber.get()
            if self.shotnumber == '':
                pass

            self.get_data_object(self.shotnumber)

            if not self.data.does_shot_exist(self.shotnumber):
                self.update_text.set("Data traces not available in MDS for {}.".format(self.shotnumber))
                return

            self.update_text.set('Querying {} tree for {}'.format(treename, str(self.shotnumber)))

            self.load_data(self.shotnumber)

            self.populateGraphs(self.shotnumber)

            self.update_text.set('Shot number {} loaded from tree.'.format(str(self.shotnumber)))
        except Exception as e:
            self.txtShotNumber['fg'] = "red"
            print(e)
            self.update_text.set("An error has occurred, and has been written to the log.")
            # logger.error(e.message)
            # logger.error(e.__doc__)

    def radialGraphCursor_moved(self):
        pass

    def roundtohundred(self, x):
        return int(math.ceil(x / 100.0)) * 100

    def find_idx_nearest_value(self, target, val):
        idx = (np.abs(target-val)).argmin()
        return idx

    def get_graph_data(self, datacaption, framenumber):
        key = ''
        for item in self.MDS_data_titles.items():
            if item[1] == datacaption:
                key = item[0]
                break

        return self.MDS_data[key][1][framenumber]

    def populateGraphs(self, shotnumber):
        self.createTimeGraphs()

        #bar = [time_signal, time_units, radial_signal, radial_units, signal, units]
        maxindex = np.argmax(self.MDS_data['IP'][4])
        max_ip_time = np.float64(self.MDS_data['IP'][0][maxindex])
        self.selectedTimeIndex = maxindex

        self.createRadialGraphs(max_ip_time)

        #TODO: set multi xdata location to max_ip_time

    def getData(self, treename, requestedTDI):
        return self.data.get_tree_data('nstx', treename, requestedTDI)

    def get_data_object(self, shotnumber):
        if USE_MOCK_DATA:
            self.data = OMFITdata.mock_shot_data(shotnumber)
        else:
            self.data = OMFITdata.OMFIT_shot_data(shotnumber)

    def load_data(self, shotnumber):

        for foo in self.MDS_data_nodes:
            self.MDS_data[foo[0]] = self.getData(foo[1], foo[2])
            self.update_text.set('Retrieved data for {}'.format(foo[0]))

        self.update_text.set('Data loaded from tree for {}'.format(shotnumber))

        self.tamper_with_data()

    def tamper_with_data(self):
        # look.  we all do things we aren't proud of.
        # the MDS tree is incorrect/inconsistant for units.  we, um, 'adjust' things here.

        #TODO: fix this for new data formats

        #bar = [time_signal, time_units, radial_signal, radial_units, signal, units]
        #determine dimensions of machine from data set
        self.MDS_data['RR'] = self.MDS_data['TEF'][2]

        #cut data before first Thomson value and after last Thomson value - the rest of any other signal is unimportant
        lastThomsonTime = np.amax(self.MDS_data['PEF'][0])
        for l in [self.MDS_data['IP'], self.MDS_data['WMHD']]:
            firstThomsonIndex = self.find_idx_nearest_value(l[0], 0)
            lastThomsonIndex = self.find_idx_nearest_value(l[0], lastThomsonTime) + 1
            for foo in [0,4]:
                l[foo] = l[foo][firstThomsonIndex:lastThomsonIndex]

        #TODO: change max to amax
        self.radialgraphxmax = self.MDS_data['NEF'][2].max()
        self.radialgraphxmin = self.MDS_data['NEF'][2].min()

        self.radialmachinexmin = self.radialgraphxmin
        self.radialmachinexmax = self.radialgraphxmax


        #change those labels
        #TODO: put IP in MA
        self.MDS_data['IP'][4] = [x/1e3 for x in self.MDS_data['IP'][4]]
        self.MDS_data['IP'][5] = '$I_P\;[MA]$'

        #TODO: put NEF in m^-3 from cm^-3
        self.MDS_data['NEF'][4] = \
            np.array([[x*1e6 for x in density] for density in \
             [[radial for radial in timestamp] for timestamp in self.MDS_data['NEF'][4]]]
                     )
        self.MDS_data['NEF'][5] = '$n_e\;[10^{20} m^{-3}]$'
        self.MDS_data['TEF'][5] = '$T_e\;[kEV]$'
        self.MDS_data['PEF'][5] = '$P_e\;[kPa]$'

        #WMHD J to kJ
        self.MDS_data['WMHD'][4] = [x/1e3 for x in self.MDS_data['WMHD'][4]]
        self.MDS_data['WMHD'][5] = '$W_{MHD}\;[kJ]$'

        # TODO: be clever and do in sigfigs
        #IP A to kA
        #self.MDS_data['IP'][4] = [x / 1000 for x in self.MDS_data['IP'][4]]
        #self.MDS_data['IP'][5] = 'kA'

        updatestring = 'Massaged MDS data.'
        self.update_text.set(updatestring)

    def export_graphs(self, shotid, file_type):
        # foo = "export {} {}, include CSV: {} ".format(str(shotid), file_type, str(include_csv))
        # print(foo)
        shotnumber = str(shotid)

        # YYYYMMDDTHH24MMSS
        timestamp = datetime.datetime.isoformat(
            datetime.datetime.today()).split('.')[0].replace('-', '').replace(':', '')

        bar = ''
        if self.include_csv.get():
            bar = (file_type + ' and CSV')
        else:
            bar = file_type

        updatestring = 'Images for {} saved in {} format'.format(shotid, bar)


        baz = ['figure_a', 'figure_1']

        for graphName in baz:
            graph = getattr(self, graphName)

            self.add_graph_thumbprint(graph)

            graphTitle = ''
            if '_1' in graphName:
                graphTitle = 'ThomsonData'
            else:
                graphTitle = 'TimeData'

            fileName = self.export_graph_image(file_type, graph, graphTitle, self.displayedTime, shotnumber, timestamp)

            if self.include_csv.get():
                self.export_csv_data(fileName, file_type, graph, graphTitle)

        self.update_text.set(updatestring)

    def export_graph_image(self, file_type, graph, graphTitle, graphtime, shotnumber, timestamp):
        directoryname = '~/{}/'.format(userid)

        #Shotnumber_yyyymmdd_hh24mmss_0798ms.ext
        fileName = '{}_{}_{}_{}.{}'.format(shotnumber, timestamp, graphTitle, graphtime, file_type).replace(' ', '')

        filetosave = fileName if not os.path.exists(directoryname) else directoryname + fileName

        graph.savefig(filetosave, dpi=defaultdpi, format=file_type, bbox_inches='tight', frameon=None)
        return filetosave

    def add_graph_thumbprint(self, graph):

        thumbprinttext = userid + ' ' + self.txtShotNumber.get()

        graph.text(.95,.85, thumbprinttext,
                   horizontalalignment='right',
                   verticalalignment='center',
                   rotation='vertical',
                   transform=graph.transFigure,
                   fontsize=audittextsize)

    def export_csv_data(self, fileName, file_type, graph, graphTitle):
        if graphTitle == 'ThomsonData':
            self.export_thomson_csv_data(fileName, file_type)
        else:
            self.export_time_csv_data(fileName, file_type, graph)

    def export_time_csv_data(self, fileName, file_type, graph):
        line = graph.gca().get_lines()[0].get_xydata()
        np.savetxt(fileName.replace(file_type, 'csv'), line, delimiter=',')

    def export_thomson_csv_data(self, fileName, file_type):
        for i in range(1, 4):
            sub = getattr(self, 'ax' + str(i))
            datacaption = sub.get_title()
            graphdata = self.get_graph_data(datacaption, self.framenumber)

            np.savetxt(fileName.replace('ThomsonData', datacaption)
                       .replace(file_type, 'csv'), graphdata, delimiter=',')

    def showPreferences(self):
        d = PreferencesDialog.PreferencesDialog(self.master, self.preferences)
        #after form
        for key, value in d.preferences.iteritems():
            self.preferences[key] = d.preferences[key]

        d.destroy()

        self.preferences['mainwindowwidth'] = ['', self.master.winfo_width()]
        self.preferences['mainwindowheight'] = ['', self.master.winfo_height()]

        self.savePreferences()

        self.update_text.set("Updated preferences.")

    def savePreferences(self):
        with open(self.getPreferencesFileName(), 'wb') as f:
            pickle.dump(self.preferences, f, pickle.HIGHEST_PROTOCOL)

    def getPreferencesFileName(self):
        preffilename = '{}.pref'.format(userid)

        #are we on the cluster?  if so, look in *their* directory
        if os.path.exists(userpath + preffilename):
            preffilename = userpath + preffilename

        return preffilename

    def loadPreferences(self):

        try:
            with open(self.getPreferencesFileName(), 'rb') as f:
                self.preferences = pickle.load(f)
                self.update_text.set('Loaded preferences.')
        except IOError:
            self.createDefaultPreferences()

    def createDefaultPreferences(self):
        prefs = {'font_size':['Font Size', 16],
            'radialgraphxmin':['', 0],
            'radialgraphxmax':['', 180],
            '1ylabelmin':['n_e Minimum', 0],
            '1ylabelmax':['n_e Maximum', -1],
            '2ylabelmin':['T_e Minimum', 0],
            '2ylabelmax':['T_e Maximum', -1],
            '3ylabelmin':['P_e Minimum', 0],
            '3ylabelmax':['P_e Maximum', -1],
            'mainwindowheight':['', 760],
            'mainwindowwidth':['', 1268]}

        self.preferences = prefs

        self.savePreferences()

        self.update_text.set('Created default preferences.')