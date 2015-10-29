import socket, sys
from struct import *
import configparser
from threading import Thread
import time
import rpyc

config = configparser.ConfigParser()
config.read('TMon.conf')

HOST = ''	# Symbolic name, meaning all available interfaces
PORT = int(config['DEFAULT']['port'])
INTERVAL = float(config['DEFAULT']['interval'])
IFACES = [x.strip() for x in config['DEFAULT']['ifaces'].split(',')]
TIMEOUT = float(config['DEFAULT']['timeout'])

g_counts = {}
g_rate = {}

def ip2section(ipaddr):
    sp = ipaddr.split('.')
    return sp[0] + '.' + sp[1]

def count(section):
    if section in g_counts:
        g_counts[section] = g_counts[section] + 1
    else:
        g_counts[section] = 1

def eth_addr (a) :
    b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (a[0] , a[1] , a[2], a[3], a[4] , a[5])
    return b

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

def measure_thread():
    #create an INET, STREAMing socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    except socket.error as msg:
        print('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    while True:
        packet = s.recvfrom(65565)
        #packet string from tuple
        packet = packet[0]
        #parse ethernet header
        ip_length = 20
        ip_header = packet[:ip_length]
        iph = unpack('!BBHHHBBH4s4s' , ip_header)
        count(ip2section(socket.inet_ntoa(iph[8])))

def handlerThread(conn):
    global g_rate
    conn.settimeout(TIMEOUT)
    while True:
        # When signal from client, send network usage
        data = conn.recv(1)
        if not data:
            break
        reply = str(g_rate)
        conn.sendall(bytes(reply, "utf-8"))
    conn.close()

measthread = Thread( target=measure_thread, args=())
measthread.daemon = True

monthread = Thread( target=calc_rate, args=() )
monthread.daemon = True

measthread.start()
monthread.start()

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
