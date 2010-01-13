#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common import Clip2ZeusApp, Clip2ZeusCtl

def main():
    from optparse import OptionParser
    import sys

    parser = OptionParser()
    parser.add_option('-p', '--port', dest='port', default=8000, help='The port for the daemon to listen on')
    options, args = parser.parse_args()

    if len(args) < 1:
        sys.exit('Please specify a command: %s' % ', '.join(Clip2ZeusApp.EXPOSED))

    params = dict(
        cmd=args.pop(0),
        args=args,
        port=options.port,
    )

    Clip2ZeusCtl(**params)

if __name__ == '__main__':
    main()

