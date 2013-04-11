class Configuration:

    def __init__(self):
        #set of flowmdos by switch id
        self.flowmods={}
        return

    def add_flow_mod(self, mod, dpid):
        if dpid in self.flowmods:
            self.flowmods[dpid].append(mod)
        else:
            self.flowmods[dpid] = [mod]
        return
