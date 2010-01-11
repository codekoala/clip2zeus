import subprocess
import time
from common import Clip2ZeusApp

class Clip2ZeusOSX(Clip2ZeusApp):

    def monitor_clipboard(self):
        """Regularly checks the system clipboard for data"""

        try:
            while True:
                # only bother processing if we have a connection
                if self.has_connection:
                    data = subprocess.Popen('/usr/bin/pbpaste', stdout=subprocess.PIPE).stdout.read()

                    if data != self.data:
                        self.process_clipboard(data)
                time.sleep(1)
        except KeyboardInterrupt:
            self.quit()

    def update_clipboard(self, text):
        """Updates the system clipboard with the specified text"""

        echo = subprocess.Popen(['/bin/echo', '-n', '%s' % text.replace('"', '\"')], stdout=subprocess.PIPE)
        copy = subprocess.Popen(['/usr/bin/pbcopy'], stdin=echo.stdout, stdout=subprocess.PIPE)
        output, errs = copy.communicate()

if __name__ == '__main__':
    Clip2ZeusOSX()

