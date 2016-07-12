from Dialog import Dialog
from Tkinter import *

class PreferencesDialog(Dialog):
    def __init__(self, parent, prefs):
        self.preferences = prefs
        self.entries = {}
        self.updatemsg = StringVar()
        Dialog.__init__(self, parent, "Preferences")

    def body(self, master):
        plotfont = {'family': 'Bitstream Vera Sans', 'size': self.preferences['font_size'][1]}

        foo = 0
        for pref in sorted(self.preferences.keys()):
            if len(self.preferences[pref][0]) == 0:
                continue
            paramvalue = str(self.preferences[pref][1])

            Label(master, text=self.preferences[pref][0], font=plotfont).grid(row=foo, column=0)
            e = Entry(master, font=plotfont)
            e.grid(row=foo, column=1)
            e.insert(END, paramvalue)
            self.entries[pref] = e
            #TODO: tooltips
            foo += 1

        l = Label(master, textvariable=self.updatemsg)
        l.grid(row=foo, column=0)

    def validate(self):
        self.updatemsg.set('')
        for key, e in self.entries.iteritems():
            try:
                foo = int(e.get())
            except ValueError:
                self.updatemsg.set('Please check all of your inputs are numbers.')
                break
        return len(self.updatemsg.get()) == 0

    def apply(self):
        for key, value in self.entries.iteritems():
            self.preferences[key] = int(value.get())
