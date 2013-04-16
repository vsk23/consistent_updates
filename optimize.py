#################################################################################################################################################################
##################################################################OPTIMIZE ONE TOUCH#############################################################################
#################################################################################################################################################################

# This library is used by the consistent updates component to check if for the current network state and the updates provided by the user is it possible to update
# the configuration with maintaining per packet consistent update in a one touch update rather than two phase update. 

# The consistent updates component calls the check_one_touch() function which takes as input.
# topo : Topology - how the switches are connected.
# config : This update configuration - This is a map from switch to list of updates pertaing to the switch.
# flowstate : state of flows for the switches in the network. 

def check_one_touch(topo,config,flowstate):
	one_switch=if_one_switch(config)
	if one_switch==0:
 	    return 0
	for key in config:
            update_switch=key
	#Reduce the topology to switch <=> switch connection
	physical_topo=reduce_to_topo(topo)
        # Find the immediate neighboring switches to check if any rules exist which forward packets bi-directionally
	neigh=find_neigh(topo,update_switch)	
	#TODOGet the packets that match the flowmods at this switch
	# If any of the rules in the connected switches forward packets to the connected switch through the same port 
	for connected_switch in neigh:
	    print connected_switch
	    if connected_switch in flowstate:
            	my_flows=flowstate[connected_switch]
	    	for flow in my_flows:
		   for key,value in topo[update_switch].iteritems():
		       if int(value.split('_')[0])==connected_switch:
		           my_action=flow.actions
		            #If any of the actions are to forward the packet to update_switch no one touch  
			    for acts in my_action:
		                if my_action[acts].port==int(value.split('_')[1]):
			            return 0 
				
	    q = Queue.Queue(0)
	    check_if_loop=Check_loop(physical_topo,update_switch,update_switch,q)
	    if check_if_loop==0:
                return 0
	    else:
                return 1


def find_neigh(topo,switch):
    neighbor=[]
    for key,value in topo[switch].iteritems():
        neighbor.append(int(value.split('_')[0]))
    return neighbor


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
		for link_node in graph[last_node]:
			if link_node not in tmp_path:
				new_path = []
				new_path = tmp_path + [link_node]
				q.put(new_path)
			if link_node in tmp_path and link_node== end:
				return 0
	return 1

def reduce_to_topo(my_hash):
    mytopo={}
    for key, value in my_hash.iteritems() :
        for key1,value1 in value.iteritems():
            value1.split('_')
            conn=int(value1[0])
            if not mytopo.has_key(key):
                mytopo[key]=[]
            if mytopo.has_key(conn):
                if mytopo[conn] == key and int(my_hash[conn][int(value1[2])].split('_'))!=key1:
                    mytopo[key].append(conn)
            else:
                mytopo[key].append(conn)
    return mytopo

def match_packet(config,switch,flowstate,neigh):
    packet_match_conf=[]
    packet_match_nwstate=[]
    for flowmod in config[switch]:
        packet_match_conf.append(flowmod.match)
    for next_sw in neigh:
        if next_sw not in packet_match_nwstate:
            packet_match_nwstate[next_sw]=[]
        for flowmod in flowstate[next_sw]: 
            packet_match_nwstate[next_sw].append(flowmod.match)
    
    c3 = [filter(lambda x: x in packet_match_conf, sublist) for sublist in packet_match_nwstate]	
    print c3


