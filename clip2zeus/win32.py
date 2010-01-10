#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Monitors the Windows system clipboard for text that contains URLs for conversion
using 2ze.us"""

import time
import win32clipboard as w
from common import Clip2ZeusApp

class Clip2ZeusWin32(Clip2ZeusApp):

    def do_clipboard_operation(self, func, *args, **kwargs):
        """Performs a quick clipboard operation, wrapping it with safety nets"""

        try:
            w.OpenClipboard()
        except Exception, err:
            pass
        else:
            try:
                result = func(*args, **kwargs)
            except TypeError, err:
                # clipboard does not contain text
                result = ''
        finally:
            try:
                w.CloseClipboard()
            except Exception, err:
                if err[0] != 1418: # Clipboard not open
                    raise err

        return result

    def monitor_clipboard(self):
        """Regularly checks the system clipboard for data"""

        def get_data():
            return w.GetClipboardData(w.CF_TEXT)

        try:
            while True:
                # only bother processing if we have a connection
                if self.has_connection:
                    data = self.do_clipboard_operation(get_data)
                    if data != self.data:
                        self.process_clipboard(data)

                time.sleep(1)
        except KeyboardInterrupt:
            self.quit()

    def update_clipboard(self, text):
        """Updates the system clipboard with the specified text"""

        def set_data(text):
            w.EmptyClipboard()
            return w.SetClipboardText(text)

        self.do_clipboard_operation(set_data, text=text)

if __name__ == '__main__':
    Clip2ZeusWin32()

