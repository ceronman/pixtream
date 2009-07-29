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
trickle_bin = 'trickle'
netcat_bin = 'nc'

processes = []
files = []

start_peer_port = 60000
start_streaming_port = 30000
tracker_port = 8080
tracker_interval = 30
peers_number = 1
media_server_rate = 30 # KB/s
media_server_port = 3000
media_file = os.path.join(script_path, 'test.ogg')
use_stdout = True

def create_process(command, args, name, stdin=None):

    output = open('{0}.output'.format(name), 'w')
    process = subprocess.Popen([command] + list(args),
                               stdin=sys.stdin if stdin is None else stdin,
                               stdout=sys.stdout,
                               stderr=subprocess.STDOUT)
    processes.append(process)
    files.append(output)
    if stdin is not None:
        files.append(stdin)
    return process

def create_tracker():
    args = '--port={0} --interval={1}'.format(tracker_port, tracker_interval)
    args = args.split()
    p = create_process(tracker_bin, args, 'tracker')
    print '**** creating tracker:\t\t', p.pid


def create_peer(consecutive):
    port = start_peer_port + consecutive + 1
    streaming_port = start_streaming_port + consecutive + 1
    args = '--port={0} --streaming-port={1} http://127.0.0.1:{2}'
    args = args.format(port, streaming_port, tracker_port)
    args = args.split()
    p = create_process(peer_bin, args, 'peer{0}'.format(consecutive))
    print '**** creating peer:\t\t', p.pid

def create_source_peer():
    port = start_peer_port
    streaming_port = start_streaming_port
    args = '--port={0} --streaming-port={1} http://127.0.0.1:{2} {3} {4}'
    args = args.format(port, streaming_port, tracker_port, '127.0.0.1',
                       media_server_port)
    args = args.split()
    p = create_process(peersource_bin, args, 'peer_source')
    print '**** creating source peer:\t', p.pid

def create_media_server():
    input_file = open(media_file, 'rb')

    args = '-d {0} {1} -l -p {2}'.format(media_server_rate, netcat_bin,
                                         media_server_port)

    args = args.split()
    p = create_process(trickle_bin, args, 'mediaserver', stdin=input_file)
    print '**** creating media server:\t', p.pid

def killall():
    print '**** killing subprocesses:'
    for process in processes:
        print 'killing', process.pid
        process.kill()

def closefiles():
    print '**** closing open files:'
    for file in files:
        print 'closing', file.name
        file.close()

def parse_options():
    global start_peer_port
    global start_streaming_port
    global tracker_port
    global tracker_interval
    global peers_number
    global media_server_rate
    global media_server_port
    global media_file

    parser = optparse.OptionParser()
    parser.usage = "Usage: %prog [options] numpeers mediafile"

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

    parser.add_option('-r', '--media-server-rate',
                      dest='media_server_rate',
                      type='int',
                      help='Media server upload rate in KB/s',
                      metavar='RATE',
                      default=media_server_rate)

    parser.add_option('-m', '--media-server-port',
                      dest='media_server_port',
                      type='int',
                      help='Media server listening port',
                      metavar='PORT',
                      default=media_server_port)

    options, args = parser.parse_args()

    if len(args) != 2:
        parser.error("Wrong number of arguments")

    start_peer_port = options.start_peer_port
    start_streaming_port = options.start_streaming_port
    tracker_port = options.tracker_port
    tracker_interval = options.tracker_interval
    media_server_rate = options.media_server_rate
    media_server_port = options.media_server_port
    peers_number = int(args[0])
    media_file = args[1]


if __name__ == '__main__':
    try:
        parse_options()

        create_media_server()
        create_tracker()
        create_source_peer()

        for i in range(peers_number):
            create_peer(i)

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        killall()
        closefiles()

