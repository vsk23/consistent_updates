import Queue
from pox.core import core
from pox.lib.revent import *
from pox.lib.recoco import *
import pox.openflow.libopenflow_01 as of

import pox.openflow.discovery
from configuration import *
from match_path import *
  # Add all links and switches


class Optimization(EventMixin):
    _core_name = "optimization"

    def __init__(self):
        if core.hasComponent("openflow"):
            self.listenTo(core.openflow)
        if core.hasComponent("openflow_discovery"):
            print("openflow_discovery")
            self.listenTo(core.openflow_discovery)
        if core.hasComponent("openflow_topology"):
            print("openflow_discovery")
            self.listenTo(core.openflow_topology)
        else:
            self.listenTo(core)
        match = of.ofp_match(in_port = 1)
        flow = of.ofp_flow_mod(match = match)
        flow.actions.append(of.ofp_action_output(port = 10))
        self.configure=Configuration()
        self.configure.add_flow_mod(flow,1)
	self.flow_table={}
	
        Timer(40, self.send_flows, recurring = False);
#        Timer(, self.check_if_one_touch(self.configure,self.flow_table), recurring = False);
        
    #def _handle_ComponentRegistered(self, event):
    #    self.addListener(GoingDownEvent, _handle_GoingDownEvent)
    #    if event.name == "openflow":
    #        self.listenTo(core.openflow)
    #    else:
    #        pass
    
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
    	pass
    def _handle_LinkEvent(self, event):
        link = event.link
        switch_one = link.dpid1
        port_one = link.port1
        switch_two = link.dpid2
        port_two = link.dpid2

        print("there was a link event between " +  str(event.link.dpid1) + "," + str(port_one) + " and " + str(event.link.dpid1) + "," + str(port_two))
   	pass


 	# Keep track of network state and send 
	# set of flow mods to 
    def check_if_one_touch(self,config1):
	if_otc=self.check_if_one_touch_flow(config1,self.flow_table)
	return if_otc

    def check_if_one_touch_flow(self,config1,flowtable):
        self.flow_table=flowtable	
	config=config1.flowmods
        #print config
	one_switch = len(config)
	if one_switch is not 1:
	    return 0
	for key,value in config.iteritems(): 
    	    switch=key
        # Create the graph based on current network topology . 
	self.graph=self.create_graph()
	#print " After "
	# 1 ---> 3 ---> 6 ---> 9 -----> 1 
	#  
        # Check for reachability back to switch where the update is done 
	#  By detecting Topological loops. 
	my_pass=self.Check_loop(self.graph,switch,switch,self.flow_table) 
	return my_pass


	# Make a graph of the physical Topo of the network
    def create_graph(self):
        self.mytopo={}
        for id,sw in core.openflow_topology.topology._entities.iteritems():
            for portid,portconn in sw.ports.iteritems():
                for neigh in portconn.entities:
                    for id1,sw1 in core.openflow_topology.topology._entities.iteritems():
                        if sw1 == neigh:
                            neigh=id1
                    if not self.mytopo.has_key(id):
                        self.mytopo[id]=[neigh]
                    else:
                        self.mytopo[id].append(neigh)
        return self.mytopo

	# Return OR of the network packet fields. 
    def match_intersect(self,mine, others):
        if mine == None:
            return others
        elif others == None:
            return mine
        elif mine == others:
            return mine
        else:
            return False

