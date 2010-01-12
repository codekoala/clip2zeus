from Tkinter import *
from datetime import datetime, timedelta
import re
import simplejson
import socket
import sys
import time
import urllib
import urllib2

APP_TITLE = 'Clip2Zeus'
DELIM = ' \n\r<>"\''
URL_RE = re.compile('((\w+)://([^/%s]+)(/?[^%s]*))' % (DELIM, DELIM), re.I | re.M)
INVALID_DOMAINS = ('2ze.us', 'bit.ly', 'tinyurl.com', 'tr.im', 'is.gd')

HEARTBEAT_INT = 30 # Interval to ensure we have a connection to 2ze.us (seconds)
TIMEOUT_SEC = 10 # Number of seconds to wait on 2ze.us before giving up

class UnsupportedPlatformError(StandardError): pass

class Clip2ZeusApp(object):

    def __init__(self, parent=None, *args, **kwargs):
        """Creates the container for common functionality"""

        if parent is None:
            parent = Tk()

        self.parent = parent

        self.data = ''
        self._has_connection = False
        self.last_check = None
        self.threshold = timedelta(seconds=HEARTBEAT_INT)
        socket.setdefaulttimeout(TIMEOUT_SEC)

        self.build_gui()

    def build_gui(self):
        """Constructs the GUI"""

        self.frame = Frame(self.parent)
        self.parent.title(APP_TITLE)
        self.frame.pack()

        self.btn_shorten = Button(self.frame, text="Shorten", command=self.check_clipboard)
        self.btn_quit = Button(self.frame, text="Quit", command=self.quit)

        self.btn_shorten.pack(side=LEFT)
        self.btn_quit.pack(side=LEFT)

    def start(self):
        """Begins processing"""
        self.monitor_clipboard()
        self.parent.mainloop()

    @staticmethod
    def for_platform():
        """Returns a platform-specific version of the application"""

        platform = sys.platform
        if platform in ('nt', 'win32'):
            import win32
            return win32.Clip2ZeusWin32
        elif platform in ('darwin', ):
            import osx
            return osx.Clip2ZeusOSX
        elif platform in ('linux', 'linux2'):
            import linux
            return linux.Clip2ZeusLinux
        else:
            raise UnsupportedPlatformError('%s is not currently supported!' % platform)

    @property
    def has_connection(self):
        """Ensures we have a good connection to 2ze.us"""

        now = datetime.now()

        if self.last_check is None or now - self.last_check > self.threshold:
            try:
                urllib2.urlopen('http://2ze.us/')
            except (urllib2.HTTPError, urllib2.URLError):
                self._has_connection = False
            else:
                self._has_connection = True

            self.last_check = now

        return self._has_connection

    def check_clipboard(self):
        """Checks the system clipboard for data"""
        pass

    def monitor_clipboard(self):
        """Regularly checks the system clipboard for data"""

        try:
            while True:
                # only bother processing if we have a connection
                if self.has_connection:
                    data = self.check_clipboard()

                    if data and data != self.data:
                        self.process_clipboard(data)

                time.sleep(1)
        except KeyboardInterrupt:
            self.quit()

    def process_clipboard(self, data):
        """Examines the clipboard contents for a URL.

        If one or more are found, they will be replaced with a 2zeus-shortened
        version of the longer URL."""

        update_data = False
        matches = URL_RE.findall(data)

        for match in matches:
            match = filter(lambda s: s.strip() or '', match)
            url = match[0].strip()
            domain = match[2].strip()

            if domain not in INVALID_DOMAINS:
                # Try to shorten this URL using 2ze.us
                params = urllib.urlencode({
                    'url': url,
                })

                try:
                    c = urllib2.urlopen('http://2ze.us/generate/', params)
                except (urllib2.HTTPError, urllib2.URLError):
                    # do something?
                    update_data = False
                    break
                else:
                    update_data = True
                    raw = c.read()
                    try:
                        json = simplejson.loads(raw)
                    except (ValueError, ):
                        json = None

                if json:
                    data = data.replace(url, json['urls'][url]['shortcut'])

        if update_data:
            self.data = data
            self.update_clipboard(self.data)

    def update_clipboard(self, text):
        """Updates the system clipboard with the specified text"""

        pass

    def quit(self):
        """Takes care of cleaning up"""

        print 'Exiting.'
        self.frame.quit()
        time.sleep(1)

