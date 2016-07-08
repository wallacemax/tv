import Tkinter
import tkFont

root = Tkinter.Tk()

list_fonts = list( tkFont.families() )

list_fonts.sort()

for this_family in list_fonts:
    print this_family