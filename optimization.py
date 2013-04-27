import Queue
from configuration import *  
import updator as up
from pox.core import core
from pox.lib.revent import *
import pox.openflow.libopenflow_01 as of
from pox.lib.recoco import Timer

class Optimization(EventMixin):
    _core_name = "optimization"
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
        self.N = 2
	self.porttable_for_switch = {}  # Array of hash tables per switch. 
	self.flow_table = {}
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
	switch=event.connection.dpid
        self.switches.append(switch)
 	pass

    def _handle_ConnectionDown(self, event):
        pass

    def _handle_FlowRemoved(self, event):
        switch=event.connection.dpid
	flow_removed = event.ofp
        for entry in self.flow_table[switch]:
            if(flow_removed.match == entry.match and flow_removed.priority == entry.priority):
                self.flow_table[switch].remove(entry)
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
	return


    def _handle_FlowMod(self,event):
	print ("I Enter")
    def _handle_PacketIn(self, event):
        print("In PacketIn")
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
	#Dummy flwo populated
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


    def check_if_one_touch(self,config1):
	config=config1.flowmods
        one_switch = len(config)
	if one_switch is not 1:
	    return
	for key,value in config.iteritems(): 
	    switch=key
	sw1 = core.openflow_topology.topology.getEntityByID(switch)
        print sw1,sw1.ports
        print sw1.flow_table
	for portid1,portvalue in sw1.ports.iteritems():
	    print  portid1,portvalue
	    for neigh in portvalue.entities:	    
	        print str(portid1) + " is connected to "
 	        print neigh
		for id,sw in core.openflow_topology.topology._entities.iteritems():
                    if sw == neigh:
                        neigh=id    
	        if neigh in self.flow_table:
                    my_flows=self.flow_table[neigh]
	            for flow in my_flows:
		        my_action=flow.actions
		        my_match=flow.match
			for acts in my_action:
			    print acts,my_match,flow
			    if acts.port==portid1:
				loop_before=self.match_packet(self.flow_table,switch,my_match)
				loop_after=self.match_packet(config,switch,my_match)
				if(loop_before or loop_after):
				    return 0 
	return 1








    def match_packet(self,config,switch,match1):
        print config
        packet_match_conf=[]
        for flowmod in config[switch]:
            packet_match_conf.append(flowmod.match)
        ob1=match1
        print "packet_match_conf"
        print packet_match_conf
        for ob in packet_match_conf:
            ob1.in_port=0
	    ob.in_port=0
            return1=ob.matches_with_wildcards(ob1)
	    if return1 is True:
		return True
	return False

    def if_one_switch(config):
        one_switch = len(config)
        one_touch_ok=1
        one_touch_no_ok=0
        if one_switch is one_touch_ok:
            return one_touch_ok
        else:
            return one_touch_no_ok

    def Check_loop(graph,start,end,q):
        temp_path = [start]
        q.put(temp_path)
        while q.qsize() != 0:
                tmp_path = q.get()
                last_node = tmp_path[len(tmp_path)-1]
                print tmp_path
                if last_node == end:
                        print "VALID_PATH : ",tmp_path
                for link_node in graph[last_node]:
                        if link_node not in tmp_path:
                                new_path = []
                                new_path = tmp_path + [link_node]
                                print "new path is "
                                print new_path
                                q.put(new_path)
                        if link_node in tmp_path and link_node== end:
                                print "loop to A"
                                print tmp_path
                                return 0
        return 1				


def launch():
    core.registerNew(Optimization)
