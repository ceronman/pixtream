"""
Script to run the Pixtream tracker application

use run() to launch the program
"""

from optparse import OptionParser
import logging
import sys

from twisted.web import server
from twisted.internet import reactor

from pixtream.tracker.resource import RootResource

def _parse_options():
    parser = OptionParser()

    parser.add_option('-p', '--port', dest='port',
                      type='int', default=8080,
                      help='Listening Port', metavar='PORT')

    parser.add_option('-i', '--interval', dest='interval',
                      type='int', default=10,
                      help='Interval in seconds for peers to make requests',
                      metavar='INTERVAL')

    return parser.parse_args()

def _setup_logger():
    format = '%(asctime)s:%(levelname)s:%(module)s:%(lineno)d: %(message)s'
    logging.basicConfig(level = logging.DEBUG,
                        format = format,
                        stream = sys.stdout)

def run():
    """Runs the tracker application"""
    _setup_logger()
    options, _ = _parse_options()

    site = server.Site(RootResource(options.interval))
    reactor.listenTCP(options.port, site)

    print 'Tracker listening on {0.port}'.format(options)
    print 'Checking peers every {0.interval} seconds'.format(options)
    print 'Press CTRL-C to quit'

    reactor.run()

