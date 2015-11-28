import configparser
import argparse

args = argparse.ArgumentParser(description='ADNS agent')
args.add_argument('-c','--conf', help='Config file', required=True)
args = vars(args.parse_args())

config = configparser.ConfigParser()
config.read(args['conf'])

# Config variables
HOST = ''	# Symbolic name, meaning all available interfaces
PORT = int(config['DEFAULT']['port'])
INTERVAL = float(config['DEFAULT']['interval'])
EXPERIMENT = config['DEFAULT']['experiment'] == 'True'

# Global data storage
g_counts = {}
g_rate = {}
