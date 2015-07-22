__author__ = 'maxwallace'
import sys
import tkinter as tk

import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from numpy import arange, sin, pi
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

USE_MDS_DATA = True
try:
    import MDS_shot_data as mdsdata
except ImportError:
    USE_MDS_DATA = False
    import mock_shot_data as mockdata

import ctypes

defaultdpi = 100
default_image_name = '%(shotnumber)s_%(graphname)s.%(fileextension)'
lineargraphwidth = 5
lineargraphratio = .45
radialgraphwidth = 5
radialgraphratio = .6

treename = 'nstx'

class tvMain:
    def __init__(self, master):
        self.master = master

        self.InitUI()

        self.graphs = dict()

        self.MDS_data = {'FIT_NE': '\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_NE',
                               'FIT_PE': '\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_PE',
                               'FIT_TE:': '\ACTIVESPEC::TOP.MPTS.OUTPUT_DATA.BEST:FIT_TE'}

        self.MDS_data_labels = {'FIT_NE': 'Ne units',
                               'FIT_PE': 'Pe units',
                               'FIT_TE:': 'Te units'}

    def InitUI(self):
        self.drawShotHeader()
        self.drawGraphs()
        self.drawFooter()

    def drawFooter(self):
        # footer
        btnEPS = tk.Button(text="Print EPS", command=self.printEPS)
        btnEPS.grid(row=2, column=0, sticky=tk.W)
        btnPNG = tk.Button(text="Print PNG", command=self.printPNG)
        btnPNG.grid(row=2, column=0)
        btnCSV = tk.Button(text="Save CSV", command=self.printCSV)
        btnCSV.grid(row=2, column=0, sticky=tk.E)

    def drawGraphs(self):
        # graph
        self.drawLinearGraphs()
        self.drawRadialGraphs()

    def drawLinearGraphs(self):
        linearFrame = tk.Frame(self.master)
        linearFrame.grid(row=1, column=0)

        figure_a = Figure(figsize=(lineargraphwidth, lineargraphwidth * lineargraphratio), dpi=100)
        ax_a = figure_a.add_subplot(111)
        self.fig_a, = ax_a.plot([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 1, 3, 8, 9, 3, 5])
        self.canvas_a = FigureCanvasTkAgg(figure_a, master=linearFrame)
        self.canvas_a.show()
        self.canvas_a.get_tk_widget().grid(row=0, column=0)

        figure_b = Figure(figsize=(lineargraphwidth, lineargraphwidth * lineargraphratio), dpi=100)
        ax_b = figure_b.add_subplot(111)
        self.fig_b, = ax_b.plot([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 1, 3, 8, 9, 3, 5])
        self.canvas_b = FigureCanvasTkAgg(figure_b, master=linearFrame)
        self.canvas_b.show()
        self.canvas_b.get_tk_widget().grid(row=1, column=0)

        figure_c = Figure(figsize=(lineargraphwidth, lineargraphwidth * lineargraphratio), dpi=100)
        ax_c = figure_c.add_subplot(111)
        self.fig_c, = ax_c.plot([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 1, 3, 8, 9, 3, 5])
        self.canvas_c = FigureCanvasTkAgg(figure_c, master=linearFrame)
        self.canvas_c.show()
        self.canvas_c.get_tk_widget().grid(row=2, column=0)

    def drawRadialGraphs(self):
        radialFrame = tk.Frame(self.master, bd=0)
        radialFrame.grid(row=1, column=1)
        theta = np.linspace(0, 10 * np.pi, 1000)
        r = np.linspace(0, 10, 1000)

        fig1 = plt.figure(figsize=(radialgraphwidth, radialgraphwidth * radialgraphratio), dpi=defaultdpi)
        fig1.subplots_adjust(left=None, bottom=None, right=None, wspace=None, hspace=None)
        ax1 = fig1.add_subplot(1, 1, 1, projection='polar')
        fig1.suptitle('Data Series A')
        self.fig1 = ax1.plot(theta, r)
        self.canvas1 = FigureCanvasTkAgg(fig1, master=radialFrame)
        self.canvas1.show()
        self.canvas1.get_tk_widget().grid(row=0)

        fig2 = plt.figure(figsize=(radialgraphwidth, radialgraphwidth * radialgraphratio), dpi=defaultdpi)
        fig2.subplots_adjust(left=None, bottom=None, right=None, wspace=None, hspace=None)
        ax2 = fig2.add_subplot(1, 1, 1, projection='polar')
        fig1.suptitle('Data Series B')
        self.fig2 = ax2.plot(theta, r)
        self.canvas2 = FigureCanvasTkAgg(fig1, master=radialFrame)
        self.canvas2.show()
        self.canvas2.get_tk_widget().grid(row=1)

    def drawShotHeader(self):
        # setup shot frame
        self.entryFrame = tk.Frame(self.master)
        self.entryFrame.grid(row=0, column=0, sticky=tk.W)

        self.txtShotNumber = tk.Entry(self.entryFrame, width=12)
        # txtShotNumber.insert("1.0", "Shot Number")
        self.txtShotNumber.pack(side=tk.LEFT)
        self.playLogo = tk.PhotoImage(file="play.gif")
        self.btnShot = tk.Button(self.entryFrame, image=self.playLogo, command=self.shotnumberinput())
        self.btnShot.pack(side=tk.LEFT)

        lblTime = tk.Label(text='Time', background='white')
        lblTime.grid(row=0, column=0)
        lblUserID = tk.Label(text='UserID', background='white')
        lblUserID.grid(row=0, column=0, sticky=tk.E)

        self.headerLogo = tk.PhotoImage(file="logo.gif")
        lblLogo = tk.Label(image=self.headerLogo)
        lblLogo.grid(row=0, column=1)

    def add_graph_to_dict(self, graph, graphname):
        self.graphs.__setitem__(graphname, graph)

    def export_graphs(self, shotid, file_type, export_csv=0):
        for graph, graphname in self.graphs:
            # what's the naming protocol like?  aw, let's just do this
            filename = default_image_name.format(shotid, graph.title(), file_type)
            graph.savefig(filename, dpi=defaultdpi, bbox_inches='tight')

            if export_csv:
                pass
                # export graph csv data
            pass

    def shotnumberinput(self):
        shotnumber = self.txtShotNumber.get()

        self.populateGraphs(shotnumber)

    def populateGraphs(self, shotnumber):
        # load each grid.  but don't be limited to these three
        pass

    def getData(self, shotnumber, requestedData):
        if USE_MDS_DATA:
            data = mdsdata.MDS_shot_data(treename, shotnumber)
        else:
            data = mockdata.mock_shot_data('foo', 4)

        return data.get_tree_data(requestedData)

    def printEPS(self):
        pass

    def printPNG(self):
        pass

    def printCSV(self):
        pass

def main():
    root = tk.Tk()
    root.wm_title("Thomson Visualization")
    # root.resizable(width=Tk.FALSE, height=Tk.FALSE)
    #root.geometry('{}x{}'.format(1024, 768))
    root["bg"] = "white"
    root.grid_columnconfigure(0, uniform="also")
    root.grid_columnconfigure(1, uniform="also")
    root["bd"] = 0
    app = tvMain(root)

    root.mainloop()  ### (3)

    sys.exit()

if __name__ == '__main__':
    main()