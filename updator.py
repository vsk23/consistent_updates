from pox.core import core
import pox.openflow.libopenflow_01 as of
import sys
from pox.lib.revent import *
from configuration import *
from pox.lib.recoco import Timer

class Updator(EventMixin):
    
    def __init__(self):
        print("LAUNCHING UPDATE _______")
        if core.hasComponent("openflow"):
            self.listenTo(core.openflow)
        else:
            self.listenTo(core)
        print(str(core.components))
        Timer(15, self.update, recurring = False);
   
    def update(self):
        print("in update")
        
        match = of.ofp_match(in_port = 1)
        flow = of.ofp_flow_mod(match = match)
        flow.actions.append(of.ofp_action_output(port = 10))
        self.config = Configuration()
        self.config.add_flow_mod(flow,1)
        self.config.add_flow_mod(flow,2)
        core.consistent_update.update_config(self.config);
 
def launch():
    core.registerNew(Updator)
