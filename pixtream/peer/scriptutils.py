"""
Utilities for creating Pixtream Peer scripts
"""

from optparse import OptionParser
import logging
import sys

def parse_options():
    parser = OptionParser()
    parser.usage = "usage: %prog [options] tracker_url"

    parser.add_option('-i', '--ip', dest='ip',
                      type='string',
                      help='IP Address to use', metavar='ADDRESS')

    parser.add_option('-p', '--port', dest='port',
                      type='int', default=60000,
                      help='Listening Port', metavar='PORT')

    parser.get_usage()

    options, args = parser.parse_args()

    if len(args) == 0:
        parser.error('Missing tracker argument')

    if len(args) > 1:
        parser.error('Too much arguments')

    return options.ip, options.port, args[0]

def setup_logger():
    # TODO: use configuration option for file logging
    format = '%(asctime)s:%(levelname)s:%(module)s:%(lineno)d: %(message)s'
    logging.basicConfig(level = logging.DEBUG,
                        format = format,
                        stream = sys.stdout)


