from Tkinter import Tk
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure



def main():
    root = Tk()

    f = Figure(figsize=(3,1.5), dpi=100)
    a = f.add_subplot(111)
    a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
    canvas = FigureCanvasTkAgg(f, root)
    canvas.show()
    canvas.get_tk_widget().grid(row=1, column=0)

    root.focus_force()
    root.mainloop()


if __name__ == '__main__':
    main()  