# This function constructs a new match object based on the fields of two match objects
# if either of two fields are None the non-None field is used as the field match
# If equal either of the field is returned. 
# Else False
# The resultant match is sent back. 
# If wither of the fields conflict.  
# Need to check if discard in_port 
    def construct_match(self,match1,match2):
        match = of.ofp_match()
        match.in_port=self.match_intersect(match1.in_port, match2.in_port)
        if(match.in_port==False):
            return False 
        match.dl_vlan=self.match_intersect(match1.dl_vlan, match2.dl_vlan)
        if(match.dl_vlan==False):
            return False 
        match.dl_src=self.match_intersect(match1.dl_src, match2.dl_src)
        if(match.dl_src==False):
            return False 
        match.dl_dst=self.match_intersect(match1.dl_dst, match2.dl_dst)
        if(match.dl_dst==False):
            return False 
        match.dl_type=self.match_intersect(match1.dl_type, match2.dl_type)
        if(match.dl_type==False):
            return False 
        match.nw_proto=self.match_intersect(match1.nw_proto, match2.nw_proto)
        if(match.nw_proto==False):
            return False 
        match.tp_src=self.match_intersect(match1.tp_src, match2.tp_src)
        if(match.tp_src==False):
            return False 
        match.tp_dst=self.match_intersect(match1.tp_dst, match2.tp_dst)
        if(match.tp_dst==False):
            return False 
        match.dl_vlan_pcp=self.match_intersect(match1.dl_vlan_pcp, match2.dl_vlan_pcp)
        if(match.dl_vlan_pcp==False):
            return False 
        match.nw_tos=self.match_intersect(match1.nw_tos, match2.nw_tos)
        if(match.nw_tos==False):
            return False
        match.nw_src=self.match_intersect(match1.nw_src, match2.nw_src)
        if(match.nw_src==False):
            return False 
        match.nw_dst=self.match_intersect(match1.nw_dst, match2.nw_dst)
        if(match.nw_dst==False):
            return False 
