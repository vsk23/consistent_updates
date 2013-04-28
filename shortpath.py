from pox.core                   import core
from pox.lib.revent             import *
from pox.lib.recoco             import Timer

import pox.openflow.libopenflow_01 as of
import sys
import copy

class ShortestPath(EventMixin):

    def __init__(self):
        _core_name = "shortest_path"

        if core.hasComponent("openflow_topology"):
            self.listenTo(core.openflow_topology)
        if core.hasComponent("openflow"):
            self.listenTo(core.openflow)
        else:
            self.listenTo(core)
        #Timer to call shortes_path
        self.dest_id = 5
        Timer(20, self.shortest_path_dest, args=[self.dest_id], recurring = False)
        
    def handle_SwitchConnectionDown(self, event):
        #call shortest path again to recaculcate
        self.shotest_path(self.dest_id)

    def get_min_entity_id(self, topology_ids, distances):
        min_id = 0;
        min_dist = 1000000000
        for sid in topology_ids:
             if distances[sid - 1] <= min_dist:
                min_dist = distances[sid - 1]
                min_id = sid
        return min_id

    def shortest_path(self, source_id, dest_id):
        #given the topology, so figure out shortest path for each
        # entity in the topology to node si
        previous = []
        distances = []
        topology_ids = []
        for ent_id, entity in core.openflow_topology.topology._entities.items():
            distances.insert(ent_id, 1000000000)
            previous.insert(ent_id, -1)
            topology_ids.insert(ent_id, ent_id)

        distances[source_id-1] = 0;
       
        topology = core.openflow_topology.topology 
       # print "Topology size " + str(len(topology_ids)) + "\n"
        while len(topology_ids) != 0:
            min_entity = topology.getEntityByID(self.get_min_entity_id(topology_ids,distances))
            if (distances[min_entity.id - 1]) == 1000000000:
                break;
            print str(topology_ids)
            topology_ids.remove(min_entity.id)
        #    print "Current Min Entity: " + str(min_entity.id) + "\n"
        #    print "New Topology size: " + str(len(topology_ids)) + "\n"
            #if we are at our target destination, break
            if min_entity.id == dest_id:
         #       print "FINISHED: " + str(previous)
                return previous 
          #  print "Ports : " + str(min_entity.ports) 
            for port_id, port in min_entity.ports.items():
                if port_id != 65534:
                   # print str(port)
                    if len(port.entities) != 0:
                        for neighboring_switch in port.entities:
                    #        print str(neighboring_switch.id)
                            alt_dist = 1 + distances[min_entity.id -1]
                            if alt_dist < distances[neighboring_switch.id - 1]:
                                    distances[neighboring_switch.id - 1] = alt_dist
                                    previous[neighboring_switch.id - 1] = min_entity.id
        
           # print "finished \n"
        #print previous
        return previous
        
            
        #install mods to forward using the shortest path
        #call consistent_update to update everything appropriately
    def shortest_path_dest(self, dest_id):
        shortest_paths={}
        for eid, entity in core.openflow_topology.topology._entities.items():
            path = []
            target = dest_id
            previous = self.shortest_path(eid, target)
            while not (previous[target - 1] == -1):
               # print "TARGET : " + str(target)
                path.append(target)
                target = previous[target - 1]
            shortest_paths[entity.id] = path;
        for sid, path in shortest_paths.items():
           print " Path for " + str(sid) + ": " + str(path)
        return self.create_config(shortest_paths)
    
    def create_config(self, shortest_paths):
        Configuration config = Configuration();
        #create a flow mod with output port to switch in short paths list
        for switch_id, path in shortest_path.items():
            node_id = switch_id
            for node in path.items():
                switch = core.openflow_topology.topology.getEntityByID(node_id)
                for port_id, port in switch.ports.items():
                    for neighboring_switch in port.entities:
                        if neighboring_switch.id == node:
                            flow = of.ofp_flow_mod(dst="00:00:00:00:00:0"+str(self.dest_id))
                            flow.actions.append(of.ofp_action_output(port = pord_id));
                            config.add_flow_mod(flow, node_id)
                node_id = node
                
        return config
def launch():
    core.registerNew(ShortestPath)
