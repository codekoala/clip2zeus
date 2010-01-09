#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Monitors the Windows system clipboard for text that contains URLs for conversion
using 2ze.us"""

import time
import win32clipboard as w
from common import Clip2ZeusApp

class Clip2ZeusWin32(Clip2ZeusApp):

    def monitor_clipboard(self):
        """Regularly checks the system clipboard for data"""

        try:
            while True:
                # only bother processing if we have a connection
                if self.has_connection:
                    try:
                        w.OpenClipboard()
                        data = w.GetClipboardData(w.CF_TEXT)
                    except (TypeError, ):
                        pass
                    else:
                        if data != self.data:
                            self.process_clipboard(data)
                    finally:
                        try:
                            w.CloseClipboard()
                        except Exception, err:
                            if err[0] != 1418: # Clipboard not open
                                raise err

                time.sleep(1)
        except KeyboardInterrupt:
            self.quit()

    def update_clipboard(self, text):
        """Updates the system clipboard with the specified text"""

        w.OpenClipboard()
        w.EmptyClipboard()
        w.SetClipboardText(text)
        w.CloseClipboard()

