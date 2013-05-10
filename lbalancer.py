from random import choice
from configuration import *
from pox.core import core
from pox.lib.revent import *
from pox.lib.recoco import *
import pox.openflow.libopenflow_01 as of

class Basic(EventMixin):
    def __init__(self):
        if core.hasComponent("openflow"):
            self.listenTo(core.openflow)
        else:
            self.listenTo(core)
        self.listN = [2,3,4]
        self.N=5	
	self.backend_servers_mac=[]
	self.backend_servers=[]
        self.connect=[]
        self.number_of_connections=1
	for x in range(2, self.N):
    	    stringx = str(x)
	    my_ip = "10.0.0."
	    my_mac ="00:00:00:00:00:0"+stringx
	    my_server = my_ip + stringx 
	    self.backend_servers_mac.append(my_mac)
	    self.backend_servers.append(my_server)
	print("The List of Backend Servers are :\n")
        for x in range(2, self.N):
	    print (self.backend_servers[x-2])
        Timer(150, self.update_server_address, recurring = False);
	

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

    def _handle_FlowStatsReceived(self,event):
        pass

    def _handle_PacketIn(self, event):
        switch = event.dpid
        packet = event.parsed
        print("PacketIn: " + str(packet))
	src=packet.src
	dst=packet.dst
	ip = packet.find('ipv4')	
        print "My source is  " + str(ip.srcip)
        print "My destination is " + str(ip.dstip)
    	if ip.srcip in self.backend_servers:
	    action4=of.ofp_action_dl_addr.set_src('00:00:00:00:00:05')
	    action2=of.ofp_action_nw_addr.set_src('10.0.0.5')
	    action3 = of.ofp_action_output(port=1)
            # Flood the packet by installing a rule using a FlowMod message
            self.match1 = of.ofp_match.from_packet(packet)
            self.match1.in_port = event.port
	    self.match1.dl_type=0x800
            flow = of.ofp_flow_mod(match=self.match1)
            #flow.idle_timeout = of.OFP_FLOW_PERMANENT
            #flow.hard_timeout = of.OFP_FLOW_PERMANENT
            flow.priority = 65534
            flow.actions.append(action4)
            flow.actions.append(action2)
            flow.actions.append(action3)
            if event.ofp.buffer_id != -1: 
                flow.buffer_id = event.ofp.buffer_id            
	    event.connection.send(flow)
	    
	if (ip.dstip == '10.0.0.5'):
	    numN=choice(self.listN)
	    print "numN" + str(numN)
	    strN=str(numN)
	    ip_addr='10.0.0.'+strN
	    mac_addr='00:00:00:00:00:0'+strN
	    action4=of.ofp_action_dl_addr.set_dst(mac_addr)
	    action2=of.ofp_action_nw_addr.set_dst(ip_addr)
	    action3 = of.ofp_action_output(port=numN)
	
        # Flood the packet by installing a rule using a FlowMod message
            self.match2 = of.ofp_match.from_packet(packet)
 	    self.match2.in_port = event.port
 	    self.match2.dl_type=0x800
            flow = of.ofp_flow_mod(match=self.match2)
        	 #flow.idle_timeout = of.OFP_FLOW_PERMANENT
        #flow.hard_timeout = of.OFP_FLOW_PERMANENT
            flow.priority = 65534
            flow.actions.append(action4)
            flow.actions.append(action2)
       	    flow.actions.append(action3)
            if event.ofp.buffer_id != -1: 
                flow.buffer_id = event.ofp.buffer_id            
	    event.connection.send(flow)
	    
        return
      
    def update_server_address(self):
        match32 = of.ofp_match()
        #flow1 = of.ofp_flow_mod(match=match32)
        #flow1.priority = 65535
	match32.nw_src='10.0.0.1'
	match32.nw_dst='10.0.0.5'
	match32.dl_type=0x800
	match32.dl_type
	mac_addr2='00:00:00:00:00:04'
	ip_addr2='10.0.0.4'
	#mac_addr='00:00:00:00:00:06'
	#ip_addr='10.0.0.6'
	action11=of.ofp_action_dl_addr.set_dst(mac_addr2)
	action12=of.ofp_action_nw_addr.set_dst(ip_addr2)
	action13 = of.ofp_action_output(port=4)
        flow2 = of.ofp_flow_mod(match=match32)
        flow2.actions.append(action11)
        flow2.actions.append(action12)
        flow2.actions.append(action13)
	#action21=of.ofp_action_dl_addr.set_dst(mac_addr2)
	#action22=of.ofp_action_nw_addr.set_dst(ip_addr2)
	#action23 = of.ofp_action_output(port=4)
        #flow1.actions.append(action21)
        #flow1.actions.append(action22)
        #flow1.actions.append(action23)
        #flow1.actions.append(action4)
        #flow1.actions.append(action2)
        #flow1.actions.append(action3)
	self.my_config=Configuration()
        match = of.ofp_match()
	print "match.in_port" + str(match.in_port)
	print("*******************************************************I come here ***************************************************************************************")
        flow2.priority = 65535
        self.my_config.add_flow_mod(flow2,1)
	core.consistent_update.update_config(self.my_config)
	

        # Flood the packet directly by sending a PacketOut message
        # msg = of.ofp_packet_out(action=action)
        # if event.ofp.buffer_id == -1: 
        #     msg.data = packet.pack()
        # else:
        #     msg.buffer_id = event.ofp.buffer_id
        # msg.in_port = event.port
        # event.connection.send(msg)

def launch():
    core.registerNew(Basic)
