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
config.read('ADNSagent.conf')

INTERVAL = float(config['GENERAL']['interval'])
TIMEOUT = float(config['GENERAL']['interval'])
SQLU = config['GENERAL']['sqlu']
SQLP = config['GENERAL']['sqlp']

DB = MySQLDatabase('pdns', user=SQLU, passwd=SQLP)

class DCLoadRecords(peewee.Model):
    dcip = peewee.CharField(primary_key=True)
    serveron = peewee.IntegerField()
    networkload = peewee.DoubleField()
    timestamp = peewee.DateTimeField()
    volatility = peewee.DoubleField()
    class Meta:
        database = DB

#DCLoadRecords.create_table()
#le = DCLoadRecords(dcip='dc1.ipaddr', networkload=22.221, serveron=True, timestamp=datetime.datetime.now(), volatility=1)
#DCLoadRecords.create(**le)
#le.save(force_insert=True)
#le = DCLoadRecords(dcip='dc2.ipaddr', networkload=22.221, serveron=True, timestamp=datetime.datetime.now(), volatility=1)
#le.save()

def updaterThread(ip, pt):
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((ip, int(pt)))
        except Exception:
            time.sleep(1)
            s.close()
            continue
        while True:
            dat = DCLoadRecords(dcip='dc1.ipaddr')
            s.send(bytes('a', "utf-8"))
            try:
                data = s.recv(128)
                dat.serveron = True
            except Exception:
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
