# This program measures the load on the DC network interfaces and creates an RPC
# server to accept requests from the CC node.
# TODO: Make a decision about where to calculate costs, on the DC and DC exports
# just cost is kind of ideal, but if we have more info at CC, we can formulate
# more elaborate LP.

import socket
import sys
import configparser
from threading import Thread
import time
import psutil
import rpyc
import argparse
import logging

args = argparse.ArgumentParser(description='Data center monitor')
args.add_argument('-c','--dcconf', help='Local config file', required=True)
args.add_argument('-l','--latency', help='Latency data', required=True)
args = vars(args.parse_args())

# Config file related things
config = configparser.ConfigParser()
config.read(args['dcconf'])

HOST = ''	# Symbolic name, meaning all available interfaces
PORT = int(config['DEFAULT']['port'])
INTERVAL = float(config['DEFAULT']['interval'])
IFACES = [x.strip() for x in config['DEFAULT']['ifaces'].split(',')]
BANDWIDTHCAP = float(config['DEFAULT']['bandwidthcap'])

# Set up logging
logging.basicConfig(filename='DC.log', level=eval('logging.'+config['DEFAULT']['log_level']))

# Global data
g_netutil = 0

# Thread that executes psutl in intervals and updates the g_netutil variable
def measurementThread(threadname):
    global g_netutil
    prev_meas_time = 0
    prev_tx = 0
    while True:
        meas_time = time.time()
        stat = psutil.net_io_counters(pernic=True)
        bytes_tx = 0
        for iface in IFACES:
            try:
                bytes_tx = bytes_tx + stat[iface].bytes_sent + stat[iface].bytes_recv
            except KeyError:
                logging.warning('Interface not found')
        g_netutil = (bytes_tx - prev_tx) / (meas_time - prev_meas_time)
        prev_tx = bytes_tx
        prev_meas_time = meas_time
        logging.debug('net util is ' + str(g_netutil))
        time.sleep(INTERVAL)

# RPC server thread
def rpcThread():
    logging.info('RPC thread started')
    class LoadMonitor(rpyc.Service):
        def on_connect(self):
            pass
        def on_disconnect(self):
            pass
        def exposed_get_load(self):
            return g_netutil
        def exposed_get_cost_data(self):
            latency = configparser.ConfigParser()
            latency.read(args['latency'])
            logging.debug('Latency data: ' + [x for x in latency.items()])
            return dict(x for x in latency['LATENCY'].items())
        def exposed_get_bandwidthcap(self):
            return BANDWIDTHCAP

    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(LoadMonitor, port = PORT)
    t.start()

if (config['DEFAULT']['experiment'] == 'True'):
    logging.info('Starting in experiment mode')
    rpcthread = Thread( target=rpcThread, args=( ) )
    rpcthread.daemon = True
    rpcthread.start()
    import readline
    import code
    vars = globals().copy()
    vars.update(locals())
    shell = code.InteractiveConsole(vars)
    shell.interact()
else:
    # Start monitoring thread to measure network usage
    monthread = Thread( target=measurementThread, args=("Thread-meas", ) )
    monthread.daemon = True
    monthread.start()
    logging.info('Network load monitor started')
    rpcThread()
