from SimpleXMLRPCServer import SimpleXMLRPCServer
from datetime import datetime, timedelta
from threading import Thread
import re
import simplejson
import socket
import sys
import time
import urllib
import urllib2
import xmlrpclib

APP_TITLE = 'Clip2Zeus'
DELIM = ' \n\r<>"\''
URL_RE = re.compile('((\w+)://([^/%%%s]+)(/?[^%s]*))' % (DELIM, DELIM), re.I | re.M)
INVALID_DOMAINS = ('2ze.us', 'bit.ly', 'tinyurl.com', 'tr.im', 'is.gd')

HEARTBEAT_INT = 30 # Interval to ensure we have a connection to 2ze.us (seconds)
TIMEOUT_SEC = 10 # Number of seconds to wait on 2ze.us before giving up
DEFAULT_PORT = 14694

class UnsupportedPlatformError(StandardError): pass

class Monitor(Thread):
    """Regularly checks the system clipboard for data"""

    def __init__(self, *args, **kwargs):
        self.app = kwargs.pop('app')
        super(Monitor, self).__init__(*args, **kwargs)

    def run(self):
        self._continue_processing = True

        while self._continue_processing:
            # don't do anything if the user only wants manual shortening
            if self.app.interval <= 0:
                time.sleep(1)
                continue

            try:
                self.app.shorten_urls()
                time.sleep(self.app.interval)
            except KeyboardInterrupt:
                self.app.quit()

    def close(self):
        self._continue_processing = False

class Clip2ZeusApp(object):

    EXPOSED = ('help', 'set_interval', 'shorten_urls', 'quit')

    def __init__(self, port=DEFAULT_PORT):
        """Creates the container for common functionality"""

        self.port = int(port)

        self.data = ''
        self._has_connection = False
        self.last_check = None
        self.interval = 1
        self.threshold = timedelta(seconds=HEARTBEAT_INT)
        socket.setdefaulttimeout(TIMEOUT_SEC)

        self.monitor_thread = Monitor(app=self)

    def expose_api(self):
        """Exposes a collection of commands for the XML-RPC server"""

        for func in Clip2ZeusApp.EXPOSED:
            self.server.register_function(getattr(self, func))

    def start(self):
        """Begins processing"""

        self.monitor_thread.start()
        self.start_server()

    def start_server(self):
        """Starts the XML-RPC server"""

        try:
            self.server = SimpleXMLRPCServer(('localhost', self.port), allow_none=True)
            self.expose_api()
            self.server.serve_forever()
        except socket.error as err:
            # my sad excuse for a graceful termination
            if err.errno == 9:
                pass
            elif err.errno == 48: # address already used
                pass
            else:
                raise err
        except KeyboardInterrupt:
            self.quit()

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

    def help(self, func=None):
        """Provides further information about a particular command"""

        if func is None:
            return self.help.__doc__
        elif func in Clip2ZeusApp.EXPOSED:
            return getattr(self, func).__doc__
        else:
            return "Invalid command."

    def check_clipboard(self):
        """Checks the system clipboard for data"""

        pass

    def update_clipboard(self, text):
        """Updates the system clipboard with the specified text"""

        pass

    def set_interval(self, interval):
        """Sets the clipboard polling frequency.

        Accepts one parameter: the number of seconds between clipboard polls.
        Use 0 to represent manual invocation."""

        try:
            self.interval = int(interval)

            if self.interval < 0:
                raise ValueError
        except (TypeError, ValueError):
            raise TypeError('Please specify an integer that is 0 or greater.')

    def shorten_urls(self):
        """Shortens any URLs that are currently in the clipboard"""

        # only bother processing if we have a connection
        if self.has_connection:
            data = self.check_clipboard()

            if data and data != self.data:
                self.process_clipboard(data)

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

    def quit(self):
        """Ends processing"""

        print 'Exiting.'
        self.monitor_thread.close()
        self.server.server_close() # see if there's a better way to handle this
        return 0

class Clip2ZeusCtl(object):
    """
    An XML-RPC controller for Clip2Zeus, so you can still control the app
    after backgrounding it.
    """

    def __init__(self, port=DEFAULT_PORT):
        self.port = port
        self.proxy = None
        self.connect()

    def launch_server(self):
        """Launches the server if needed--not a good idea with the CLI command"""

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', DEFAULT_PORT))
        except socket.error as err:
            if err.errno == 48: # address already in use
                pass
            else:
                raise err
        else:
            sock.close()
            from clip2zeus import main
            self.server_thread = Thread(target=main)
            self.server_thread.start()
            time.sleep(1)

    def notify(self, message):
        """Tells the user something"""

        print message

    def execute_command(self, cmd, args=[]):
        """Calls a command using the XML-RPC proxy"""

        try:
            if cmd == 'help':
                self.help(*args)
            elif cmd in Clip2ZeusApp.EXPOSED:
                func = getattr(self.proxy, cmd)
                func(*args)
            else:
                sys.exit('Invalid command.  Options include: %s' % ', '.join(Clip2ZeusApp.EXPOSED))
        except socket.error as err:
            self.notify('Failed to connect to application: %s' % err)

            if err.errno == 61:
                sys.exit(1)
        except xmlrpclib.Fault as fault:
            self.notify('%s' % fault)

    def connect(self, port=None):
        """Attempt to connect to the XML-RPC server"""

        try:
            port = port or self.port
            self.proxy = xmlrpclib.ServerProxy('http://localhost:%s/' % port, allow_none=True)
        except Exception, e:
            print e
        else:
            self.port = port

    def help(self, func=None):
        """Calls the help function on the server"""

        print self.proxy.help(func)

