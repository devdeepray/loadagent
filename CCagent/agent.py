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
glob_config = configparser.ConfigParser()
glob_config.read('global.conf')

INTERVAL = float(config['GENERAL']['interval'])
TIMEOUT = float(config['GENERAL']['timeout'])
DC_LIST = [x[1] for x in config['DC_ID'].items()]
ADNS_LIST = [x[1] for x in config['ADNS_ID'].items()]
DC_IP = glob_config['DC_IP_MAP']
DC_PORT = glob_config['DC_PORT_MAP']
ADNS_IP = glob_config['ADNS_IP_MAP']
ADNS_PORT = glob_config['ADNS_PORT_MAP']

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
    dc_list = config['DC_IP']
    adns_list = config['ADNS_IP']
    lpvars = {}
    for client in config['CLIENTS']['client_ids'].split(','):
        for dcid in dc_list:
            for adnsid in adns_list:
                lpvars[(client, dcid, adnsid)] = LpVariable(client + '_' + dcid + '_' + adnsid, 0, 1);




    

# Thread for updating the table periodically by polling the DC.
def dc_thread(ip, pt):
    global g_dc_loads
    g_dc_loads[ip] = 0
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
            time.sleep(INTERVAL)
        s.close()

def adns_thread(ip, pt):
    global g_adns_ip_loads
    g_adns_ip_loads[ip] = {}
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
            dat.timestamp = datetime.datetime.now()
            try:
                dat.clientloads = s.root.get_traffic()
            except Exception:
                print('Connection to ' + ip + ', ' + pt + ' timed out.')
                g_adns_ip_loads[ip] = dat
                break
            g_adns_ip_loads[ip] = dat
            time.sleep(INTERVAL)
        s.close()

# Data center threads
for dcid in DC_LIST:
    t = Thread( target=dc_thread, args=(DC_IP[dcid], DC_PORT[dcid], ))
    t.daemon = True
    t.start()
# ADNS threads
for asid in ADNS_LIST:
    t = Thread( target=adns_thread, args=(ADNS_IP[asid], ADNS_PORT[asid], ))
    t.daemon = True
    t.start()

