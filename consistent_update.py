# CONSISTENT UPDATES - POX
"""
This module allows for consistent updating to a new configuration."
Configuration is specified by a list of flowmods. 
"""

from pox.core                     import core
from pox.lib.revent               import *
from pox.lib.recoco               import Timer

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
        if core.hasComponent("optimization"):
            self.listenTo(core.optimization)
        else:
            self.listenTo(core)
        self.vlan = 1;
        self.delete_interval = 5; #number of seconds to wait, need to NOT HARDCODE THIS
        return
   
    def is_external(self,dpid,port):
        sw1 = core.openflow_topology.topology.getEntityByID(dpid)
        if len(sw1.ports[port].entities) == 0:
            return 1 
        else:
            return 0

    # update_config
    # main update function that should be called to update 
    # network configuration    
    def update_config(self, config):
 
        if core.optimization.check_if_one_touch(config):
            self.one_touch_update(config)
        else:
            self.two_phase_update(config)
            self.vlan = self.vlan%4093 + 1
        return
    
    # delete_old_rules
    # removes old (previous vlan) rules that are currently installed on
    # both internal and external switches

    def delete_old_rules(self):
        print("deleting old rules with vlan : " + str(self.vlan - 1))
        flow = of.ofp_flow_mod(command = of.OFPFC_DELETE)
        flow.match.dl_vlan = self.vlan - 2; 
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

        #read all the flow mods
        for dpid,flow_mod_list in config.flowmods.iteritems():
            for flow_mod in flow_mod_list:
                flow_mod.match.dl_vlan = self.vlan 
                core.openflow.getConnection(dpid).send(flow_mod)

        #for all external ports, install vlan mod rules
        for id,sw in core.openflow_topology.topology._entities.iteritems():
            for portid in sw.ports.iterkeys():
                if self.is_external(id,portid) == 1 and portid < 10:
                    match = of.ofp_match(in_port = portid)
                    flow = of.ofp_flow_mod(match = match)
                    flow.command = of.OFPFC_MODIFY_STRICT
                    action = of.ofp_action_vlan_vid(vlan_vid = self.vlan)
                    flow.actions.append(action)
                    core.openflow.getConnection(id).send(flow)

        # Delete the old vlan rules after a certain interval
        Timer(self.delete_interval, self.delete_old_rules, recurring = False)
        return 

def launch():
    component = ConsistentUpdate()
    core.registerNew(ConsistentUpdate) 
