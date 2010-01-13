import subprocess
import time
from common import Clip2ZeusApp

class Clip2ZeusOSX(Clip2ZeusApp):

    def check_clipboard(self):
        """Checks the system clipboard for data"""

        print 'Checking in OSX'
        return subprocess.Popen('/usr/bin/pbpaste', stdout=subprocess.PIPE).stdout.read()

    def update_clipboard(self, text):
        """Updates the system clipboard with the specified text"""

        print 'Updating in OSX'
        echo = subprocess.Popen(['/bin/echo', '-n', '%s' % text.replace('"', '\"')], stdout=subprocess.PIPE)
        copy = subprocess.Popen(['/usr/bin/pbcopy'], stdin=echo.stdout, stdout=subprocess.PIPE)
        output, errs = copy.communicate()

if __name__ == '__main__':
    Clip2ZeusOSX()

