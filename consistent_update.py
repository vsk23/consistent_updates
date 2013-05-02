# CONSISTENT UPDATES - POX
"""
This module allows for consistent updating to a new configuration."
Configuration is specified by a list of flowmods. 
"""

from pox.core                     import core
from pox.lib.revent               import *
from pox.lib.recoco               import Timer
from pox.lib.addresses import IPAddr
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
        self.vlan = 1;
        self.CONTROLLER_PORT_ID = 65534
        self.delete_interval = 5; #number of seconds to wait, need to NOT HARDCODE THIS
        return
  
    def is_external_switch(self,dpid):
        sw1 = core.openflow_topology.topology.getEntityByID(dpid)
        for portid, port in sw1.ports.items():
            if not(portid == self.CONTROLLER_PORT_ID):
                if len(port.entities) == 0:
                    return 1
        return 0
 
    def is_external(self,dpid,port):
        sw1 = core.openflow_topology.topology.getEntityByID(dpid)
        return len(sw1.ports[port].entities) == 0

    def update_config(self, config):
        #INSERT OPTIMIZATION CALL HERE 
        optimization = 2 
        if optimization == 1:
            self.one_touch_update(config)
        else:
            self.two_phase_update(config)
            self.vlan = self.vlan%4093 + 1
        return

    
    # delete_old_rules
    # removes old (previous vlan) rules that are currently installed on
    # both internal and external switches
    
    def delete_old_rules(self):
        flow = of.ofp_flow_mod(command = of.OFPFC_DELETE_STRICT)
        flow.match.dl_vlan = self.vlan - 1; 
        for con in core.openflow._connections.values():
            con.send(flow); 
 
    # one_touch_update
    # installs the given flow mods on the appropriate switched using a one
    # touch update 
    def one_touch_update(self, config):
        for dpid,flow_mod_list in config.flowmods.iteritems():
            for flow_mod in flow_mod_list:
                flow_mod.match.dl_vlan = self.vlan;
                core.openflow.getConnection(dpid).send(flow_mod)
        return

    # two_phase_update
    # installs the given flow mods on the appropriate switches
    # first, it installs rules with a new vlan id on the internal switches
    # second, it installs vlan mod rules to external switches to modify
    # appropriately
    def two_phase_update(self, config):
        for dpid, flow_mod_list in config.flowmods.iteritems():
            switch = core.openflow_topology.topology.getEntityByID(dpid);
            # If switch is fully internal
            if not self.is_external_switch(dpid):
                for flow_mod in flow_mod_list:
                    flow_mod.match.dl_vlan = self.vlan
                    core.openflow.getConnection(dpid).send(flow_mod)
            else:
                for flow in flow_mod_list:
                    if not(flow.match.in_port == self.CONTROLLER_PORT_ID):
                        # Incomping port is external
                        if self.is_external(dpid, flow.match.in_port):
                            flow.dl_vlan = self.vlan
                            flow.actions.insert(0,of.ofp_action_vlan_vid(vlan_vid = self.vlan))
                        else:
                            actions = list(flow.actions)
                            for action in actions:
                                if isinstance(action, of.ofp_action_output):
                                    # Outbound port is external
                                    if self.is_external(dpid, action.port):
                                        flow.actions.insert(0,of.ofp_action_header(type = of.OFPAT_STRIP_VLAN))
                                    else:
                                        flow.match.dl_vlan = self.vlan
                        core.openflow.getConnection(dpid).send(flow)

        # Delete the old vlan rules after a certain interval
        Timer(self.delete_interval, self.delete_old_rules, recurring = False)
        return 

def launch():
    component = ConsistentUpdate()
    core.registerNew(ConsistentUpdate) 
