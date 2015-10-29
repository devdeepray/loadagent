import socket
import sys
import configparser
from threading import Thread
import time
import psutil
import peewee
from peewee import *
import datetime

config = configparser.ConfigParser()
config.read('CCagent.conf')

INTERVAL = float(config['GENERAL']['interval'])
TIMEOUT = float(config['GENERAL']['timeout'])
SQLU = config['GENERAL']['sqlu']
SQLP = config['GENERAL']['sqlp']
SQLD = config['GENERAL']['sqld']

DB = MySQLDatabase(SQLD, user=SQLU, passwd=SQLP)

class DCLoadRecords(peewee.Model):
    dcip = peewee.CharField(primary_key=True)
    serveron = peewee.IntegerField()
    networkload = peewee.DoubleField()
    timestamp = peewee.DateTimeField()
    volatility = peewee.DoubleField()
    class Meta:
        database = DB

# Set up table and entries for servers if they don't exist.
try:
    DCLoadRecords.drop_table()
except Exception:
    print('Table does not exist, creating new')

DCLoadRecords.create_table()

for ip in config['DC_IP']:
    le = DCLoadRecords(dcip=config['DC_IP'][ip], networkload=0, serveron=False, timestamp=datetime.datetime.now(), volatility=1)
    le.save(force_insert=True)

# Thread for updating the table periodically by polling the DC.
def updaterThread(ip, pt):
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((ip, int(pt)))
            print('Connected to ' + ip + ' on port ' + pt)
        except Exception:
            print('Could not connect to ' + ip + ' on port ' + pt)
            time.sleep(1)
            s.close()
            continue
        while True:
            dat = DCLoadRecords(dcip=ip)
            s.send(bytes('a', "utf-8"))
            try:
                data = s.recv(128)
                dat.serveron = True
            except Exception:
                print('Connection to ' + ip + ', ' + pt + ' timed out.')
                dat.serveron = False
                dat.timestamp = datetime.datetime.now()
                dat.save()
                break
            dat.networkload = float(data.split(b':')[1])
            dat.timestamp = float()
            dat.save()
            time.sleep(1)
        s.close()

for addr, port in zip(config['DC_IP'], config['DC_PORT']):
    t = Thread( target=updaterThread, args=(config['DC_IP'][addr], config['DC_PORT'][port], ))
    t.daemon = True
    t.start()

while True:
    a = 1
