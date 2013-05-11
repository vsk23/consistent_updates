""" Custom topology used in evaluating shortpath

"""
from mininet.topo import Topo

class ShortPathOne(Topo):

    def __init__(self):
        
        #Initialize topology
        Topo.__init__(self)

        #Add hosts and switches
        switch_one = self.addSwitch('s1')
        switch_two = self.addSwitch('s2')
        switch_three = self.addSwitch('s3')
        switch_four = self.addSwitch('s4')
        switch_five= self.addSwitch('s5')

        #Add hosts
        host_one = self.addHost('h1')
        host_two = self.addHost('h2')
        host_three = self.addHost('h3')
        host_four = self.addHost('h4')
        host_five = self.addHost('h5')

        #Add links
        self.addLink(switch_one, switch_two)
        self.addLink(switch_two, switch_three)
        self.addLink(switch_three, switch_five)
        self.addLink(switch_two, switch_four)
        self.addLink(switch_four, switch_five)

        self.addLink(host_one, switch_one)
        self.addLink(host_two, switch_two)
        self.addLink(host_three, switch_three)
        self.addLink(host_four, switch_four)
        self.addLink(host_five, switch_five)
  

topos = { 'shortpath_one': (lambda: ShortPathOne()) }
