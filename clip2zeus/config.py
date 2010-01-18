from ConfigParser import SafeConfigParser
import logging
import os
import re

CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.clip2zeus')

try:
    os.makedirs(CONFIG_DIR)
except:
    pass # directory already exists

CONFIG_FILE = os.path.join(CONFIG_DIR, 'clip2zeus.conf')

class Clip2ZeusConfig(SafeConfigParser):

    __instance = None

    def get(self, section, option, default=None):
        """Allows default values to be returned if necessary"""

        if self.has_section(section) and self.has_option(section, option):
            return SafeConfigParser.get(self, section, option)
        else:
            return default

    def getint(self, section, option, default=''):
        """Returns an integer"""

        return int(self.get(section, option, default))

    def getfloat(self, section, option, default=''):
        """Returns a float"""

        return float(self.get(section, option, default))

    def getboolean(self, section, option, default=''):
        """Returns a boolean"""

        return bool(self.get(section, option, default))

    def set(self, section, option, value):
        """Sets some configuration value and persists to disk"""

        if not self.has_section(section):
            self.add_section(section)

        SafeConfigParser.set(self, section, option, str(value))
        self.write(open(CONFIG_FILE, 'w'))

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            # make sure the file exists
            if not os.path.exists(CONFIG_FILE):
                open(CONFIG_FILE, 'w')

            cls.__instance = Clip2ZeusConfig()
            cls.__instance.read(open(CONFIG_FILE))

        return cls.__instance

config = Clip2ZeusConfig.instance()

DELIM = ' \n\r<>"\''
URL_RE = re.compile('((\w+)://([^/%%%s]+)(/?[^%s]*))' % (DELIM, DELIM), re.I | re.M)
INVALID_DOMAINS = ('2ze.us', 'bit.ly', 'tinyurl.com', 'tr.im', 'is.gd')

# Interval to ensure we have a connection to 2ze.us (seconds)
HEARTBEAT_INT = config.getint('main', 'heartbeat', 30)
# Number of seconds to wait on 2ze.us before giving up
TIMEOUT_SEC = config.getint('main', 'timeout', 10)
DEFAULT_PORT = config.getint('main', 'port', 14694)

#
# Logging
#

LOG_FILE = os.path.join(CONFIG_DIR, 'clip2zeus.log')
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(levelname)-8s %(asctime)s [%(process)d]%(module)s:%(lineno)d %(message)s'

