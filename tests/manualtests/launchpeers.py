#!/usr/bin/python

"""
Test to launch several peers at the same time
"""

import optparse
import subprocess
import os
import sys
import time

script_path = os.path.dirname(os.path.abspath(__file__))
bin_path = os.path.join(script_path, '..', '..', 'bin')

tracker_bin = os.path.join(bin_path, 'tracker')
peer_bin = os.path.join(bin_path, 'peer')
peersource_bin = os.path.join(bin_path, 'peersource')

processes = []

start_peer_port = 60000
start_streaming_port = 30000
tracker_port = 8080
tracker_interval = 30
peers_number = 1

def create_process(command, *args):
    process = subprocess.Popen([command] + list(args),
                               stdout=sys.stdout,
                               stderr=sys.stderr)
    processes.append(process)
    return process

def create_tracker():
    args = '--port={0} --interval={1}'.format(tracker_port, tracker_interval)
    args = args.split()
    p = create_process(tracker_bin, *args)
    print '**** creating tracker: ', p.pid


def create_peer(consecutive):
    port = start_peer_port + consecutive
    streaming_port = start_streaming_port + consecutive
    args = '--port={0} --streaming-port={1} http://127.0.0.1:{2}'
    args = args.format(port, streaming_port, tracker_port)
    args = args.split()
    p = create_process(peer_bin, *args)
    print '**** creating peer: ', p.pid

def killall():
    print '**** killing subprocesses:'
    for process in processes:
        print 'killing', process.pid
        process.kill()

def parse_options():
    global start_peer_port
    global start_streaming_port
    global tracker_port
    global tracker_interval
    global peers_number

    parser = optparse.OptionParser()
    parser.usage = "Usage: %prog [options] number_of_peers"

    parser.add_option('-t', '--tracker-port',
                      dest='tracker_port',
                      type='int',
                      help='Port to use with the tracker',
                      metavar='PORT',
                      default=tracker_port)

    parser.add_option('-i', '--tracker-interval',
                      dest='tracker_interval',
                      type='int',
                      help='Interval of the tracker checks in seconds',
                      metavar='INTERVAL',
                      default=tracker_interval)

    parser.add_option('-p', '--start-peer-port',
                      dest='start_peer_port',
                      type='int',
                      help='Starting listening port for the peers',
                      metavar='PORT',
                      default=start_peer_port)

    parser.add_option('-s', '--start-streaming-port',
                      dest='start_streaming_port',
                      type='int',
                      help='Starting listening port for streaming',
                      metavar='PORT',
                      default=start_streaming_port)

    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error("Wrong number of arguments")

    start_peer_port = options.start_peer_port
    start_streaming_port = options.start_streaming_port
    tracker_port = options.tracker_port
    tracker_interval = options.tracker_interval
    peers_number = int(args[0])


if __name__ == '__main__':
    try:
        parse_options()

        create_tracker()

        for i in range(peers_number):
            create_peer(i)

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        killall()

