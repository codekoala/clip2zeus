#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import time

from common import Clip2ZeusApp

class Clip2ZeusLinux(Clip2ZeusApp):

    def check_clipboard(self):
        """Checks the system clipboard for data"""

        print 'Checking in linux'
        clipboard = gtk.clipboard_get()
        return clipboard.wait_for_text()

    def update_clipboard(self, text):
        """Updates the system clipboard with the specified text"""

        print 'Updating in linux'
        clipboard = gtk.clipboard_get()
        clipboard.set_text(text)
        clipboard.store()

if __name__ == '__main__':
    Clip2ZeusLinux()

