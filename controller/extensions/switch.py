from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class SwitchController:
  def __init__(self, dpid, connection, controller):
    self.dpid = dpid
    self.connection = connection
    # El SwitchController se agrega como handler de los eventos del switch
    self.connection.addListeners(self)
    self.controller = controller

  def _handle_PacketIn(self, event):
    """
    Esta funcion es llamada cada vez que el switch recibe un paquete
    y no encuentra en su tabla una regla para rutearlo
    """
    packet = event.parsed
    log.info("Packet arrived to switch %s from %s to %s", self.dpid, packet.src, packet.dst)

    if packet.type != packet.IP_TYPE:  # Solo IPv4
        return

    if event.port == 1:
      port = 2
    else:
      port = 1

    print('Puerto de entrada ' + str(event.port))
    print('Puerto de salida ' + str(port))

    msg = of.ofp_flow_mod()
    msg.data = event.ofp

    msg.match.dl_dst = packet.dst
    msg.match.dl_src = packet.src
    msg.match.in_port = event.port
    msg.match.dl_type = packet.type

    msg.actions.append(of.ofp_action_output(port = port))

    self.connection.send(msg)
