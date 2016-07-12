from Tkinter import *
from tvMain import *


def main():
    center_window()
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
    root.bind('<Right>', lambda event,arg=1: tvMain.updateTimeGraphKeypress(app, arg))

    root.lift()

    root.mainloop()  ### (3)
    app.savePreferences()

def on_closing():
    sys.exit()

def center_window(width=1268, height=760):
    # get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))


root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == '__main__':
    main()
