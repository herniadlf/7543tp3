LINK_ATTRIBUTES=["dpid1", "port1", "dpid2", "port2"]

class Link(object):
    def __init__(self, link):
        self.link = link
        self.weight = 0

    def __getattribute__(self, key):
        if key in LINK_ATTRIBUTES:
            return self.link.__getattribute__(key)
        return super(Link, self).__getattribute__(key)
