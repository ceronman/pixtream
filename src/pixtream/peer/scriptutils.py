"""
Utilities for creating Pixtream Peer scripts
"""

from optparse import OptionParser
import logging
import sys

__all__ = ['parse_options', 'parse_source_options', 'setup_logger']


def _creat_basic_options(parser):
    parser.add_option('-i', '--ip', dest='ip',
                      type='string',
                      help='IP Address to use', metavar='ADDRESS')

    parser.add_option('-p', '--port', dest='port',
                      type='int', default=60000,
                      help='Listening Port', metavar='PORT')

    parser.add_option('-s', '--streaming-port', dest='streaming_port',
                      type='int', default=30000,
                      help='Listening Port for the streaming output',
                      metavar='PORT')

def parse_options():
    parser = OptionParser()
    parser.usage = "usage: %prog [options] tracker_url"
    _creat_basic_options(parser)

    options, args = parser.parse_args()

    if len(args) == 0:
        parser.error('Missing tracker argument')

    if len(args) != 1:
        parser.error('Too much arguments')

    return options.ip, options.port, options.streaming_port, args[0]

def parse_source_options():
    parser = OptionParser()
    parser.usage = "usage: %prog [options] tracker_url source_type source\n" \
                   "Source Types: http, file, tcp\n" \
                   "Examples:\n" \
                   "$ %prog http://tracker.com http http://source.com:8080\n" \
                   "$ %prog http://tracker.com file /var/song.mp3\n" \
                   "$ %prog http://tracker.com tcp 192.168.1.10:30000"

    _creat_basic_options(parser)

    options, args = parser.parse_args()

    if len(args) == 0:
        parser.error('Missing tracker argument')

    if len(args) != 3:
        parser.error('Wrong number of arguments')

    tracker_url, source_type, source = args

    if source_type not in ('http', 'file', 'tcp'):
        parser.error('Invalid source type')

    return (options.ip, options.port, options.streaming_port,
            tracker_url, source_type, source)

def setup_logger():
    # TODO: use configuration option for file logging
    format = '[%(asctime)s][%(process)d][%(levelname)s][%(module)s][%(lineno)d] %(message)s'
    logging.basicConfig(level = logging.DEBUG,
                        format = format,
                        stream = sys.stdout)


