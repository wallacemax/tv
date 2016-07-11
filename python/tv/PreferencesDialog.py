from Dialog import Dialog
from Tkinter import *

class PreferencesDialog(Dialog):
    def __init__(self, parent, prefs):
        self.preferences = prefs
        Dialog.__init__(self, parent, "Preferences")

    def body(self, master):
        plotfont = {'family': 'Bitstream Vera Sans', 'size': self.preferences['font_size'][1]}

        foo = 0
        for pref in sorted(self.preferences.keys()):
            if len(self.preferences[pref][0]) == 0:
                continue
            Label(master, text=self.preferences[pref][0], font=plotfont).grid(row=foo, column=0)
            Entry(master, text=self.preferences[pref][1], font=plotfont).grid(row=foo, column=1)
            foo += 1

    def validate(self):
        return 1

    def apply(self):
        pass