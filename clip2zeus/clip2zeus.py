#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Monitors the system clipboard for text that contains URLs for conversion
using 2ze.us"""

from common import *

__version__ = '0.7a'

def main():
    clip2zeus = Clip2ZeusApp.for_platform()
    clip2zeus().start()

if __name__ == '__main__':
    main()

