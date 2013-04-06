# two phase update
# one touch update

class Configuration:

    def __init__(self):
        #set of flowmdos by switch id
        self.flowmods={}
        return

    def add_flow_mod(ofp_flow_mod mod, int dpid):
        if dpid in self.flowmods:
            self.flowmods.[dpid].append(mod)
        else:
            self.flowmods.[dpid] = [mod]
        return
class ConsistentUpdates(EventMixin):
    
    def __init__(self):
        if core.hasComponent("openflow"):
            self.listenTo(core.openflow)
        else:
            self.listenTo(core)

    def update_config(Configuration config):
        #pass to optimizer for optimizations
        one_touch_update(config);
        return

    def two_phase_update(Configuration config):
        #read all the flow mods

    def one_touch_update(Configuration config):
        for dpid,flow_mod_list in config.flowmods:  
                    
