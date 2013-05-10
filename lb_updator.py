from pox.core import core
import pox.openflow.libopenflow_01 as of
import sys
from pox.lib.revent import *
from configuration import *
from pox.lib.recoco import Timer

class Updator(EventMixin):
    _core_name = "updator"
    
    def __init__(self):
        print("LAUNCHING UPDATE _______")
        if core.hasComponent("openflow"):
            self.listenTo(core.openflow)
        else:
            self.listenTo(core)
        print(str(core.components)) 
        match = of.ofp_match(in_port = 1)
        flow = of.ofp_flow_mod(match = match)
        flow.actions.append(of.ofp_action_output(port = 10))
        self.configure=Configuration()
        self.configure.add_flow_mod(flow,1)
        self.flow_table={}
        #Timer(60, self.one_touch_test, recurring = False);
  	 
    def one_touch_test(self):
        print("in update")
        
        match = of.ofp_match(in_port = 1)
        flow = of.ofp_flow_mod(match = match)
        flow.actions.append(of.ofp_action_output(port = 10))
        self.config = Configuration()
        self.config.add_flow_mod(flow,1)
        #self.config.add_flow_mod(flow,2)
        core.consistent_update.update_config(self.config)

    def call_updator(self):
	print "Cant enter" 
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
        # 3, 6,7, 5, 8, 18	
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
	# 3,6,7,5,8,18
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
        self.flow_table[5].append(flow5)
        self.flow_table[9].append(flow8)
        self.flow_table[9].append(flow18)
        return self.flow_table
	#    print " No loop" 
	 
def launch():
    core.registerNew(Updator)
