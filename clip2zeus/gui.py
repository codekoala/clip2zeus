#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A Tk interface to control Clip2Zeus
"""

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

from clip2zeus_ctl import Clip2ZeusCtl

class Clip2ZeusTk(Clip2ZeusCtl):

    def __init__(self):
        super(Clip2ZeusTk, self).__init__()

        self.build_gui()
        self.parent.mainloop()

    def build_gui(self):
        """Constructs the GUI"""

        self.parent = tk.Tk()
        self.parent.title(APP_TITLE)

        self.opt_value = tk.IntVar()
        self.opt_poll = tk.Radiobutton(self.parent, text='Automatic shortening',
            value=ID_AUTO, variable=self.opt_value, command=self.mode_selected)
        self.opt_manual = tk.Radiobutton(self.parent, text='Manual shortening',
            value=ID_MANUAL, variable=self.opt_value, command=self.mode_selected)

        self.btn_shorten = tk.Button(self.parent, text="Shorten", command=self.check_clipboard)
        self.btn_quit = tk.Button(self.parent, text="Quit", command=self.quit)

        self.opt_manual.grid(row=0, column=0, sticky='w')
        self.opt_poll.grid(row=1, column=0, sticky='w')
        self.btn_shorten.grid(row=0, column=1, sticky='e')
        self.btn_quit.grid(row=1, column=1, sticky='e')

    def mode_selected(self):
        print 'Mode selected: ', self.opt_value.get()

if __name__ == '__main__':
    Clip2ZeusTk()

