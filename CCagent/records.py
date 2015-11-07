class DCLoadRecords:
    def __init__(self, ip):
        self.dcip = ip
        self.serveron = False
        self.networkload = 0
        self.timestamp = datetime.datetime.now()
        self.costs = {}
        self.bandwidthcap = 0
    def __repr__(self):
        return "ip: " + self.dcip + " load: " + str(self.networkload)

class ADNSLoadRecords:
    def __init__(self, ip):
        self.adnsip = ip
        self.clientloads = {}
        self.timestamp = datetime.datetime.now()
    def __repr__(self):
        return "ip: " + self.adnsip + " load: " + str(self.clientloads)
