from pulp import *

def solve_lp(ADNS_LIST, DC_LIST, CLIENT_LIST, g_adns_ip_loads, g_dc_costs, g_dc_caps, g_dc_loads):
    prob = LpProblem("LB problem", LpMinimize)
    # Define the LP variables
    # weights:
    # Bk is the load proportion on adns k
    # aik is the fraction of traffic from i at k
    # cost ij is the

    costs = {}
    for adnsid in ADNS_LIST:
        for client in CLIENT_LIST:
            try:
                m = g_adns_ip_loads[adnsid][client]
            except Exception:
                m = 0
            for dc in DC_LIST:
                varid = client + '_' + dc + '_' + adnsid
                try:
                    dc_cost = g_dc_costs[dc][client]
                except Exception:
                    dc_cost = DEFAULT_COST
                costs[varid] = dc_cost * m;

    lb_vars = LpVariable.dicts("Lb", [varid for varid in costs], 0, 1)
    prob += lpSum([costs[i] * lb_vars[i] for i in costs]), "Total cost to minimize"

    # add sum over servers = 1 constraint.
    for adnsid in ADNS_LIST:
        for client in CLIENT_LIST:
            curvars = [client + '_' + dc + '_' + adnsid for dc in DC_LIST]
            prob += lpSum([lb_vars[i] for i in curvars]) == 1, "Distribution fraction sum constraint for " + adnsid + client

    # Need to get multiplicative factor for ADNS load to server load proportion
    # This is total DC load by total ADNS load.

    tot_adns_load = 0
    for adns in g_adns_ip_loads:
        loads = g_adns_ip_loads[adns]
        for client in loads:
            tot_adns_load = tot_adns_load + loads[client]
    tot_dc_load = 0
    for dc in g_dc_loads:
        tot_dc_load = tot_dc_load + g_dc_loads[dc]
    bandwidthfactor = tot_dc_load / tot_adns_load
    for dcid in DC_LIST:
        curvars = dict((client + '_' + dcid + '_' + adnsid,
                                g_adns_ip_loads[adnsid][client])
                    for client in CLIENT_LIST for adnsid in ADNS_LIST)
        prob += lpSum([lb_vars[i] * (curvars[i] * bandwidthfactor)
                        for i in curvars]) <= g_dc_caps[dcid], "bandwid constraint for " + dcid


    prob.writeLP("LBlp.lp")
    prob.solve()
    print(LpStatus[prob.status])
    # Each of the variables is printed with it's resolved optimum value
    for v in prob.variables():
        print(v.name, "=", v.varValue)
