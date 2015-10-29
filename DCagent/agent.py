import socket
import sys
import configparser
from threading import Thread
import time
import psutil
import rpyc

config = configparser.ConfigParser()
config.read('DCagent.conf')

HOST = ''	# Symbolic name, meaning all available interfaces
PORT = int(config['DEFAULT']['port'])
INTERVAL = float(config['DEFAULT']['interval'])
IFACES = [x.strip() for x in config['DEFAULT']['ifaces'].split(',')]
TIMEOUT = float(config['DEFAULT']['timeout'])

g_netutil = 0

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
                print ('iface not found, skipping')
        g_netutil = (bytes_tx - prev_tx) / (meas_time - prev_meas_time)
        prev_tx = bytes_tx
        prev_meas_time = meas_time
        time.sleep(INTERVAL)

print ('Starting mon thread')
# Start monitoring thread to measure network usage
monthread = Thread( target=measurementThread, args=("Thread-meas", ) )
monthread.daemon = True
monthread.start()


class LoadMonitor(rpyc.Service):
    def on_connect(self):
        pass
    def on_disconnect(self):
        pass
    def exposed_get_load(self):
        return g_netutil

from rpyc.utils.server import ThreadedServer
t = ThreadedServer(LoadMonitor, port = PORT)
t.start()
