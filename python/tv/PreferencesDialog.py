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
        for key, value in sorted(self.preferences.iteritems()):
            if len(value[0]) == 0:
                continue
            paramvalue = str(value[1])

            Label(master, text=value[0], font=plotfont).grid(row=foo, column=0)
            e = Entry(master, font=plotfont)
            e.grid(row=foo, column=1)
            e.insert(END, paramvalue)
            self.entries[key] = e
            #TODO: tooltips
            foo += 1

        l = Label(master, textvariable=self.updatemsg)
        l.grid(row=foo, column=0)

    def validate(self):
        self.updatemsg.set('')
        for key, e in self.entries.iteritems():
            try:
                foo = float(e.get())
            except ValueError:
                self.updatemsg.set('Please check all of your inputs are numbers.')
                break
        return len(self.updatemsg.get()) == 0

    def apply(self):
        for key, value in self.entries.iteritems():
            self.preferences[key][1] = float(value.get())
