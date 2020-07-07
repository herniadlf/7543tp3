"""
Este archivo ejemplifica la creacion de una topologia de mininet
En este caso estamos creando una topologia muy simple con la siguiente forma

   host --- switch --- switch --- host
"""

from mininet.topo import Topo

class FatTree( Topo ):
  def __init__( self, levels = 2, **opts ):
    Topo.__init__(self, **opts)

    print('level', levels)
    # Client hosts
    cli_h1 = self.addHost('cli_h1')
    cli_h2 = self.addHost('cli_h2')
    cli_h3 = self.addHost('cli_h3')

    # Root switch
    root_sw = self.addSwitch('s1')

    # Link between switches
    previous_level_switches = [root_sw]
    if levels > 1:
      for actual_level in range(1, levels):
        print("actual level is ", actual_level)
        actual_level_switches = []
        switches_qty = 2**actual_level
        for switch_index in range(0, switches_qty):
          print("switch index is ", switch_index)
          switch = self.addSwitch('s{}{}'.format(actual_level+1, switch_index+1))
          for previous_switch in previous_level_switches:
            self.addLink(previous_switch, switch)
          actual_level_switches.append(switch)
        previous_level_switches = actual_level_switches

    # Server hosts
    index = 1
    for leaf_level_switch in previous_level_switches:
      server_host = self.addHost('srv_h{}'.format(index))
      self.addLink(leaf_level_switch, server_host)
      index = index +1

    # Link between clients and root switch
    self.addLink(root_sw, cli_h1)
    self.addLink(root_sw, cli_h2)
    self.addLink(root_sw, cli_h3)

topos = { 'fat_tree': FatTree }

