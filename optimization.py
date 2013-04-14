import Queue
from pox.core import core
from pox.lib.revent import *
import pox.openflow.libopenflow_01 as of
from pox.lib.recoco import Timer



config = { "1":["flow1","flow3","flow2","flow5"],
                "2":["FLOWE"]}


class Learning_switch(EventMixin):

    def __init__(self):
        if core.hasComponent("openflow"):
            print("has openflow component")
            self.listenTo(core.openflow)
        if core.hasComponent("openflow_discovery"):
            print("has openflow_discovery component")
            self.listenTo(core.openflow_discovery)
        if core.hasComponent("openflow_topology"):
            print("has openflow_topology component")
            self.listenTo(core.openflow_topology)
        else:
            self.listenTo(core)
        #store|| Key = ether.switch Value = output port
        self.host_port_map={}
        self.physical_topo={}
        self.switches=[]
    def _handle_ComponentRegistered(self, event):
        self.addListener(GoingDownEvent, _handle_GoingDownEvent)
        if event.name == "openflow":
            self.listenTo(core.openflow)
        else:
            pass

    # You should modify the handlers below.
    def _handle_ConnectionUp(self, event):
        print("has _handle_ConnectionUp")
        switch=event.connection.dpid
        self.switches.append(switch)
        print self.switches
         self.switches.append(switch)
        print self.switches
        pass

    def _handle_ConnectionDown(self, event):
        pass

    def _handle_FlowRemoved(self, event):
        pass

    def _handle_PortStatus(self,event):
        pass

    def _handle_StatsReply(self,event):
        pass

    def _handle_LinkEvent(self, event):
        link = event.link
        switch_one = link.dpid1
        port_one = link.port1
        switch_two = link.dpid2
        port_two = link.dpid2
        self.physical_topo[link.dpid1]=[]
        self.physical_topo[link.dpid1].append(link.dpid2)
        for key, value in self.physical_topo.iteritems() :
                print key, value
        self.hash_list=list(self.physical_topo)
        return

    def _handle_PacketIn(self, event):
        print("In PacketIn")
        self.one_switch=if_one_switch(config)
        if self.one_switch == 1:
            self.q = Queue.Queue(0)
            self.check_if_loop=Check_loop(self.physical_topo,1,1,self.q)
            if self.check_if_loop==0:
                print "Can't be one touch"
            else:
                print "Can be one touch"
        else:
            print "Can't be one touch"
        return
    def _handle_SwitchJoin(self,event):
         return

def launch():
    core.registerNew(Learning_switch)

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
                print tmp_path
                if last_node == end:
                        print "VALID_PATH : ",tmp_path
                for link_node in graph[last_node]:
                        if link_node not in tmp_path:
                                new_path = []
                                new_path = tmp_path + [link_node]
                                print "new path is "
                                print new_path
                                q.put(new_path)
                        if link_node in tmp_path and link_node== end:
                                print "loop to A"
                                print tmp_path
                                return 0
        return 1
