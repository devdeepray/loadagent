
# The mapping function from ip address to client region
def ip2section(ipaddr):
    sp = ipaddr.split('.')
    return sp[0] + '.' + sp[1]
