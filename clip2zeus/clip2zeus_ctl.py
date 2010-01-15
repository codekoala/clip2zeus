#!/usr/bin/env python
# -*- coding: utf-8 -*-

from clip2zeus.common import Clip2ZeusApp, Clip2ZeusCtl, DEFAULT_PORT

def main():
    from optparse import OptionParser
    import sys

    parser = OptionParser()
    parser.add_option('-p', '--port', dest='port', default=DEFAULT_PORT, help='The port for the daemon to listen on')
    options, args = parser.parse_args()

    if len(args) < 1:
        sys.exit('Please specify a command: %s' % ', '.join(Clip2ZeusApp.EXPOSED))

    params = dict(
        port=options.port,
    )

    Clip2ZeusCtl(**params).execute_command(args.pop(0), args)

if __name__ == '__main__':
    main()

