# CONSISTENT UPDATES - POX
"""
This module allows for consistent updating to a new configuration."
Configuration is specified by a list of flowmods. 
"""

from pox.core                     import core
from pox.lib.revent               import *
import pox.openflow.libopenflow_01 as of
import sys

log = core.getLogger()

class ConsistentUpdate(EventMixin):
    _core_name = "consistent_update"

    def __init__(self):
        if core.hasComponent("openflow"):
            self.listenTo(core.openflow)
        if core.hasComponent("openflow_topology"):
            self.listenTo(core.openflow_topology)
        else:
            self.listenTo(core)
        self.vlan = 2;
        return
    
    def one_touch_update(self,config):
        print(str(config.flowmods));
        for dpid,flow_mod_list in config.flowmods.iteritems():
            for flow_mod in flow_mod_list:
                core.openflow.getConnection(dpid).send(flow_mod)
        return

    def is_external(self,dpid,port):
        sw1 = core.openflow_topology.topology.getEntityByID(dpid)
        if len(sw1.ports[port].entities) == 0:
            return 1 
        else:
            return 0
    
    def update_config(self, config):
        #INSERT OPTIMIZATION CALL HERE 
        optimize = 1
        if optimize == 1:
            self.one_touch_update(config);
        if optimize == 2:
            self.two_phase_update(config,self.vlan);
            self.vlan = self.vlan + 1
        return

    def two_phase_update(self, config, new_vlan):
        #read all the flow mods
        for dpid,flow_mod_list in config.flowmods.iteritems():
            for flow_mod in flow_mod_list:
                flow_mod.match.dl_vlan = new_vlan
                core.openflow.getConnection(dpid).send(flow_mod)
        #for all external ports
        for id,sw in core.openflow_topology.topology._entities.iteritems():
            for portid in sw.ports.iterkeys():
                if self.is_external(id,portid) == 1 and portid < 10:
                    match = of.ofp_match(in_port = portid)
                    flow = of.ofp_flow_mod(match = match)
                    action = of.ofp_action_vlan_vid(vlan_vid = new_vlan)
                    flow.actions.append(action)
                    flow.actions.append(action2)
                    core.openflow.getConnection(id).send(flow)
        for con in core.openflow._connections.values();
            #send a flow mod to all the PREVIOUS vlan id version rules to timeout
        return
        

def launch():
    component = ConsistentUpdate()
    core.registerNew(ConsistentUpdate) 
