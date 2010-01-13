#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A Tk interface to control Clip2Zeus
"""

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

import sys
import tkMessageBox

from clip2zeus_ctl import Clip2ZeusCtl
from common import APP_TITLE, DEFAULT_PORT

ID_MANUAL = 100
ID_AUTO = 110

class Clip2ZeusTk(Clip2ZeusCtl):

    def __init__(self, ):
        super(Clip2ZeusTk, self).__init__()

        self.launch_server()
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
        self.scl_interval = tk.Scale(self.parent, from_=0, to=30,
            label='Interval', orient=tk.HORIZONTAL, tickinterval=10, command=self.mode_selected)

        self.btn_shorten = tk.Button(self.parent, text="Shorten", command=self.check_clipboard)
        self.btn_quit = tk.Button(self.parent, text="Quit", command=self.quit)

        self.opt_manual.grid(row=0, column=0, sticky='w')
        self.opt_poll.grid(row=1, column=0, sticky='w')
        self.btn_shorten.grid(row=0, column=1, sticky='e')
        self.btn_quit.grid(row=1, column=1, sticky='e')
        self.scl_interval.grid(row=2, column=0, sticky='w')

    def notify(self, message):
        """Tells the user something"""

        tkMessageBox.showwarning(message=message)

    def check_clipboard(self):
        """Checks the clipboard for URLs that need to be shortened"""

        self.execute_command('shorten_urls')

    def mode_selected(self, interval=-1):
        """Sets the polling mode--automatic vs manual"""

        if int(interval) == 0:
            self.opt_value.set(ID_MANUAL)
            self.opt_manual.select()
        elif int(interval) > 0:
            self.opt_value.set(ID_AUTO)
            self.opt_poll.select()
        elif interval == -1:
            mode = self.opt_value.get()
            if mode == ID_AUTO:
                interval = int(self.scl_interval.get())
                if interval <= 0:
                    interval = 1

            elif mode == ID_MANUAL:
                interval = 0

            self.mode_selected(interval)

        self.scl_interval.set(interval)
        self.execute_command('set_interval', [interval])

    def quit(self):
        """Kills the application"""

        self.execute_command('quit')
        sys.exit(0)

def main():
    Clip2ZeusTk()

if __name__ == '__main__':
    main()

