class Graph:
    def __init__(self):
        self.links = []
        self.routes = {}
        self.switches = {}
    
    def add_switch(self, switch):
        self.switches[switch.dpid] = switch
    
    def add_link(self, link):
        self.links.append(link)

    def ports_in_switch(self, dpid):
        ports = []

        for link in self.links:
            if link.dpid1 == dpid:
                ports.append(link.port1)
            
            if link.dpid2 == dpid:
                ports.append(link.port2)

        return ports

    def get_route(self, event):
        """
        Que define la ruta?

        Esta definida por:
            - Mac de origen
            - Mac de destino
            - TCP/UDP
        
        Esto define la secuencia de switches
        """
        packet = event.parsed


        """
        {
            '1': { // FROM
                '2': { // TO
                    'tcp': ruta // PROTOCOL
                }
            }
        }
        """
        routes_from = self.routes.get(packet.src, None)
        route_to = None
        
        if routes_from is not None:
            route_to = routes_from.get(packet.dst, None)
            if route_to is not None:
                if route_to.get(packet.payload.protocol, None) is not None:
                    return route_to.get(packet.payload.protocol)

        route = self.find_route(packet)

        if route_to is None:
            route_to = {}

        route_to[packet.payload.protocol] = route

        if routes_from is None:
            routes_from = {}
        
        routes_from[packet.dst] = route_to

        self.routes[packet.src] = routes_from

        return route

    def find_route(self, packet, visited = []):
        """
        HOST1 ----LINK1---- (dpid1, port1) SWITCH1
        
        SWITCH1 (dpid1, port2) ----LINK2---- (dpid2, port1) SWITCH2

        SWITCH2 (dpid2, port2) ----LINK3---- HOST2


        ----------------------
        SWTICH (dpid1, port1) ----LINK---- (dpid2, port2) HOST
        
        SWTICH (dpid2, port2) ----LINK---- (dpid1, port1) HOST
        """

        # Encuentro cual es el primer switch y el último
        for switch in self.switches.values():
            if switch.host == packet.src:
                first_dpid = switch.dpid
            if switch.host == packet.dst:
                last_dpid = switch.dpid


        """
                        s1 (first_dpid)
                s2                         s3
            s4      s5      s6(last_dpid)       s7
        """

        """
        1 paso: Empezamos desde s6 y encontramos a s2 y s3
        2 paso: Empezamos con s2: s1, s4, s5, s7

        Caminos posibles:
            s6 s2 s4 s3 s1
            s6 s2 s5 s3 s1
            s6 s2 s7 s3 s1
            s6 s2 s1

            s6 s3 s4 s2 s1
            s6 s3 s5 s2 s1
            s6 s3 s7 s2 s1
            s6 s3 s1
        """

        # Necesito encontrar todos los switches que llegan al last_dpid
        visited = []
        previous = []
        for link in self.links:
            if link.dpid1 == last_dpid:
                previous.append(Node(link.dpid2, link.port2))
            elif link.dpid2 == last_dpid:
                previous.append(Node(link.dpid1, link.port1))
        

        
        return [
        ]



class Node:
    def __init__(self, dpid, port):
        self.dpid = dpid
        self.port = port

class Link(object):
    def __init__(self, link):
        self.dpid1 = link.dpid1
        self.port1 = link.port1
        self.dpid2 = link.dpid2
        self.port2 = link.port2
        self.weight = 1
