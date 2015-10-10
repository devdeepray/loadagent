import socket
import sys
import configparser
from threading import Thread
import time
import psutil

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

def handlerThread(conn):
    global g_netutil
    conn.settimeout(TIMEOUT)
    while True:
        # When signal from client, send network usage
        data = conn.recv(1)
        print(data)
        if not data:
            break
        reply = 'netrate : ' + str(g_netutil)
        conn.sendall(bytes(reply, "utf-8"))
        time.sleep(1)
    conn.close()

print ('Starting mon thread')
# Start monitoring thread to measure network usage
monthread = Thread( target=measurementThread, args=("Thread-meas", ) )
monthread.daemon = True
monthread.start()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print( 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1] )
    sys.exit()

print( 'Socket bind complete' )

#Start listening on socket
s.listen(10)
print( 'Now serving clients' )

#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
        conn, addr = s.accept()
        handler = Thread(target=handlerThread, args=(conn, ) )
        handler.daemon = True
        handler.start()
s.close()
