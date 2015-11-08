from pulp import *

def solve_lp(ADNS_LIST, DC_LIST, CLIENT_LIST, adns_ip_loads, dc_client_costs, dc_bw_caps, load_multiplier):
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
                m = adns_ip_loads[adnsid][client]
            except Exception:
                m = 0
            for dc in DC_LIST:
                varid = client + '_' + dc + '_' + adnsid
                try:
                    dc_cost = dc_client_costs[dc][client]
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

    for dcid in DC_LIST:
        curvars = dict((client + '_' + dcid + '_' + adnsid,
                                adns_ip_loads[adnsid][client])
                    for client in CLIENT_LIST for adnsid in ADNS_LIST)
        prob += lpSum([lb_vars[i] * (curvars[i] * load_multiplier)
                        for i in curvars]) <= dc_bw_caps[dcid], "bandwid constraint for " + dcid


    prob.writeLP("LBlp.lp")
    prob.solve()
    print(LpStatus[prob.status])
    # Each of the variables is printed with it's resolved optimum value
    for v in prob.variables():
        print(v.name, "=", v.varValue)
