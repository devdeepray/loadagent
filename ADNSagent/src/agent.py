# This is the ADNS agent. It sniffs packets and keeps count of how many packets
# arrived from each region.

import socket, sys
from struct import *
import configparser
from threading import Thread
import time
import rpyc
from ipmapper import *
from globaldefs import *

# Record a packet from a particular region
def count(section):
    if section in g_counts:
        g_counts[section] = g_counts[section] + 1
    else:
        g_counts[section] = 1

# Calculates the rate of packets per unit interval
def calc_rate():
    global g_counts
    global g_rate
    while True:
        tmp = {}
        for addr, count in g_counts.items():
            tmp[addr] = count / INTERVAL
        g_rate = tmp
        g_counts = {}
        time.sleep(INTERVAL)
        print(str(g_rate))

# Packet sniffing thread
def measure_thread():
    #create an INET, STREAMing socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    except socket.error as msg:
        print('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    while True:
        packets = s.recvfrom(65565)
        #packet string from tuple
        packet = packets[0]
        #parse ethernet header
        ip_length = 20
        ip_header = packet[:ip_length]
        iph = unpack('!BBHHHBBH4s4s' , ip_header)
        count(ip2section(socket.inet_ntoa(iph[8])))

def rpcThread():
    class TrafficMonitor(rpyc.Service):
        def on_connect(self):
            pass
        def on_disconnect(self):
            pass
        def exposed_get_traffic(self):
            return g_rate

    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(TrafficMonitor, port = PORT)
    t.start()

if EXPERIMENT:
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

measthread = Thread( target=measure_thread, args=())
measthread.daemon = True

monthread = Thread( target=calc_rate, args=() )
monthread.daemon = True

measthread.start()
monthread.start()
