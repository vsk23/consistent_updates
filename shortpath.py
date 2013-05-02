from pox.core                   import core
from pox.lib.revent             import *
from pox.lib.recoco             import Timer
from configuration              import *
from pox.openflow.discovery import *
from pox.lib.addresses import IPAddr, EthAddr
import pox.lib.packet as pkt
import pox.openflow.libopenflow_01 as of
import sys
import copy
"""
ShortestPath
----------------------------------------------------------||
ShortestPath is an application that computes the shortest
path of a network topology using Djikstra's algorithm.

It requires the openfow core and openflow_discovery objects that must
be launched in the command line along with this module.
"""
class ShortestPath(EventMixin):
    #The dependencies needed to run this application
    _wantComponents = set(['openflow', 'openflow_discovery'])
    
    def __init__(self):
        super(EventMixin, self).__init__()
        if not core.listenToDependencies(self, self._wantComponents):
            self.listenTo(core)
        self.dest_ids = [5,4,3,2,1]
        self.links_down = 0
        self.CONTROLLER_PORT_ID = 65534
 
    def _handle_openflow_discovery_LinkEvent(self, event):
        # I a link is removed, we must recalculate the
        # shortest path in case it was affected.
        if event.removed:
            if self.links_down == 0:
                self.links_down = 1 
                print "new link down \n"
                configs = []
                for dest_id in self.dest_ids:
                    configs.append(self.shortest_path_dest(dest_id))

                configs[0].add_config(configs[1])
                configs[0].add_config(configs[2])
                configs[0].add_config(configs[3])
                configs[0].add_config(configs[4])
                core.consistent_update.update_config(configs[0])
        return

    # Name: get_min_entity_id
    # Description: Return the id of the entity with the smallest distance
    # Arguments:
    #   topology_ids: an array of switch_ids
    #   distances: current distances calculated for each switch_id
    # Return: integer switch id

    def get_min_entity_id(self, topology_ids, distances):
        min_id = 0;
        min_dist = 1000000000
        for sid in topology_ids:
             if distances[sid - 1] <= min_dist:
                min_dist = distances[sid - 1]
                min_id = sid
        return min_id

    # Name: shortest_path
    # Description: Calculates the shortest path from source_id switch to
    #              dest_id switch
    # Arguments:
    #   source_id: id of the sink node to calculate shortest distances from 
    #   dest_id: id of the destination node to calculate the shortest distance to 
    # Return: an array of neighbords in the optimal path
    def shortest_path(self, source_id, dest_id):
        previous = [] #neighbors in optimal path
        distances = [] # min distances of each node
        topology_ids = [] # vertices remaining in our topology

        for ent_id, entity in core.openflow_topology.topology._entities.items():
            distances.insert(ent_id, 1000000000)
            previous.insert(ent_id, -1)
            topology_ids.insert(ent_id, ent_id)

        distances[source_id - 1] = 0;
        topology = core.openflow_topology.topology 

        # while we haven't looped through the entire topology
        while len(topology_ids) != 0:
            min_entity = topology.getEntityByID(self.get_min_entity_id(topology_ids,distances))
            if (distances[min_entity.id - 1]) == 1000000000:
                break;
            topology_ids.remove(min_entity.id)
            
            if min_entity.id == dest_id:
                return previous 
            
            for port_id, port in min_entity.ports.items():
                if port_id != self.CONTROLLER_PORT_ID:
                    for neighboring_switch in port.entities:
                        alt_dist = 1 + distances[min_entity.id - 1]
                        # if the new distance is more optimal for this neighboring switch
                        if alt_dist < distances[neighboring_switch.id - 1]:
                            distances[neighboring_switch.id - 1] = alt_dist
                            previous[neighboring_switch.id - 1] = min_entity.id
        return previous
    
    # Name: shortest_path_dest
    # Description: Calculates the shortest path from all switches to
    #              dest_id switch
    # Arguments:
    #   dest_id: id of the destination node to calculate the shortest distance to 
    # Return: a configuration of flow mods to install on these switches to route
    # packets by the shortest path to dest_id

    def shortest_path_dest(self, dest_id):
        shortest_paths={}
        for eid, entity in core.openflow_topology.topology._entities.items():
            path = []
            previous = self.shortest_path(eid, dest_id)
            target = dest_id - 1 
            while not (previous[target] == -1):
                path.append(previous[target])
                target = previous[target] - 1
            path.reverse()
            path.append(dest_id);
            shortest_paths[entity.id] = path[1:len(path)];
        return self.create_config(shortest_paths, dest_id)
     
    # Name: create_config 
    # Description: Creates configuration flow mods to send via the shortest path to destination node 5
    # Arguments:
    #       shortest_paths: dict of shortest paths from each node to dest id 5
    # Return: a configuration of flow mods to install on these switches to route
    # packets by the shortest path to dest_id

    def create_config(self, shortest_paths, dest_id):
        config = Configuration();
        for switch_id, path in shortest_paths.items():
            node_id = switch_id
            for node in path:
                switch = core.openflow_topology.topology.getEntityByID(node_id)
                for port_id, port in switch.ports.items():
                    for neighboring_switch in port.entities:
                        if neighboring_switch.id == node:
                            other_ports = self.get_other_ports(switch, port_id)
                            for oport_id in other_ports:
                                dest = ""
                                if dest_id > 9:
                                    dest = "10.0.0." + str(dest_id)
                                else:
                                    dest = "10.0.0.0" + str(dest_id)
                                match = of.ofp_match(dl_type=0x800,
                                                     in_port = oport_id,
                                                     nw_dst = dest,
                                                     dl_dst = EthAddr("00:00:00:00:00:0"+ str(dest_id)))
                                flow = of.ofp_flow_mod(match = match)
                                flow.actions.append(of.ofp_action_output(port = port_id));
                                config.add_flow_mod(flow, node_id)
                node_id = node
        #A  final flow for last node
        switch = core.openflow_topology.topology.getEntityByID(dest_id)
        for port_id, port in switch.ports.items():      
            if not(port_id == self.CONTROLLER_PORT_ID):
                if len(port.entities) == 0:
                    other_ports = self.get_other_ports(switch, port_id)
                    for oport_id in other_ports:
                        match = of.ofp_match(dl_type = 0x800,
                                             in_port = oport_id,
                                             dl_dst = EthAddr("00:00:00:00:00:0"+str(dest_id)),
                                            nw_dst = "10.0.0.0"+str(dest_id)
                             )
                        flow = of.ofp_flow_mod( match = match)
                        flow.actions.append(of.ofp_action_output(port = port_id))
                        config.add_flow_mod(flow, dest_id)
        return config

    def get_other_ports(self, switch, oport_id):
        oports=[]
        for port_id, port in switch.ports.items():
            if not(port_id == oport_id) and not(port_id == self.CONTROLLER_PORT_ID):
                oports.append(port_id)
        return oports

def launch():
    if not core.hasComponent("ShortestPath"):
        core.register("ShortestPath", ShortestPath())
