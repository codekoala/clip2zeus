#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Monitors the system clipboard for text that contains URLs for conversion
using 2ze.us
"""

from clip2zeus.common import *

def main():
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-p', '--port', dest='port', default=DEFAULT_PORT, help='The port for the daemon to listen on')
    options, args = parser.parse_args()

    params = dict(
        port=options.port,
    )

    clip2zeus = Clip2ZeusApp.for_platform()
    clip2zeus(**params).start()

if __name__ == '__main__':
    main()

