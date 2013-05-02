from pox.core import core
import pox.openflow.libopenflow_01 as of
import sys
from pox.lib.revent import *
from configuration import *
from pox.lib.recoco import Timer

class ShortestPathApp(EventMixin):

    def __init__(self):
        if core.hasComponent("openflow"):
            self.listenTo(core.openflow)
        else:
            self.listenTo(core)
        print "Launched Shortest Path\n"
        self.dest_ids = [5,4,3,2,1]
        Timer(20, self.shortestpath_test, recurring = False)

    def shortestpath_test(self):
        configs = [] 
        for dest_id in self.dest_ids:
            configs.append(core.ShortestPath.shortest_path_dest(dest_id))
        configs[0].add_config(configs[1])
        configs[0].add_config(configs[2])
        configs[0].add_config(configs[3])
        configs[0].add_config(configs[4])

        core.consistent_update.update_config(configs[0]);


def launch():
    core.registerNew(ShortestPathApp) 
