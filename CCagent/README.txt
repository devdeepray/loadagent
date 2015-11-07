global.conf

This file contains global information about all the DC nodes and the ADNS nodes.
It contains the mapping from DC id, ADNS id to the ip addresses and ports.

CCagent.conf

This contains details like polling interval, timeouts, and the DC and ADNS
servers it needs to get data from.

ADNS_LIST = ['A1']
DC_LIST = ['D1', 'D2']
CLIENT_LIST = ['C1', 'C2', 'C3']
g_adns_ip_loads = {}
g_adns_ip_loads['A1'] = {}
g_adns_ip_loads['A1']['C1'] = 100
g_adns_ip_loads['A1']['C2'] = 100
g_adns_ip_loads['A1']['C3'] = 100
g_dc_costs = {}
g_dc_costs['D1'] = {}
g_dc_costs['D2'] = {}
g_dc_costs['D1']['C1'] =1
g_dc_costs['D1']['C2'] =2
g_dc_costs['D1']['C3'] =3
g_dc_costs['D2']['C1'] =3
g_dc_costs['D2']['C2'] =2
g_dc_costs['D2']['C3'] =1
g_dc_loads = {}
g_dc_loads['D1'] = 200
g_dc_loads['D2'] = 100
g_dc_caps = {}
g_dc_caps['D1'] = 18
g_dc_caps['D2'] = 12

Things to ask:
ADNS load and DC load corellation. We need to limit DC load, but we are taking decision on
ADNS. Thus, we need some kind of relation.
