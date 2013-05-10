import Queue
from pox.core import core
from pox.lib.revent import *
from pox.lib.recoco import *
import pox.openflow.libopenflow_01 as of
import updator as up
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
        Timer(140, self.send_flows, recurring = False);
        #Timer(30, self.check_if_one_touch(), recurring = False);
        
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
	config=config1.flowmods
        #print config
	one_switch = len(config)
	if one_switch is not 1:
	    return 0
	for key,value in config.iteritems(): 
    	    switch=key
        # Create the graph based on current network topology . 
	self.graph=self.create_graph()
        if len(self.graph) ==0:
	    return 1
	print ("self.graph" + str(self.graph ))
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
       	self.flow_table=core.updator.call_updator()
        print self.flow_table
	
def launch():
    core.registerNew(Optimization)