#            other_nw_dst = other.get_nw_dst()
#        if self_nw_dst[1] > other_nw_dst[1] or not IPAddr(other_nw_dst[0]).inNetwork((self_nw_dst[0], 32-self_nw_dst[1])): return False
 
        return match
        
    def Check_loop(self,graph,start,end,flow_state):
        q = Queue(0);
        temp_path = [start]
        match=of.ofp_match()
        flag=1
        current_match_path=match_path(match,temp_path)
        q.put(current_match_path)
        while q.qsize() != 0:
            tmp_path = q.get()
            lastmatch=tmp_path.lastswitchmatch
            lastpath=tmp_path.path
            last_node = lastpath[len(lastpath)-1]
            if last_node is end and flag == 1:
                flag=0
            elif last_node is end and flag != 1:
                return 1 
            for link_node in graph[last_node]:
                if link_node not in lastpath:
                    new_path = []
                    new_path = lastpath + [link_node]
		    if link_node in self.flow_table:	
                       for flow in self.flow_table[link_node]:
                    	    match=flow.match
                    	    cons_match=self.construct_match(lastmatch,match)
                    	    if(cons_match!=False):
                                new_matchpath=match_path(cons_match,new_path)
			        q.put(new_matchpath)
		else:
		     return 0
	return 1


    def send_flows(self):
	match = of.ofp_match(nw_tos=1,in_port=3)
	match2 = of.ofp_match(dl_type=0x800)
	match3 = of.ofp_match(nw_src='10.0.0.1')
	match6 = of.ofp_match(nw_src='10.0.0.1')
	match9 = of.ofp_match(nw_dst='10.0.0.3',in_port=3)
	match2 = of.ofp_match(in_port=3)
	match2 = of.ofp_match(in_port=3)
	for key,con in core.openflow._connections.iteritems():
            print key,con		
	action = of.ofp_action_output(port=2)
  	match.dl_type=0x800
	flow = of.ofp_flow_mod(match=match)
	flow.actions.append(action)
	action = of.ofp_action_output(port=2)
  	match.dl_type=0x800
	flow = of.ofp_flow_mod(match=match)
	flow.actions.append(action)
	action2 = of.ofp_action_output(port=2)
	action3 = of.ofp_action_output(port=2)
	action4 = of.ofp_action_output()
	match3 = of.ofp_match()
	match3.nw_src='10.0.0.1'
  	match3.dl_type=0x800
	match3.nw_dst='10.0.0.2'
	match3.in_port=3
	match4 = of.ofp_match()
	match4.nw_src='10.0.0.1'
	match4.nw_dst='10.0.0.2'
  	match4.dl_type=0x806
	match4.in_port=3
	match5 = of.ofp_match()
	match5.nw_src='10.0.0.2'
	match5.nw_dst='10.0.0.8'
  	match5.dl_type=0x812
	match5.in_port=3
	match6 = of.ofp_match()
	match6.nw_src='10.0.0.1'
	match6.nw_dst='10.0.0.2'
	match6.in_port=5
	match7 = of.ofp_match()
	match7.nw_src='10.0.0.1'
	match7.nw_dst='10.0.0.2'
	match8 = of.ofp_match()
	match8.nw_src='10.0.0.4'
	match8.nw_dst='10.0.0.6'
	match19 = of.ofp_match()
	match19.nw_src='10.0.0.12'
	match19.nw_dst='10.0.0.23'
	match12 = of.ofp_match()
	match12.nw_src='10.0.0.14'
	match12.nw_dst='10.0.0.25'
	match13 = of.ofp_match()
	match13.nw_src='10.0.0.16'
	match13.nw_dst='10.0.0.27'
	match14 = of.ofp_match()
	match14.nw_src='10.0.0.18'
	match14.nw_dst='10.0.0.29'
	match15 = of.ofp_match()
	match15.nw_src='10.0.0.21'
	match15.nw_dst='10.0.0.22'
	match16 = of.ofp_match()
	match16.nw_src='10.0.0.31'
	match16.nw_dst='10.0.0.32'
	match18 = of.ofp_match()
	match18.nw_src='10.0.0.41'
	match18.nw_dst='10.0.0.42'
	match9 = of.ofp_match()
	match9.nw_src='10.0.0.1'
	match9.nw_dst='10.0.0.2'
	action2 = of.ofp_action_output(port=2)
	
	flow2 = of.ofp_flow_mod(match=match2)
	flow2.actions.append(action4)
	flow3 = of.ofp_flow_mod(match=match3)
	flow4 = of.ofp_flow_mod(match=match4)
	flow5 = of.ofp_flow_mod(match=match5)
	flow7 = of.ofp_flow_mod(match=match7)
	flow6 = of.ofp_flow_mod(match=match6)
	flow8 = of.ofp_flow_mod(match=match8)
	flow16 = of.ofp_flow_mod(match=match16)
	flow18 = of.ofp_flow_mod(match=match18)
	flow13 = of.ofp_flow_mod(match=match13)
	flow15 = of.ofp_flow_mod(match=match15)
	flow14 = of.ofp_flow_mod(match=match14)
	#flow9 = of.ofp_flow_mod(match=match9)
	flow3.actions.append(action3)
	flow4.actions.append(action4)
        self.flow_table[1]=[]
        self.flow_table[2]=[]
        self.flow_table[3]=[]
        self.flow_table[4]=[]
        self.flow_table[5]=[]
        self.flow_table[6]=[]
        self.flow_table[7]=[]
        self.flow_table[8]=[]
        self.flow_table[9]=[]
        self.flow_table[2].append(flow2)
        self.flow_table[4].append(flow2)
        self.flow_table[3].append(flow3)
        self.flow_table[6].append(flow6)
        self.flow_table[6].append(flow7)
        self.flow_table[3].append(flow5)
        self.flow_table[4].append(flow4)
        self.flow_table[5].append(flow5)
        self.flow_table[9].append(flow8)
        self.flow_table[9].append(flow18)
        self.flow_table[9].append(flow13)
        self.flow_table[9].append(flow16)
        self.flow_table[9].append(flow14)
        self.flow_table[9].append(flow15)
        #self.flow_table[9].append(flow9)
	#chk=self.check_if_one_touch(self.configure,self.flow_table) 
	#if chk == 1:
	#    print " reaches back"
	#else:
	#    print " No loop" 
def launch():
    core.registerNew(Optimization)
