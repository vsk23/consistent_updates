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
        print str(core.components)
        self.dest_id = 5
        Timer(20, self.shortestpath_test, recurring = False)

    def shortestpath_test(self):
        print "calling shortestpath"
        config = core.ShortestPath.shortest_path_dest(self.dest_id);
        print str(config.flowmods)
        core.consistent_update(config);


def launch():
    core.registerNew(ShortestPathApp) 
