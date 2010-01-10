#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import time
from common import Clip2ZeusApp

class Clip2ZeusLinux(Clip2ZeusApp):

    def monitor_clipboard(self):
        """Regularly checks the system clipboard for data"""

        try:
            while True:
                # only bother processing if we have a connection
                if self.has_connection:
                    clipboard = gtk.clipboard_get()
                    data = clipboard.wait_for_text()

                    if data and data != self.data:
                        self.process_clipboard(data)
                time.sleep(1)
        except KeyboardInterrupt:
            self.quit()

    def update_clipboard(self, text):
        """Updates the system clipboard with the specified text"""

        clipboard = gtk.clipboard_get()
        clipboard.set_text(text)
        clipboard.store()

if __name__ == '__main__':
    Clip2ZeusLinux()

