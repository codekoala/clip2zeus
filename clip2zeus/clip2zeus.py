#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Monitors the system clipboard for text that contains URLs for conversion
using 2ze.us"""

from common import *

__version__ = '0.5'

def main():
    clip2zeus = Clip2ZeusApp.for_platform()
    clip2zeus()

if __name__ == '__main__':
    main()

