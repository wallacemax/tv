from Dialog import Dialog
from Tkinter import *

class PreferencesDialog(Dialog):
    def __init__(self, parent):
        Dialog.__init__(self, parent, "Preferences")

    def body(self, master):
        Label(master, text="First:").grid(row=0)
        Label(master, text="Second:").grid(row=1)

        self.e1 = Entry(master)
        self.e2 = Entry(master)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        return self.e1  # initial focus

    def apply(self):
        first = int(self.e1.get())
        second = int(self.e2.get())
        print first, second  # or something
    # def body(self, master):
    #     plotfont = {'family': 'Bitstream Vera Sans', 'size': self.preferences['font_size'][1]}
    #
    #     masterFrame = Frame(master)
    #     for pref in self.preferences:
    #         with Frame(master) as fr:
    #             Label(fr, text=self.preferences[pref][0], font=plotfont).grid(row=0, column=0)
    #             Entry(fr, text=self.preferences[pref][1], font=plotfont).grid(row=0, column=1)
    #
    #
    # def validate(self):
    #     return 1
    #
    # def apply(self):
    #     pass