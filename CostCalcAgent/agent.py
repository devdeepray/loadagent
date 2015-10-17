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
config.read('Costagent.conf')

INTERVAL = float(config['GENERAL']['interval'])
SQLU = config['GENERAL']['sqlu']
SQLP = config['GENERAL']['sqlp']
SQLD = config['GENERAL']['sqld']

DB = MySQLDatabase(SQLD, user=SQLU, passwd=SQLP)

def calcCost(loadrecord):
	return loadrecord.networkload

class DCLoadRecords(peewee.Model):
	dcip = peewee.CharField(primary_key=True)
	serveron = peewee.IntegerField()
	networkload = peewee.DoubleField()
	timestamp = peewee.DateTimeField()
	volatility = peewee.DoubleField()
	class Meta:
		database = DB

class DCCostRecords(peewee.Model):
	dcip = peewee.CharField(primary_key=True)
	cost = peewee.DoubleField()
	class Meta:
		database = DB


# Set up table and entries for servers if they don't exist.
try:
	DCLoadRecords.create_table()
except Exception:
	print('Load table already exists, skipping creation')

try:
	DCCostRecords.create_table()
except Exception:
	print('Cost table already exists, skipping creation')

while True:
	for loadrecord in DCLoadRecords.select():
		costval = calcCost(loadrecord)
		costrecord, created = DCCostRecords.get_or_create(dcip=loadrecord.dcip, defaults={'cost' : 0});
		costrecord.cost = costval
		costrecord.save();

