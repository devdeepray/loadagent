import configparser

config = configparser.ConfigParser()
config.read('CCagent.conf')
glob_config = configparser.ConfigParser()
glob_config.read('global.conf')

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
DEFAULT_COST = 10
CLIENT_LIST = glob_config['CLIENTS']['client_ids'].split(',')

g_dc_loads = {}
g_adns_ip_loads = {}
