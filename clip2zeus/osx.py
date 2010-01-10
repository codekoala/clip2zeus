from AppKit import *
import time
from common import Clip2ZeusApp

class Clip2ZeusOSX(Clip2ZeusApp):

    def __init__(self):
        super(Clip2ZeusOSX, self).__init__()

        self.pb = NSPasteboard.generalPasteboard()

    def monitor_clipboard(self):
        """Regularly checks the system clipboard for data"""

        try:
            while True:
                # only bother processing if we have a connection
                if self.has_connection:
                    data = self.pb.stringForType_(NSStringPboardType).mutableCopy()

                    if data != self.data:
                        self.process_clipboard(data)
                time.sleep(1)
        except KeyboardInterrupt:
            self.quit()

    def update_clipboard(self, text):
        """Updates the system clipboard with the specified text"""

        self.pb.declareTypes_owner_([NSStringPboardType], None)
        self.pb.setString_forType_(text, NSStringPboardType)

