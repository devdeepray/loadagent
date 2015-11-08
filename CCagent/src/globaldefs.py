import configparser
import argparse

args = argparse.ArgumentParser(description='Central coordinating agent')
args.add_argument('-lc','--localconf', help='Local config file', required=True)
args.add_argument('-gc','--globalconf', help='Global config file', required=True)
args = vars(args.parse_args())

config = configparser.ConfigParser()
config.read(args['localconf'])
glob_config = configparser.ConfigParser()
glob_config.read(args['globalconf'])

# Local CC config
INTERVAL = float(config['GENERAL']['interval'])
TIMEOUT = float(config['GENERAL']['timeout'])
DC_LIST = [x[1] for x in config['DC_ID'].items()]
ADNS_LIST = [x[1] for x in config['ADNS_ID'].items()]

# Global mappings
DC_IP = glob_config['DC_IP_MAP']
DC_PORT = glob_config['DC_PORT_MAP']
ADNS_IP = glob_config['ADNS_IP_MAP']
ADNS_PORT = glob_config['ADNS_PORT_MAP']
DEFAULT_COST = float(glob_config['PARAMS']['def_cost'])
CLIENT_LIST = glob_config['CLIENTS']['client_ids'].split(',')
LOAD_MULTIPLIER = float(glob_config['PARAMS']['load_multiplier'])


g_dc_loads = {}
g_adns_ip_loads = {}
