
__author__ = 'maxwallace'
import sys
import datetime
import os

logfilename = '{}_Thomson.log'.format(datetime.datetime.isoformat(
            datetime.datetime.today()).split('.')[0].replace('-', '').replace(':', ''))
import logging
logging.basicConfig(filename=logfilename, level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # for Python2
    import Tkinter as tk
    logger.debug('Using Tkinter for Python2')
except ImportError:
    # for Python3
    import tkinter as tk
    logger.debug('Using tkinter for Python3')

import matplotlib
matplotlib.use('agg')
matplotlib.use('TkAgg')
from pylab import *

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
USE_MDS_DATA = True

try:
    import MDS_shot_data as mdsdata
except ImportError:
    USE_MDS_DATA = False
    import mock_shot_data as mockdata

import ctypes

from matplotlib.widgets import MultiCursor
from matplotlib.widgets import SpanSelector

defaultdpi = 100
radialgraphwidth = 6.5
radialgraphratio = 1
timegraphwidth = 6
timegraphratio = 1
audittextsize=6

treename = 'nstx'
userid = os.getenv('LOGNAME')

include_csv = 0

plotfont = {'family': 'Bitstream Vera Sans', 'size': 12}
matplotlib.rc('font', **plotfont)

headerlogofilepath = "NSTX-U_logo_thick_font_transparent.gif"

class tvMain:
    def __init__(self, master):
        self.master = master

        self.update_text = tk.StringVar()
        self.update_text.set('Loading initial graphics.')

        self.InitUI()

        self.MDS_data_nodes = {'FIT_NE': '\\NEF',
                               'FIT_PE': '\\PEF',
                               'FIT_TE': '\\TEF',
                               'CPLASMA': '\\IP',
                               'WMHD': '\\EFIT01::WMHD'}

        self.MDS_data = {'FIT_NE': Ellipsis,
                         'FIT_PE': Ellipsis,
                         'FIT_TE': Ellipsis,
                         'CPLASMA': Ellipsis,
                         'WMHD': Ellipsis}

        self.MDS_data_titles = {'FIT_NE': 'Density (Ne)',
                                'FIT_PE': 'Pressure (Pe)',
                                'FIT_TE': 'Temperature (Te)',
                                'CPLASMA': 'Plasma Current',
                                'WMHD': 'Stored Energy'}

        self.update_text.set('Please input shot number for visualization.')

    def InitUI(self):
        self.drawShotHeader()

        self.drawFooter()

    def drawFooter(self):
        # footer
        btnEPS = tk.Button(text="Print EPS", command=lambda: self.export_graphs(self.txtShotNumber.get(), 'EPS'))
        btnEPS.grid(row=3, column=0, sticky=tk.W)
        btnPNG = tk.Button(text="Print PNG", command=lambda: self.export_graphs(self.txtShotNumber.get(), 'PNG'))
        btnPNG.grid(row=3, column=0)
        self.include_csv = tk.BooleanVar()
        self.chkCSV = tk.Checkbutton(text="Save CSV", variable=self.include_csv)
        self.chkCSV.grid(row=3, column=0, sticky=tk.E)

        self.lblOutput = tk.Label(textvariable=self.update_text)
        self.lblOutput.grid(row=3, column=1)

    def drawShotHeader(self):
        # setup shot frame
        self.entryFrame = tk.Frame(self.master)
        self.entryFrame.grid(row=0, column=0, sticky=tk.W)

        self.lblShot = tk.Label(self.entryFrame, text='Shot Number:')
        self.lblShot.pack(side=tk.LEFT)

        self.txtShotNumber = tk.Entry(self.entryFrame, width=12)
        self.txtShotNumber.insert(0, "130000")
        self.txtShotNumber.pack(side=tk.LEFT)
        self.playLogo = tk.PhotoImage(file="play.gif")
        self.btnShot = tk.Button(self.entryFrame, image=self.playLogo, command=self.shotnumberInput)
        self.btnShot.pack(side=tk.LEFT)

        # lblTime = tk.Label(text=strftime('%H:%M:%S'), background='white')
        # lblTime.grid(row=0, column=0)
        # lblUserID = tk.Label(text=userid, background='white')
        # lblUserID.grid(row=0, column=0, sticky=tk.E)

        self.headerLogo = tk.PhotoImage(file=headerlogofilepath)
        lblLogo = tk.Label(image=self.headerLogo)
        lblLogo.grid(row=0, column=1)

    def updateRadialGraphs(self, framenumber, time_difference = 0):
        self.framenumber = framenumber
        logger.debug('Updating radial graphs for framenumber {} at time_difference {}'
                     .format(framenumber, time_difference))
        ne = self.MDS_data['FIT_NE']
        te = self.MDS_data['FIT_TE']
        pe = self.MDS_data['FIT_PE']
        rr = self.MDS_data['RR']

        displayedTime = '{0:.2f}'.format(ne[0][framenumber]*1000) + 'ms'
        displayedTimeDifference = '{0:.2f}'.format(time_difference) + 'ms'
        self.figure_1.suptitle('Thomson data at {}, {} different'.format(displayedTime, displayedTimeDifference))  #3.1502ms

        self.ax1.clear()
        self.ax1.plot(rr, ne[1][framenumber], marker='.', linestyle='None', c='red')
        self.ax1.set_title(self.MDS_data_titles['FIT_NE'])
        setp(self.ax1.get_xticklabels(), visible=False)
        self.ax1.set_ylabel(ne[2])

        self.ax2.clear()
        self.ax2.plot(rr, te[1][framenumber], marker='s', linestyle='None', c='blue')
        self.ax2.set_title(self.MDS_data_titles['FIT_TE'])
        setp(self.ax2.get_xticklabels(), visible=False)
        self.ax2.set_ylabel(te[2])

        self.ax3.clear()
        self.ax3.plot(rr, pe[1][framenumber], marker='^', linestyle='None', c='green')
        self.ax3.set_title(self.MDS_data_titles['FIT_PE'])
        self.ax3.set_xlabel(pe[3])
        self.ax3.set_ylabel(pe[2])

        self.canvas_1.draw()


    def createRadialGraphs(self, selected_time):
        logger.debug('Creating radial graphs for {}'.format(selected_time))

        radialFrame = tk.Frame(self.master)
        radialFrame.grid(row=2, column=0)

        rr = self.MDS_data['RR']

        # return dim_signal, signal, str(units), str(dim_units)
        #           X          Y        Yunit       Xunit

        self.figure_1 = plt.figure(figsize=(radialgraphwidth,
                                            radialgraphwidth * radialgraphratio),
                                   dpi=defaultdpi,
                                   facecolor='white')

        self.figure_1.add_axes()

        self.figure_1.add_subplot(311)
        self.ax1 = plt.subplot(3, 1, 1)
        self.ax2 = plt.subplot(3, 1, 2)
        self.ax3 = plt.subplot(3, 1, 3)

        self.span = SpanSelector(self.ax3, self.updateRadialGraphBounds, 'horizontal', span_stays=True)

        self.figure_1.subplots_adjust(hspace=.25)

        self.canvas_1 = FigureCanvasTkAgg(self.figure_1, master=radialFrame)

        self.canvas_1.show()
        self.canvas_1.get_tk_widget().grid(row=0, column=0)

        self.updateRadialGraphTime(selected_time)

    def updateRadialGraphBounds(self, vmin, vmax):
        print('min {} max {}'.format(vmin, vmax))

    def updateRadialGraphTime(self, selected_time):
        try:
            # MPL MouseEvent: xy=(456,424) xydata=(0.796994851319,0.273058346212) button=None dblclick=False inaxes=Axes(0.125,0.614815;0.775x0.285185)
            nearest_frame = self.find_idx_nearest_value(self.MDS_data['FIT_NE'][0], selected_time)
            nearest_time = self.MDS_data['FIT_NE'][0][nearest_frame]
            timedelta = nearest_time - selected_time
            self.updateRadialGraphs(nearest_frame, timedelta)
            pass
        except Exception as e:
            self.update_text.set("An error was generated, and has been written to the log.")
            logger.error(e.message)
            logger.error(e.__doc__)

    def createTimeGraphs(self):

        cplasma = self.MDS_data['CPLASMA']
        wmhd = self.MDS_data['WMHD']
        # return dim_signal, signal, str(units), str(dim_units)
        #           X          Y        Yunit       Xunit

        maxscale = np.amax([np.amax(cplasma[0]), np.amax(wmhd[0])])

        self.figure_a = Figure(figsize=(timegraphwidth,
                                        timegraphwidth * timegraphratio), dpi=defaultdpi, facecolor='white')
        ax_a = self.figure_a.add_subplot(2, 1, 1)
        ax_a.set_ylabel(cplasma[2])
        ax_a.set_ylim([0, np.amax(cplasma[1])])
        ax_a.set_xlim([0, maxscale])
        ax_a.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
        ax_a.set_title(self.MDS_data_titles['CPLASMA'])
        self.fig_a, = ax_a.plot(cplasma[0], cplasma[1], marker='.', linestyle='None')

        ax_b = self.figure_a.add_subplot(2, 1, 2)
        ax_b.set_xlabel('Time [s]')
        ax_b.set_ylabel(wmhd[2])
        ax_b.set_ylim([0, np.amax(wmhd[1])])
        ax_b.set_xlim([0, maxscale])
        ax_b.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
        ax_b.set_title(self.MDS_data_titles['WMHD'])
        self.fig_b, = ax_b.plot(wmhd[0], wmhd[1], marker='.', linestyle='None')

        self.figure_a.subplots_adjust(hspace=.7, bottom=0.13)

        self.canvas_a = FigureCanvasTkAgg(self.figure_a, master=self.master)

        self.multi = MultiCursor(self.canvas_a, (ax_a, ax_b), color='g', lw=2, horizOn=True)

        self.canvas_a.mpl_connect('motion_notify_event', self.TimeGraphMove)

        self.canvas_a.show()
        self.canvas_a.get_tk_widget().grid(row=2, column=1)

    def TimeGraphMove(self, event):

        if event.xdata == None:
            return

        selected_time = event.xdata

        self.updateRadialGraphTime(selected_time)

    def find_idx_nearest_value(self, target, val):
        idx = (np.abs(target-val)).argmin()
        return idx

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


        if not os.path.exists(shotnumber):
            os.makedirs(shotnumber)

        baz = ['figure_a', 'figure_1']

        for graphName in baz:
            graph = getattr(self, graphName)

            self.add_graph_thumbprint(graph)

            graphTitle = ''
            if '_1' in graphName:
                graphTitle = 'ThomsonData'
            else:
                graphTitle = 'TimeData'

            fileName = '{}/{}_{}_{}.{}'.format(shotnumber, shotnumber, graphTitle, timestamp,
                                               file_type).replace(' ', '')
            graph.savefig(fileName, dpi=defaultdpi, format=file_type, bbox_inches='tight', frameon=None)

            if self.include_csv.get():
                self.export_csv_data(fileName, file_type, graph, graphTitle)

        self.update_text.set(updatestring)

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

    def get_graph_data(self, datacaption, framenumber):
        key = ''
        for item in self.MDS_data_titles.items():
            if item[1] == datacaption:
                key = item[0]
                break

        return self.MDS_data[key][1][framenumber]

    def shotnumberInput(self):

        try:
            shotnumber = self.txtShotNumber.get()
            if shotnumber == '':
                pass

            self.get_data_object(shotnumber)

            self.update_text.set('Querying {} tree for {}'.format(treename, str(shotnumber)))

            self.load_data(shotnumber)

            self.populateGraphs(shotnumber)

            self.update_text.set('Shot number {} loaded from tree.'.format(str(shotnumber)))
        except Exception as e:
            self.update_text.set("An error has occurred, and has been written to the log.")
            logger.error(e.message)
            logger.error(e.__doc__)

    def doesShotExist(self, shotnumber):
        # TODO: is there a doesShotExist method available in the tree?
        data = self.get_data_object(shotnumber)

        return data.does_shot_exist(shotnumber)

    def populateGraphs(self, shotnumber):
        self.createTimeGraphs()

        max_ip_time = np.float64(self.MDS_data['CPLASMA'][0][np.argmax(self.MDS_data['CPLASMA'][1])])

        self.createRadialGraphs(max_ip_time)

    def radialGraphCursor_moved(self):
        pass

    def getData(self, shotnumber, requestedData):
        return self.data.get_tree_data(requestedData)

    def get_data_object(self, shotnumber):
        if USE_MDS_DATA:
            self.data = mdsdata.MDS_shot_data(treename, shotnumber)
        else:
            self.data = mockdata.mock_shot_data('foo', shotnumber)

    def load_data(self, shotnumber):
        for key, value in self.MDS_data_nodes.items():
            self.MDS_data[key] = self.getData(shotnumber, value)
            # TODO: and somehow merge into the graphs.  how to tell linear from radial?
            # stuff into figures, somehow, automagically and with correct x grid deviations
            self.update_text.set('Retrieved data for {}'.format(key))

        self.update_text.set('Data loaded from tree for {}'.format(shotnumber))

        self.tamper_with_data()

    def tamper_with_data(self):
        # look.  we all do things we aren't proud of.
        # the MDS tree is incorrect/inconsistant for units.  we, um, 'adjust' things here.
        # return dim_signal, signal, str(units), str(dim_units)
        #           X          Y        Yunit       Xunit
        cpl_tuple = self.MDS_data['CPLASMA']
        cpl = []
        cpl.append(list(cpl_tuple[0]))
        cpl.append(list(cpl_tuple[1]))
        cpl[1] = [x/1000 for x in cpl[1]]
        cpl.append('MA')
        cpl.append('Time [s]')
        self.MDS_data['CPLASMA'] = cpl

        wmhd_tuple = self.MDS_data['WMHD']
        wmhd = []
        wmhd.append(list(wmhd_tuple[0]))
        wmhd.append(list(wmhd_tuple[1]))
        wmhd[1] = [x/1000 for x in wmhd[1]]
        wmhd.append('kJ')
        wmhd.append('Time [s]')
        self.MDS_data['WMHD'] = wmhd

        self.MDS_data['RR'] = [27.5984, 38.9197, 46.7415, 54.4599, 61.7876, 68.6409, 75.014, 80.931, 91.5366, 100.742,
               108.8, 115.914, 119.17, 122.248, 125.164, 127.932, 130.563, 133.068, 135.458, 137.742,
               139.927, 142.02, 143.581, 144.478, 145.96, 147.817, 149.607, 151.333, 152.999, 156.17]

        for foo in ['FIT_TE', 'FIT_NE', 'FIT_PE']:
            bar_tuple = self.MDS_data[foo]
            bar = []
            bar.append(list(bar_tuple[0]))
            bar.append(list(bar_tuple[1].transpose()))
            bar.append(str(bar_tuple[2]))
            bar.append('Radius [cm]')
            self.MDS_data[foo] = bar

        updatestring = 'Massaged MDS data.'
        self.update_text.set(updatestring)

def main():
    root = tk.Tk()
    root.wm_title("Thomson Visualization")
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h))
    #root.geometry('{}x{}'.format(1300, 800))
    root["bg"] = "white"
    root.grid_columnconfigure(0, uniform="also", minsize=512)
    root.grid_columnconfigure(1, uniform="also")

    root["bd"] = 0
    app = tvMain(root)

    root.mainloop()  ### (3)

    sys.exit()


if __name__ == '__main__':
    main()
