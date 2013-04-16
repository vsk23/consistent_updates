import Queue
from configuration import *  
import updator as up
from pox.core import core
from pox.lib.revent import *
import pox.openflow.libopenflow_01 as of
from pox.lib.recoco import Timer
import optimize as op


config1 = { 1:["flow1","flow3","flow2","flow5"]}


class Learning_switch(EventMixin):
    
    
    def __init__(self):
        if core.hasComponent("openflow"):
            print("has openflow component")
            self.listenTo(core.openflow)
        if core.hasComponent("openflow_discovery"):
            print("has openflow_discovery component") 
            self.listenTo(core.openflow_discovery)
        if core.hasComponent("openflow_topology"):
            print("has openflow_topology component") 
            self.listenTo(core.openflow_topology)
        else:
            self.listenTo(core)
        #store|| Key = ether.switch Value = output port
        self.N = 2
	self.porttable_for_switch = {}  # Array of hash tables per switch. 
        self.topo={}
        self.switches=[]
        self.flow_table={}
        self.config={}
    def _handle_ComponentRegistered(self, event):
        self.addListener(GoingDownEvent, _handle_GoingDownEvent)
        if event.name == "openflow":
            self.listenTo(core.openflow)
        else:
            pass
    
    # You should modify the handlers below.
    def _handle_ConnectionUp(self, event):
        print("has _handle_ConnectionUp") 
	switch=event.connection.dpid
        self.switches.append(switch)
	print self.switches
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
	if not self.topo.has_key(link.dpid1):
	    self.topo[link.dpid1]={}
	    self.topo[link.dpid1][link.port1]=str(link.dpid2)+ "_" +str(link.port2)
	else:
	    self.topo[link.dpid1][link.port1]=str(link.dpid2)+ "_" +str(link.port2)

	for key, value in self.topo.iteritems() :
    	       	print key, value
	return

    def _handle_PacketIn(self, event):
        print("In PacketIn")
	# Basic functionality of L2 Switch
        switch = event.dpid
	print ("Switch is " + str(switch))
	# Encountered packet from Switch: switch 
#	self.porttable_for_switch[switch] = {}	
	packet = event.parsed
        thisport= event.port
        print("PacketIn: " + str(packet))
        src = packet.src
	dst = packet.dst
	# Create a hash of the source and the assosiated port 
 	if switch not in self.porttable_for_switch:
	    self.porttable_for_switch[switch] = {}
	if src not in self.porttable_for_switch[switch]:
	    print ("Registering for Switch " +str(switch)+"MAC address" + str(src) + "at Port" + str(thisport))
	    self.porttable_for_switch[switch][src]=thisport
        

	if dst not in self.porttable_for_switch[switch]:
	    my_action = of.ofp_action_output(port=of.OFPP_FLOOD)
            my_in_port = event.port
            packetout = of.ofp_packet_out(in_port=my_in_port)  
            if event.ofp.buffer_id != -1: 
                packetout.buffer_id = event.ofp.buffer_id            
            packetout.actions.append(my_action)
	    event.connection.send(packetout)
	else:
         # modify the flow table on the switch i
	    action = of.ofp_action_output(port=self.porttable_for_switch[switch][dst])
	    match = of.ofp_match.from_packet(packet)
            print ("FROM PACKET" + str(match))
	    match.in_port = event.port
            flow = of.ofp_flow_mod(match=match)
	    flow.command = of.OFPFC_ADD
            flow.idle_timeout = of.OFP_FLOW_PERMANENT
            flow.hard_timeout = of.OFP_FLOW_PERMANENT
            flow.priority = 65535
            flow.actions.append(action)
            if event.ofp.buffer_id != -1: 
                flow.buffer_id = event.ofp.buffer_id            
            event.connection.send(flow)
	    print("FLOW MATCH  " +str(flow.match))		
	    print("FLOW   " +str(flow))		
            if switch not in self.flow_table:
                self.flow_table[switch]=[]
            
            self.flow_table[switch].append(flow)
            print self.flow_table
	    match2 = of.ofp_match(in_port = 1)
            flow2 = of.ofp_flow_mod(match = match2)
            flow2.actions.append(of.ofp_action_output(port = 10))
	    self.config[2]=[flow2]          
            print self.config
	on_tc=op.check_one_touch(self.topo,self.config,self.flow_table)	
	print "can I one touch? " + str(on_tc)

def launch():
    core.registerNew(Learning_switch)


def match_packet(config,switch,flowstate,neigh):
    print config
    print flowstate
    packet_match_conf=[]
    packet_match_nwstate=[]
    for flowmod in config[switch]:
        packet_match_conf.append(flowmod.match)
    for next_sw in neigh:
        print next_sw,neigh 
        for flowmod in flowstate[next_sw]: 
            packet_match_nwstate.append(flowmod.match)
    
    print packet_match_conf,packet_match_nwstate
     
    for ob in packet_match_conf:
	for ob1 in packet_match_nwstate:
            print ob.next, ob1.next
            print ob.__dict__, ob1.__dict__
            print ob.__dict__ == ob1.__dict__
		
#    b3 = [val for val.next in packet_match_conf if val.next in packet_match_nwstate]    
#    print "b3"
#    print b3




def one_touch_test1():
    print("in update")
    match = of.ofp_match(in_port = 1)
    flow = of.ofp_flow_mod(match = match)
    flow.actions.append(of.ofp_action_output(port = 10))
    config = Configuration()
    config.add_flow_mod(flow,1)
    config.add_flow_mod(flow,2)
    return config 

