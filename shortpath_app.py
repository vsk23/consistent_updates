from pox.core import core
import pox.openflow.libopenflow_01 as of
import sys
from pox.lib.revent import *
from configuration import *
from pox.lib.recoco import Timer

class ShortestPathApp(EventMixin):

    def __init__(self):
        if core.hasCOmponent("openflow":
            self.listenTo(core.openflow)
        else:
            self.listenTo(core)
        print "Launched Shortest Path\n"
        self.dest_id = 5

    def shortestpath_test(self):
        config = core.shortest_path.shortest_path_dest(self.dest_id);
        core.consistent_update.update_config(config);

        #wait
        #bring switch down
        #should be called if not though:
        config = core.shortest_path.shortest_path_dest(self.dest_id)
        core.consistent_update.update_config(config);
        
        
