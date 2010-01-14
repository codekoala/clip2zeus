from SimpleXMLRPCServer import SimpleXMLRPCServer
from datetime import datetime, timedelta
from threading import Thread, Event
import logging
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

__author__ = 'Josh VanderLinden'
__version__ = '0.8e'

APP_TITLE = 'Clip2Zeus'
DELIM = ' \n\r<>"\''
URL_RE = re.compile('((\w+)://([^/%%%s]+)(/?[^%s]*))' % (DELIM, DELIM), re.I | re.M)
INVALID_DOMAINS = ('2ze.us', 'bit.ly', 'tinyurl.com', 'tr.im', 'is.gd')

HEARTBEAT_INT = 30 # Interval to ensure we have a connection to 2ze.us (seconds)
TIMEOUT_SEC = 10 # Number of seconds to wait on 2ze.us before giving up
DEFAULT_PORT = 14694
LOG_FILE = 'clip2zeus.log'
LOG_LEVEL = logging.DEBUG
FORMAT = '%(asctime)10s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'

logging.basicConfig(level=LOG_LEVEL,
                    format='%(levelname)-8s %(asctime)s %(module)s:%(lineno)d %(message)s',
                    datefmt='%d.%m %H:%M:%S',
                    filename=LOG_FILE,
                    filemode='a')
logger = logging.getLogger('Clip2Zeus')

def port_is_free(port):
    """Ensures that a port is available for binding"""

    try:
        port = int(port)
        logger.debug('Testing port %s' % port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', port))
    except socket.error, err:
        logger.debug('Caught an exception: %s' % (err, ))
        logger.debug(err[0], type(err[0]))
        if err[0] in (48, 10048, 10061): # address already in use
            return False
        else:
            raise err
    else:
        logger.debug('I was able to bind to port %s... unbinding.' % port)
        sock.close()
        return True

class UnsupportedPlatformError(StandardError): pass

class Server(SimpleXMLRPCServer):
    """Wrapper to allow more graceful termination"""

    def serve_forever(self):
        self.quit = False
        while not self.quit:
            self.handle_request()

    def kill(self):
        self.quit = True

class Clip2ZeusApp(object):

    EXPOSED = ('help', 'set_interval', 'shorten_urls', 'quit')

    def __init__(self, port=DEFAULT_PORT):
        """Creates the container for common functionality"""

        logger.debug('Starting %s v%s' % (APP_TITLE, __version__))

        self.port = int(port)

        self.data = ''
        self._has_connection = False
        self.last_check = None
        self.interval = 1
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
            logger.debug('Starting server...')
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
            logger.debug('Updating interval to %s' % interval)
            self.interval = int(interval)

            if self.interval < 0:
                raise ValueError
        except (TypeError, ValueError):
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

                if usable:
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
                func(*args)
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

