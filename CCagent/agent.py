# This is the code for the central coordinator. It basically pulls information
# from the DCs and the ADNS servers, and solves the linear program to get the
# routing tables. We then need to set up the ADNS resolver to redirect the
# load appropriately.
# Current status:
# pulls from ADNS servers
# pulls from DC servers
# TODO:
# Generate the LP and solve, find out a way to tell pdns.

import socket
import sys
from threading import Thread
import time
import psutil
import rpyc
from peewee import *
import datetime
from pulp import *
import records
import lpsolver



# Thread for building the LP and solving it
def lp_thread():
    solve_lp(ADNS_LIST, DC_LIST, CLIENT_LIST, g_adns_ip_loads, g_dc_loads)

# Thread for updating the table periodically by polling the DC.
def dc_thread(id, ip, pt):
    global g_dc_loads
    g_dc_loads[id] = 0
    while True:
        try:
            s = rpyc.connect(ip, int(pt))
            print('Connected to ' + ip + ' on port ' + pt)
        except Exception:
            print('Could not connect to ' + ip + ' on port ' + pt)
            time.sleep(1)
            continue
        while True:
            dat = DCLoadRecords(ip)
            g_dc_loads[ip] = dat
            try:
                dat.networkload = s.root.get_load()
                dat.costs = s.root.get_latency_data()
                dat.bandwidthcap = s.root.get_bandwidthcap()
                dat.serveron = True
            except Exception:
                print('Connection to ' + ip + ', ' + pt + ' timed out.')
                g_dc_loads[id] = dat
                break
            g_dc_loads[ip] = dat
            time.sleep(INTERVAL)
        s.close()

def adns_thread(id, ip, pt):
    global g_adns_ip_loads
    g_adns_ip_loads[id] = {}
    while True:
        try:
            s = rpyc.connect(ip, int(pt))
            print('Connected to ' + ip + ' on port ' + pt)
        except Exception:
            print('Could not connect to ' + ip + ' on port ' + pt)
            time.sleep(1)
            continue
        while True:
            dat = ADNSLoadRecords(ip)
            g_adns_ip_loads[id] = dat
            try:
                dat.clientloads = s.root.get_traffic()
            except Exception:
                print('Connection to ' + ip + ', ' + pt + ' timed out.')
                break
            time.sleep(INTERVAL)
        s.close()

# Data center threads
for dcid in DC_LIST:
    t = Thread( target=dc_thread, args=(dcid, DC_IP[dcid], DC_PORT[dcid], ))
    t.daemon = True
    t.start()
# ADNS threads
for asid in ADNS_LIST:
    t = Thread( target=adns_thread, args=(asid, ADNS_IP[asid], ADNS_PORT[asid], ))
    t.daemon = True
    t.start()
