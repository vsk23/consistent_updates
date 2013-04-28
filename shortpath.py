from pox.core                   import core
from pox.lib.revent             import *
from pox.lib.recoco             import Timer
from configuration              import *
from pox.openflow.discovery import *

import pox.openflow.libopenflow_01 as of
import sys
import copy

class ShortestPath(EventMixin):
    _wantComponents = set(['openflow', 'openflow_topology', 'openflow_discovery'])
    def __init__(self):
        super(EventMixin, self).__init__()
        if not core.listenToDependencies(self, self._wantComponents):
            self.listenTo(core)
        self.dest_id = 5
        
    def _handle_openflow_discovery_LinkEvent(self, event):
        if event.removed:
            config = self.shortest_path_dest(self.dest_id)
            core.consistent_update.update_config(config)
        return

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
        while len(topology_ids) != 0:
            min_entity = topology.getEntityByID(self.get_min_entity_id(topology_ids,distances))
            if (distances[min_entity.id - 1]) == 1000000000:
                break;
            topology_ids.remove(min_entity.id)
            #if we are at our target destination, break
            if min_entity.id == dest_id:
                return previous 
            for port_id, port in min_entity.ports.items():
                if port_id != 65534:
                    if len(port.entities) != 0:
                        for neighboring_switch in port.entities:
                            alt_dist = 1 + distances[min_entity.id -1]
                            if alt_dist < distances[neighboring_switch.id - 1]:
                                    distances[neighboring_switch.id - 1] = alt_dist
                                    previous[neighboring_switch.id - 1] = min_entity.id
        
        return previous
        
            
    def shortest_path_dest(self, dest_id):
        shortest_paths={}
        for eid, entity in core.openflow_topology.topology._entities.items():
            path = []
            target = dest_id
            previous = self.shortest_path(eid, target)
            while not (previous[target - 1] == -1):
                path.append(target)
                target = previous[target - 1]
            shortest_paths[entity.id] = path;
        return self.create_config(shortest_paths)
    
    def create_config(self, shortest_paths):
        config = Configuration();
        #create a flow mod with output port to switch in short paths list
        for switch_id, path in shortest_paths.items():
            node_id = switch_id
            for node in path:
                switch = core.openflow_topology.topology.getEntityByID(node_id)
                for port_id, port in switch.ports.items():
                    for neighboring_switch in port.entities:
                        if neighboring_switch.id == node:
                            match = of.ofp_match(dl_type=0X800,
                                                 nw_dst="10.0.0.05")
                            flow = of.ofp_flow_mod( match = match)
                            flow.actions.append(of.ofp_action_output(port = port_id));
                            config.add_flow_mod(flow, node_id)
                node_id = node
        return config

def launch():
    if not core.hasComponent("ShortestPath"):
        core.register("ShortestPath", ShortestPath())
