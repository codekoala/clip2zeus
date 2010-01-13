#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Monitors the system clipboard for text that contains URLs for conversion
using 2ze.us
"""

from common import *

__author__ = 'Josh VanderLinden'
__version__ = '0.8a'

def main():
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-p', '--port', dest='port', default=8000, help='The port for the daemon to listen on')
    options, args = parser.parse_args()

    params = dict(
        port=options.port,
    )

    clip2zeus = Clip2ZeusApp.for_platform()
    clip2zeus(**params).start()

if __name__ == '__main__':
    main()

