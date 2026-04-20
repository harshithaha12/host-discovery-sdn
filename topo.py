from mininet.topo import Topo

class SimpleTopo(Topo):

    def build(self):

        # Force OpenFlow13 switch
        s1 = self.addSwitch(
            's1',
            protocols='OpenFlow13'
        )

        # Hosts
        h1 = self.addHost(
            'h1',
            ip='10.0.0.1/24',
            mac='00:00:00:00:00:01'
        )

        h2 = self.addHost(
            'h2',
            ip='10.0.0.2/24',
            mac='00:00:00:00:00:02'
        )

        h3 = self.addHost(
            'h3',
            ip='10.0.0.3/24',
            mac='00:00:00:00:00:03'
        )

        # Links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)


topos = {
    'simpletopo': lambda: SimpleTopo()
}