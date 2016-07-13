from Tkinter import *
from tvMain import *


def main():

    root.wm_title("ThomsonViz")
    root["bg"] = "white"
    root.tk_setPalette(background='white', foreground='black')
    for foo in [0, 1]:
        root.grid_columnconfigure(foo, weight=1)
    for foo in [0, 2]:
        root.grid_rowconfigure(foo, weight=1)
    root.grid_rowconfigure(2, minsize=512)
    root.resizable(True, True)

    root["bd"] = 0
    app = tvMain(root)
    root.bind('<Left>', lambda event,arg=-1: tvMain.updateTimeGraphKeypress(app, arg))
    root.bind('<Prior>', lambda event, arg=-1: tvMain.updateTimeGraphKeypress(app, arg))
    root.bind('<Right>', lambda event,arg=1: tvMain.updateTimeGraphKeypress(app, arg))
    root.bind('<Next>', lambda event, arg=1: tvMain.updateTimeGraphKeypress(app, arg))

    root.lift()

    root.mainloop()

def on_closing():
    sys.exit()

root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == '__main__':
    main()
