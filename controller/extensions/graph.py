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
        # Primero busco si ya tengo cargado en mis rutas segun la key que tiene el paquete
        routes_from = self.routes.get(packet.src, None)
        route_to = None
        
        if routes_from is not None:
            route_to = routes_from.get(packet.dst, None)
            if route_to is not None:
                if route_to.get(packet.payload.protocol, None) is not None:
                    # Si la tengo cargada, listo!
                    return route_to.get(packet.payload.protocol)

        # si no la tengo cargada, tengo que calcular la ruta que tiene que hacer
        route = self.find_route(packet)
        if not route:
            return

        # una vez encontrada, la cargo en las rutas del grafo
        if route_to is None:
            route_to = {}

        route_to[packet.payload.protocol] = route

        if routes_from is None:
            routes_from = {}
        
        routes_from[packet.dst] = route_to

        self.routes[packet.src] = routes_from

        return route

    def find_route(self, packet):
        # Encuentro cual es el primer switch y el ultimo
        first_dpid = None
        last_dpid = None
        for switch in self.switches.values():
            hosts = [item[0] for item in switch.connected_hosts]
            if packet.src in hosts:
                first_dpid = switch.dpid
            if packet.dst in hosts:
                last_dpid = switch.dpid

        # Busco todos los caminos que llegan al ultimo switch mediante metodo recursivo
        routes = self.build_routes(first_dpid, last_dpid, [])
        if not routes:
            return

        # Consegui varias rutas, me quedo con las que efectivamente terminan en el ultimo swtich
        # a su vez, dejo calculado en una tupla el costo de cada una de estas rutas
        filtered_routes = []
        for route in map(tuple, routes):
            if route[len(route)-1][0] == last_dpid:
                cost = 0
                for switch in route:
                    dpid = switch[0]
                    cost += self.switches[dpid].weight
                route_cost_tuple = (route, cost)
                filtered_routes.append(route_cost_tuple)

        # utilizo el costo para obtener el costo minimo
        less_cost_route = self.compare_routes(filtered_routes)

        route = []
        # ya me quede con una ruta, ahora queda mapear a nodos
        # actualizo el peso que tiene cada switch de la ruta
        for each_route_node in less_cost_route:
            as_node = Node(each_route_node[0], each_route_node[1])
            route.append(as_node)
            self.update_weight(as_node)

        return route

    def compare_routes(self, routes):
        less_cost_route = routes[0]
        for route_cost in routes:
            cost = route_cost[1]
            if less_cost_route[1] > cost:
                less_cost_route = route_cost

        return less_cost_route[0]


    def build_routes(self, actual_dpid, dst_dpid, visited_dpid):
        visited_dpid.append(actual_dpid)
        # Condicion de corte: Si llegue al destino, devuelvo un array solo con el destino
        if actual_dpid == dst_dpid:
            return [[(dst_dpid, -1)]] # pongo port=-1 porque el ultimo puerto ya lo conozco

        # voy recorriendo las aristas del grafo
        routes = []
        for link in self.links:
            if link.dpid1 == actual_dpid and not link.dpid2 in visited_dpid:
                next_dpid = link.dpid2
                for route in self.build_routes(next_dpid, dst_dpid, visited_dpid[:]):
                    actual_route = [(actual_dpid, link.port1)]
                    for dpid in route:
                        actual_route.append(dpid)
                    routes.append(actual_route)
            elif link.dpid2 == actual_dpid and not link.dpid1 in visited_dpid:
                next_dpid = link.dpid1
                for route in self.build_routes(next_dpid, dst_dpid, visited_dpid[:]):
                    actual_route = [(actual_dpid, link.port2)]
                    for dpid in route:
                        actual_route.append(dpid)
                    routes.append(actual_route)

        return routes

    def update_weight(self, src_node):
        switch = self.switches.get(src_node.dpid)
        switch.weight += 1

    def remove_link(self, link_to_be_removed):
        self.links = filter(lambda link: link_to_be_removed != link, self.links)

        first_node = Node(link_to_be_removed.dpid1, link_to_be_removed.port1)
        second_node = Node(link_to_be_removed.dpid2, link_to_be_removed.port2)

        print("first node is ", str(first_node.dpid))
        print("second node is ", str(second_node.dpid))
        for route_from, routes_to in self.routes.items():
            for route_to, protocol_routes in routes_to.items():
                for protocol, route in protocol_routes.items():
                    linked_nodes = zip(route[:len(route)-1], route[1:])
                    for linked_node in linked_nodes:
                        print("linked node is ", str(linked_node[0].dpid), str(linked_node[1].dpid))
                        if linked_node[0] == first_node and linked_node[1] == second_node:
                            for node in route:
                                switch = self.switches[node.dpid]
                                switch.weight -= 1
                            protocol_routes.pop(protocol)
                            continue
                if not protocol_routes:
                    routes_to.pop(route_to)
            if not routes_to:
                self.routes.pop(route_from)


    def remove_switch(self, switch_id):
        self.links = filter(lambda link: switch_id not in [link.dpid1, link.dpid2], self.links)

        for route_from, routes_to in self.routes.items():
            for route_to, protocol_routes in routes_to.items():
                for protocol, route in protocol_routes.items():
                    dpids_in_route = [node.dpid for node in route]
                    if switch_id in dpids_in_route:
                        for dpid in dpids_in_route:
                            switch = self.switches[dpid]
                            switch.weight -= 1
                        protocol_routes.pop(protocol)
                if not protocol_routes:
                    routes_to.pop(route_to)
            if not routes_to:
                self.routes.pop(route_from)

        self.switches.pop(switch_id)


class Node:
    def __init__(self, dpid, port=None):
        self.dpid = dpid
        self.port = port

    def __str__(self):
        return str(self.dpid) + " " + str(self.port)

    def __eq__(self, other):
        return self.dpid == other.dpid

class Link(object):
    def __str__(self):
        return str(self.dpid1) + " " + str(self.port1) + " " + str(self.dpid2) + " " + str(self.port2)

    def __init__(self, link):
        self.dpid1 = link.dpid1
        self.port1 = link.port1
        self.dpid2 = link.dpid2
        self.port2 = link.port2

    def __eq__(self, other):
        return self.dpid1 == other.dpid1 and self.port1 == other.port1 \
               and self.dpid2 == other.dpid2 and self.port2 == other.port2
