from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class SwitchController:
  def __init__(self, dpid, connection, graph):
    self.dpid = dpid
    self.connection = connection
    # El SwitchController se agrega como handler de los eventos del switch
    self.connection.addListeners(self)
    self.graph = graph
    self.connected_hosts = set()
    self.weight = 0

  def _handle_PacketIn(self, event):
    """
    Esta funcion es llamada cada vez que el switch recibe un paquete
    y no encuentra en su tabla una regla para rutearlo
    """
    packet = event.parsed
    log.info("Packet arrived to switch %s from %s to %s", self.dpid, packet.src, packet.dst)
    
    # Agrego el host conectado al switch
    if (event.port not in self.graph.ports_in_switch(self.dpid)):
        self.connected_hosts.add((packet.src, event.port))

    # Solo IPv4, con IPv6 estamos teniendo lio
    if packet.type != packet.IP_TYPE:
        return

    port = None

    for connection in self.connected_hosts:
      if (packet.dst == connection[0]):
        # Si llega un paquete a un switch, y el dst es un host que yo tengo conectado
        # como es topo fat tree, se que debo mandarselo a ese host directamente
        port = connection[1]

    if port is None:
      # Si llega desde un switch o host y no tengo host conectado busco la ruta
      route = self.graph.get_route(event)
      port = self.process_nodes(route)


    # Armo el mensaje
    msg = of.ofp_flow_mod()
    msg.data = event.ofp

    msg.match.dl_dst = packet.dst
    msg.match.dl_src = packet.src
    msg.match.in_port = event.port
    msg.match.dl_type = packet.type

    msg.actions.append(of.ofp_action_output(port = port))

    self.connection.send(msg)

  def process_nodes(self, route):
    output_port = None
    route_nodes = len(route)
    for i in range(route_nodes-1):
      src_node = route[i]
      dst_node = route[i+1]
      if src_node.dpid == self.dpid:
        output_port = src_node.port
      elif dst_node.dpid == self.dpid:
        output_port = dst_node.port

    return output_port
