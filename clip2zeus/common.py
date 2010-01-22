from datetime import datetime, timedelta
from threading import Thread, Event
import re

try:
    # Python 2.6+
    import json
except ImportError:
    import simplejson as json
    
import socket
import sys
import time
import urllib
import urllib2
import xmlrpclib

from clip2zeus import APP_TITLE, __version__
from clip2zeus.globals import *
from clip2zeus.config import *

class Clip2ZeusApp(object):

    EXPOSED = ('help', 'get_version', 'get_interval', 'set_interval', 'shorten_urls', 'quit')

    def __init__(self, port=DEFAULT_PORT):
        """Creates the container for common functionality"""

        logger.debug('Welcome to %s v%s' % (APP_TITLE, __version__))

        self.port = int(port)

        self.data = ''
        self.server = None
        self._has_connection = False
        self.last_check = None
        self.interval = config.get('main', 'interval', 1)
        self.threshold = timedelta(seconds=HEARTBEAT_INT)
        socket.setdefaulttimeout(TIMEOUT_SEC)

        self.thread_event = Event()
        self.monitor_thread = Thread(target=self.monitor_clipboard)

    def expose_api(self):
        """Exposes a collection of commands for the XML-RPC server"""

        logger.debug('Exposing API')
        for func in Clip2ZeusApp.EXPOSED:
            logger.debug(' - %s' % func)
            self.server.register_function(getattr(self, func))

    def start(self):
        """Begins processing"""

        logger.debug('Beginning Clip2Zeus')
        self.monitor_thread.start()
        self.start_server()

    def start_server(self):
        """Starts the XML-RPC server"""

        if not port_is_free(self.port):
            logger.error('Port %s is already being used.' % self.port)
            self.quit()
            sys.exit(1)

        try:
            logger.debug('Starting server on port %s...' % self.port)
            self.server = Server(('localhost', self.port), allow_none=True, logRequests=False)
            self.expose_api()
            self.server.serve_forever()
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

    def get_version(self):
        """Retrieves the version number for the server"""

        return __version__

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

    def get_interval(self, default=1):
        """Returns the current polling interval in seconds"""

        logger.debug('Interval requested by client: %s' % (self.interval,))
        return self.interval

    def set_interval(self, interval):
        """Sets the clipboard polling frequency.

        Accepts one parameter: the number of seconds between clipboard polls.
        Use 0 to represent manual invocation."""

        try:
            logger.debug('Updating interval to %s' % interval)
            self.interval = int(interval)

            if self.interval < 0:
                raise ValueError

            config.set('main', 'interval', self.interval)
        except (TypeError, ValueError), err:
            logger.error('%s' % (err,))
            raise ValueError('Please specify an integer that is 0 or greater.')

    def monitor_clipboard(self):
        """Regularly checks the system clipboard for data"""

        while True:
            if self.interval <= 0:
                wait = 1
            else:
                wait = self.interval

            self.thread_event.wait(wait)
            if self.thread_event.isSet():
                break

            if self.interval > 0:
                self.shorten_urls()

    def shorten_urls(self):
        """Shortens any URLs that are currently in the clipboard"""

        # only bother processing if we have a connection
        if self.has_connection:
            data = self.check_clipboard()

            if data and data != self.data:
                logger.info('Found new clipboard data to process.')
                logger.debug('Old data: %s' % (self.data, ))
                logger.debug('New data: %s' % (data, ))
                self.process_clipboard(data)

    def process_clipboard(self, data):
        """Examines the clipboard contents for a URL.

        If one or more are found, they will be replaced with a 2zeus-shortened
        version of the longer URL."""

        logger.info('Shortening URLs in clipboard')

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
                    logger.info(' - %s' % url)
                    c = urllib2.urlopen('http://2ze.us/generate/', params)
                except (urllib2.HTTPError, urllib2.URLError):
                    # do something?
                    update_data = False
                    break
                else:
                    update_data = True
                    raw = c.read()
                    try:
                        usable = json.loads(raw)
                    except (ValueError, ):
                        usable = None

                if usable and usable['urls'].get(url, None):
                    short = usable['urls'][url]['shortcut']
                    logger.info('   -> %s' % short)
                    data = data.replace(url, short)

        self.data = data

        if update_data:
            logger.debug('Updating clipboard')
            self.update_clipboard(self.data)

    def quit(self):
        """Ends processing"""

        logger.info('Exiting.')
        self.thread_event.set()
        self.monitor_thread.join()

        if self.server:
            self.server.kill()

class Clip2ZeusCtl(object):
    """
    An XML-RPC controller for Clip2Zeus, so you can still control the app
    after backgrounding it.
    """

    def __init__(self, port=DEFAULT_PORT):
        self.port = port
        self.proxy = None
        self.connect()

    def notify(self, message):
        """Tells the user something"""

        logger.debug('Received message: %s' % (message, ))
        print message

    def execute_command(self, cmd, args=[]):
        """Calls a command using the XML-RPC proxy"""

        logger.debug('Executing command "%s" via XML-RPC' % (cmd, ))
        try:
            if cmd == 'help':
                self.help(*args)
            elif cmd in Clip2ZeusApp.EXPOSED:
                func = getattr(self.proxy, cmd)
                return func(*args)
            else:
                logger.error('Invalid command: %s' % (cmd, ))
                sys.exit('Invalid command.  Options include: %s' % ', '.join(Clip2ZeusApp.EXPOSED))
        except socket.error, err:
            self.notify('Failed to connect to application: %s' % (err[1], ))

            if err[0] in (48, 61, 10061):
                sys.exit(1)
        except xmlrpclib.Fault, fault:
            self.notify('%s' % (fault, ))

    def connect(self, port=DEFAULT_PORT):
        """Attempt to connect to the XML-RPC server"""

        logger.debug('Connecting to XML-RPC server')
        if port_is_free(port):
            logger.error('Port is not in use')
            sys.exit(1)

        try:
            port = port or self.port
            self.proxy = xmlrpclib.ServerProxy('http://localhost:%s/' % port, allow_none=True)
        except Exception, e:
            logger.error('%s' % (e, ))
            raise e
        else:
            self.port = port

    def help(self, func=None):
        """Calls the help function on the server"""

        print self.proxy.help(func)

