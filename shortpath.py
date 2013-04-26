from pox.core import core
import pox.openflow.libopenflow_01 as of
import sys


class ShotestPath(EventMixin):

    def __init___(self):
        if core.hasComponent("openflow_topology"):
            self.listenTo(core.openflow_topology);
        if core.hasComponent("openflow"):
            self.listenTo(core.openflow)
        else:
            self.listenTo(core)
        #Timer to call shortes_path
        Timer(self.shortest_path, args=[1, 5], recurring = False)
        
    def handle_SwitchConnectionDown(self, event):
        #call shortest path again to recaculcate
        shotest_path()

    def shortest_path(selfi, source_id, dest_id):
        #given the topology, so figure out shortest path for each
        # entity in the topology to node si
        previous = []
        distances = []
        for entity in core.openflow_topology.topology:
            distances[entity.id] = 1000000000

        distances[source_id] = 0;
       
        topology = core.openflow_topology.topology 
        while topology.size != 0:
            min_entity = topology.getEntityByID(distances.index(min(distances)))
            if (distances.index(min(distances))) == 1000000000:
                break;
            topology.removeEntity(min_entity)
            #if we are at our target destination, break
            if min_entity.id = dest_id:
                return previous 
               
            for port in entity.ports:
                if port.entities != 0:
                    neighbor_id = port.entities[id].id
                    alt_dist = 1 + distances[min_entity]
                    if alt_dist < distances[neighbord_id]:
                        distances[neighbor_id] = alt_dist
                        previous[neighbor_id] = min_entity                       
        
            
        #install mods to forward using the shortest path
        #call consistent_update to update everything appropriately
    def shortest_path_dest(self, dest_id):
        shortest_paths={}
        for entity in core.openflow_topology.topology:
            path = []
            target = dest_id
            previous = shortest_path(entity.id, target)
            while not (previous[target] is None):
                path.append(target)
                target = previous[target]
            shortest_path[entity.id] = path;
        return shortest_paths;

def launch():
    component = ShortestPath()
    core.registerNew(ShortestPath)
