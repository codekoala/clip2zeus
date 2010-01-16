from SimpleXMLRPCServer import SimpleXMLRPCServer
import logging
import socket

#
# Utilities
#

class Server(SimpleXMLRPCServer):
    """Wrapper to allow more graceful termination"""

    def serve_forever(self):
        self.quit = False
        while not self.quit:
            self.handle_request()

    def kill(self):
        self.quit = True

def get_logger():
    from clip2zeus.config import LOG_LEVEL, LOG_FORMAT, LOG_FILE
    logging.basicConfig(level=LOG_LEVEL,
                        format=LOG_FORMAT,
                        datefmt='%d.%m %H:%M:%S',
                        filename=LOG_FILE,
                        filemode='a')
    return logging.getLogger('Clip2Zeus')

logger = get_logger()

def port_is_free(port=None):
    """Ensures that a port is available for binding"""

    if port is None:
        from clip2zeus.config import config
        port = config.get('main', 'port')

    try:
        port = int(port)
        logger.debug('Testing port %s' % (port,))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', port))
    except socket.error, err:
        logger.debug('Caught an exception: %s' % (err,))
        if err[0] in (98, 48, 10048, 10061): # address already in use
            return False
        else:
            raise err
    else:
        logger.debug('Port %s is available. Unbinding.' % (port,))
        sock.close()
        return True

#
# Exceptions
#

class UnsupportedPlatformError(StandardError):
    pass

