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
import configparser
from threading import Thread
import time
import psutil
import rpyc
from peewee import *
import datetime
from pulp import *

config = configparser.ConfigParser()
config.read('CCagent.conf')

INTERVAL = float(config['GENERAL']['interval'])
TIMEOUT = float(config['GENERAL']['timeout'])

class LPInfo:
    def __init__(self):
        self.costmatrix = {}
        self.adnsclientsplit = {}
        self.adnsloadfraction = {}
        self.totaladnsload = 0

class DCLoadRecords:
    def __init__(self, ip):
        self.dcip = ip
        self.serveron = False
        self.networkload = 0
        self.timestamp = datetime.datetime.now()
        self.volatility = 1
    def __repr__(self):
        return "ip: " + self.dcip + " load: " + str(self.networkload)

class ADNSLoadRecords:
    def __init__(self, ip):
        self.adnsip = ip
        self.clientloads = {}
        self.timestamp = datetime.datetime.now()
    def __repr__(self):
        return "ip: " + self.adnsip + " load: " + str(self.clientloads)

g_dc_loads = {}
g_adns_ip_loads = {}
g_dc_costs = {}


# Thread for building the LP and solving it
def lp_thread():
    prob = LpProblem("LB problem", LpMinimize)
    # Define the LP variables
    

# Thread for updating the table periodically by polling the DC.
def dc_thread(ip, pt):
    global g_dc_loads
    while True:
        try:
            s = rpyc.connect(ip, int(pt))
            print('Connected to ' + ip + ' on port ' + pt)
        except Exception:
            print('Could not connect to ' + ip + ' on port ' + pt)
            time.sleep(1)
            s.close()
            continue
        while True:
            dat = DCLoadRecords(ip)
            dat.serveron = False
            dat.timestamp = datetime.datetime.now()
            dat.networkload = 0
            try:
                dat.networkload = s.root.get_load()
                dat.serveron = True
            except Exception:
                print('Connection to ' + ip + ', ' + pt + ' timed out.')
                g_dc_loads[ip] = dat
                break
            g_dc_loads[ip] = dat
            time.sleep(1)
        s.close()

def adns_thread(ip, pt):
    while True:
        try:
            s = rpyc.connect(ip, int(pt))
            print('Connected to ' + ip + ' on port ' + pt)
        except Exception:
            print('Could not connect to ' + ip + ' on port ' + pt)
            time.sleep(1)
            s.close()
            continue
        while True:
            dat = ADNSLoadRecords(ip)
            dat.timestamp = datetime.datetime.now()
            try:
                dat.clientloads = s.root.get_traffic()
            except Exception:
                print('Connection to ' + ip + ', ' + pt + ' timed out.')
                g_adns_ip_loads[ip] = dat
                break
            g_adns_ip_loads[ip] = dat
            time.sleep(1)
        s.close()

# Data center threads
for addr, port in zip(config['DC_IP'], config['DC_PORT']):
    t = Thread( target=dc_thread, args=(config['DC_IP'][addr], config['DC_PORT'][port], ))
    t.daemon = True
    t.start()
# ADNS threads
for addr, port in zip(config['ADNS_IP'], config['ADNS_PORT']):
    t = Thread( target=adns_thread, args=(config['ADNS_IP'][addr], config['ADNS_PORT'][port], ))
    t.daemon = True
    t.start()

