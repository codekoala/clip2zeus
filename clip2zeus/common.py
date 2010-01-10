from datetime import datetime, timedelta
import re
import simplejson
import socket
import sys
import time
import urllib
import urllib2

APP_TITLE = 'Clip2Zeus'
URL_RE = re.compile('((\w+)://([^/]+)/?([^ \n\r]*))', re.I | re.M)
INVALID_DOMAINS = ('2ze.us', 'bit.ly', 'tinyurl.com', 'tr.im', 'is.gd')

HEARTBEAT_INT = 30 # Interval to ensure we have a connection to 2ze.us (seconds)
TIMEOUT_SEC = 10 # Number of seconds to wait on 2ze.us before giving up

class UnsupportedPlatformError(StandardError): pass

class Clip2ZeusApp(object):

    def __init__(self):
        self.data = ''
        self._has_connection = False
        self.last_check = None
        self.threshold = timedelta(seconds=HEARTBEAT_INT)
        socket.setdefaulttimeout(TIMEOUT_SEC)
        self.monitor_clipboard()

    @staticmethod
    def for_platform():
        """Returns a platform-specific version of the application"""

        if sys.platform in ('nt', 'win32'):
            import win32
            return win32.Clip2ZeusWin32
        elif sys.platform in ('darwin', ):
            import osx
            return osx.Clip2ZeusOSX
        else:
            raise UnsupportedPlatformError

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

    def monitor_clipboard(self):
        """Regularly checks the system clipboard for data"""
        pass

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

