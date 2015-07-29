__author__ = 'maxwallace'
import sys
import tkinter as tk
import os
import datetime

import matplotlib
import matplotlib.pyplot as plt

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from time import strftime

USE_MDS_DATA = True
try:
    import MDS_shot_data as mdsdata
except ImportError:
    USE_MDS_DATA = False
    import mock_shot_data as mockdata

import ctypes

defaultdpi = 100
radialgraphwidth = 5
radialgraphratio = 1.2
timegraphwidth = 5
timegraphratio = .6

treename = 'nstx'
userid = os.getenv('LOGNAME')

include_csv = 0

plotfont = {'family': 'san-serif', 'size': 12}
matplotlib.rc('font', **plotfont)


class tvMain:
    def __init__(self, master):
        self.master = master

        self.update_text = tk.StringVar()
        self.update_text.set('Loading initial graphics.')

        self.InitUI()

        self.MDS_data_nodes = {'FIT_NE': '\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_NE',
                               'FIT_PE': '\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_PE',
                               'FIT_TE': '\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_TE',
                               'CPLASMA': '\EFIT01::TOP.RESULTS.GEQDSK:CPASMA',
                               'WMHD': '\EFIT01::TOP.RESULTS.AEQDSK:WMHD'}

        self.MDS_data = {'FIT_NE': [],
                         'FIT_PE': [],
                         'FIT_TE': [],
                         'CPLASMA': [],
                         'WMHD': []}

        self.MDS_data_titles = {'FIT_NE': 'Density (Ne)',
                                'FIT_PE': 'Pressure (Pe)',
                                'FIT_TE': 'Temperature (Te)',
                                'CPLASMA': 'Plasma Current',
                                'WMHD': 'Stored Energy'}

        self.update_text.set('Please input shot number for visualization.')

    def InitUI(self):
        self.drawShotHeader()
        # self.drawGraphs()
        self.drawFooter()

    def drawFooter(self):
        # footer
        btnEPS = tk.Button(text="Print EPS", command=lambda: self.export_graphs(self.txtShotNumber.get(), 'EPS'))
        btnEPS.grid(row=3, column=0, sticky=tk.W)
        btnPNG = tk.Button(text="Print PNG", command=lambda: self.export_graphs(self.txtShotNumber.get(), 'PNG'))
        btnPNG.grid(row=3, column=0)
        self.include_csv = tk.IntVar()
        self.chkCSV = tk.Checkbutton(text="Save CSV", variable=include_csv)
        self.chkCSV.grid(row=3, column=0, sticky=tk.E)

    def drawGraphs(self):
        # graph
        self.drawRadialGraphs()
        self.drawTimeGraphs()

    def drawRadialGraphs(self, framenumber=0):

        self.framenumber = framenumber

        radialFrame = tk.Frame(self.master)
        radialFrame.grid(row=2, column=0)

        ne = self.MDS_data['FIT_NE']
        te = self.MDS_data['FIT_TE']
        pe = self.MDS_data['FIT_PE']

        self.figure_1 = plt.figure(figsize=(radialgraphwidth,
                                            radialgraphwidth * radialgraphratio),
                                   dpi=defaultdpi,
                                   facecolor='white')

        self.figure_1.add_axes()
        self.figure_1.add_subplot(311)

        self.ax1 = plt.subplot(3, 1, 1)
        self.ax1.plot(ne[framenumber])
        self.ax1.set_title(self.MDS_data_titles['FIT_NE'])
        self.ax1.set_ylabel('eV?')

        self.ax2 = plt.subplot(3, 1, 2)
        self.ax2.plot(te[framenumber])
        self.ax2.set_title(self.MDS_data_titles['FIT_TE'])
        self.ax2.set_ylabel('eV?')

        self.ax3 = plt.subplot(3, 1, 3)
        self.ax3.plot(pe[framenumber])
        self.ax3.set_title(self.MDS_data_titles['FIT_PE'])
        self.ax3.set_ylabel('eV?')

        self.ax3.set_xlabel('Radial Profile')
        self.figure_1.subplots_adjust(hspace=1)

        self.canvas_1 = FigureCanvasTkAgg(self.figure_1, master=radialFrame)
        self.canvas_1.show()
        self.canvas_1.get_tk_widget().grid(row=0, column=0)

    def drawTimeGraphs(self):

        timeFrame = tk.Frame(self.master, bd=0)
        timeFrame.grid(row=2, column=1)

        cplasma = self.MDS_data['CPLASMA']
        wmhd = self.MDS_data['WMHD']

        self.figure_a = Figure(figsize=(timegraphwidth,
                                        timegraphwidth * timegraphratio), dpi=defaultdpi, facecolor='white')
        ax_a = self.figure_a.add_subplot(111)
        ax_a.set_xlabel('Time (ms)')
        ax_a.set_ylabel('eV ?')
        self.figure_a.suptitle(self.MDS_data_titles['CPLASMA'])
        self.fig_a, = ax_a.plot(cplasma)
        self.canvas_a = FigureCanvasTkAgg(self.figure_a, master=timeFrame)
        self.canvas_a.show()
        self.canvas_a.get_tk_widget().grid(row=0, column=0)

        self.figure_b = Figure(figsize=(timegraphwidth,
                                        timegraphwidth * timegraphratio), dpi=defaultdpi, facecolor='white')
        ax_b = self.figure_b.add_subplot(111)
        ax_b.set_xlabel('Time (ms)')
        ax_b.set_ylabel('eV ?')
        self.figure_b.suptitle(self.MDS_data_titles['WMHD'])
        self.fig_b, = ax_b.plot(wmhd)
        self.canvas_b = FigureCanvasTkAgg(self.figure_b, master=timeFrame)
        self.canvas_b.show()
        self.canvas_b.get_tk_widget().grid(row=1, column=0)

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

        lblTime = tk.Label(text=strftime('%H:%M:%S'), background='white')
        lblTime.grid(row=0, column=0)
        lblUserID = tk.Label(text=userid, background='white')
        lblUserID.grid(row=0, column=0, sticky=tk.E)

        self.headerLogo = tk.PhotoImage(file="logo.gif")
        lblLogo = tk.Label(image=self.headerLogo)
        lblLogo.grid(row=0, column=1, sticky=tk.E)

        self.lblOutput = tk.Label(textvariable=self.update_text)
        self.lblOutput.grid(row=1, column=0, columnspan=2)

    def export_graphs(self, shotid, file_type):
        # foo = "export {} {}, include CSV: {} ".format(str(shotid), file_type, str(include_csv))
        # print(foo)
        shotnumber = str(shotid)

        # YYYYMMDDTHH24MMSS
        timestamp = datetime.datetime.isoformat(
            datetime.datetime.today()).split('.')[0].replace('-', '').replace(':', '')

        updatestring = 'Images for {} saved in {} format'.format(shotid,
                            file_type + ' and CSV' if self.include_csv.get() else file_type)

        if not os.path.exists(shotnumber):
            os.makedirs(shotnumber)

        for graphName in {'figure_a', 'figure_b', 'figure_1'}:
            graph = getattr(self, graphName)

            try:
                graphTitle = graph._suptitle._text
            except AttributeError:
                graphTitle = 'ThomsonData'

            fileName = '{}/{}_{}_{}.{}'.format(shotnumber, shotnumber, graphTitle, timestamp,
                                               file_type).replace(' ', '')
            graph.savefig(fileName, dpi=defaultdpi, format=file_type, bbox_inches='tight', frameon=None)

            if self.include_csv.get():
                self.export_csv_data(fileName, file_type, graph, graphTitle)

        self.update_text.set(updatestring)

    def export_csv_data(self, fileName, file_type, graph, graphTitle):
        if graphTitle == 'ThomsonData':
            self.export_thomson_csv_data(fileName, file_type)
        else:
            self.export_time_csv_data(fileName, file_type, graph)

    def export_time_csv_data(self, fileName, file_type, graph):
        line = graph.gca().get_lines()[0].get_xydata()
        np.savetxt(fileName.replace(file_type, 'csv'), line, delimiter=',')

    def export_thomson_csv_data(self, fileName, file_type):
        for i in range(1, 3):
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

        return self.MDS_data[key][framenumber]

    def shotnumberInput(self):
        shotnumber = self.txtShotNumber.get()
        if shotnumber == '':
            pass

        self.get_data_object(shotnumber)

        self.update_text.set('Querying {} tree for {}'.format(treename, str(shotnumber)))

        self.load_data(shotnumber)

        self.populateGraphs(shotnumber)

        self.update_text.set('Shot number {} loaded from tree.'.format(str(shotnumber)))

    def doesShotExist(self, shotnumber):
        # TODO: is there a doesShotExist method available in the tree?
        data = self.get_data_object(shotnumber)

        return data.does_shot_exist(shotnumber)

    def populateGraphs(self, shotnumber):
        self.drawTimeGraphs()
        self.drawRadialGraphs(0)

    def radialGraphCursor_moved(self):
        pass

    def getData(self, shotnumber, requestedData):
        return self.data.get_tree_data(requestedData)

    def get_data_object(self, shotnumber):
        if USE_MDS_DATA:
            self.data = mdsdata.MDS_shot_data(treename, shotnumber)
        else:
            self.data = mockdata.mock_shot_data('foo', 4)

    def load_data(self, shotnumber):
        for key, value in self.MDS_data_nodes.items():
            self.MDS_data[key] = self.getData(shotnumber, value)
            # TODO: and somehow merge into the graphs.  how to tell linear from radial?
            # stuff into figures, somehow, automagically and with correct x grid deviations
            self.update_text.set('Retrieved data for {}'.format(key))

        self.update_text.set('Data loaded from tree for {}'.format(shotnumber))


def main():
    root = tk.Tk()
    root.wm_title("Thomson Visualization")
    root.geometry('{}x{}'.format(1024, 768))
    root["bg"] = "white"
    root.grid_columnconfigure(0, uniform="also", minsize=512)
    root.grid_columnconfigure(1, uniform="also")
    root["bd"] = 0
    app = tvMain(root)

    root.mainloop()  ### (3)

    sys.exit()


if __name__ == '__main__':
    main()
