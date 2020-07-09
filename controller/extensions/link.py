LINK_ATTRIBUTES=["dpid1", "port1", "dpid2", "port2"]

class Link(object):
    def __init__(self, link):
        self.link = link
        self.weight = 0

    def __getattr__(self, key):
        if key in LINK_ATTRIBUTES:
            return self.link.__getattr__(key)
        return super(Link, self).__getattr__(key)

    def __setattr__(self, key, value):
        if key in LINK_ATTRIBUTES:
            return self.link.__setattr__(key, value)
        return super(Link, self).__setattr__(key, value)
