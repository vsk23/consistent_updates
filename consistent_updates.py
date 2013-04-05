from pox.core import core
from pox.lib.revent import *
import pox.openflow.libopenflow_01 as of
import sys 
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
from pox.lib.recoco import Timer

class Learning_switch(EventMixin):

    def __init__(self):
        if core.hasComponent("openflow"):
            print("has openflow component")
            self.listenTo(core.openflow)
        if core.hasComponent("openflow_discovery"):
            print("has openflow_discovery component") 
            self.listenTo(core.openflow_discovery)
        else:
            self.listenTo(core)
        #store|| Key = ether.switch Value = output port
        self.host_port_map={} 
    
    def _handle_ComponentRegistered(self, event):
        self.addListener(GoingDownEvent, _handle_GoingDownEvent)
        if event.name == "openflow":
            self.listenTo(core.openflow)
        else:
            pass
    
    # You should modify the handlers below.
    def _handle_ConnectionUp(self, event):
        pass

    def _handle_ConnectionDown(self, event):
        pass

    def _handle_FlowRemoved(self, event):
        pass

    def _handle_PortStatus(self,event):
        pass

    def _handle_StatsReply(self,event):
        pass
    
    def _handle_LinkEvent(self, event):
        link = event.link
        switch_one = link.dpid1
        port_one = link.port1 
        switch_two = link.dpid2
        port_two = link.dpid2
        
        print("there was a link event between " +  str(event.link.dpid1) + "," + str(port_one) + " and " + str(event.link.dpid1) + "," + str(port_two))
        return

    def _handle_PacketIn(self, event):
        print("In PacketIn")
        return

def launch():
    core.registerNew(Learning_switch)
  
