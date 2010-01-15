#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A Windows service for running the Clip2Zeus application in the background
on Windows.
"""

from win32serviceutil import ServiceFramework, HandleCommandLine
import servicemanager
import win32service

class Clip2ZeusService(ServiceFramework):

    _svc_name_ = "Clip2Zeus Service"
    _svc_display_name_ = "Clip2Zeus Automatic URL Shortening"

    def __init__(self, args):
        super(Clip2ZeusService, self).__init__(args)
        self.isAlive = True
        self.clip2zeus = None

    def SvcDoRun(self):
        """Starts the service"""

        from clip2zeus.win32 import Clip2ZeusWin32

        servicemanager.LogInfoMsg("Starting %s" % Clip2ZeusWin32._svc_name_)
        self.clip2zeus = Clip2ZeusWin32()
        self.clip2zeus.start()

    def SvcStop(self):
        """Stops the service"""

        servicemanager.LogInfoMsg("Stopping %s" % Clip2ZeusWin32._svc_name_)
        if self.clip2zeus is not None:
            self.clip2zeus.quit()

        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.isAlive = False

if __name__ == '__main__':
    HandleCommandLine(Clip2ZeusService)

