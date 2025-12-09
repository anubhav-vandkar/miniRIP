from mininet.net import Mininet
from mininet.node import Host, OVSSwitch
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel, info

NODE_IDS = {
    'u': 1,
    'v': 2,
    'w': 3,
    'x': 4,
    'y': 5,
    'z': 6
}

EDGES = [
    ('u', 'v'),
    ('u', 'x'),
    ('v', 'w'),
    ('v', 'x'),
    ('x', 'y'),
    ('x', 'w'),
    ('w', 'y'),
    ('w', 'z'),
    ('y', 'z'),
]

class MyTopo(Topo):
    def build(self):
        for name in NODE_IDS:
            self.addHost(name)

        self.link_map = {}

        for i, (a, b) in enumerate(EDGES):
            sw = self.addSwitch(f"s{i}")   # unique switch per edge
            self.addLink(a, sw)
            self.addLink(b, sw)

            self.link_map[(a, b)] = sw
            self.link_map[(b, a)] = sw
            
def assign_ips(net, topo):
    info("*** Assigning IPs (/30 per link)\n")

    for a, b in EDGES:
        ida = NODE_IDS[a]
        idb = NODE_IDS[b]
        low, high = sorted((ida, idb))

        # Each link gets a /30
        subnet = f"172.16.{low}{high}"
        ipa = f"{subnet}.1/30"
        ipb = f"{subnet}.2/30"

        intfA, intfB = topo.link_map[(a, b)]

        net.get(a).cmd("ip link set lo up")
        net.get(b).cmd("ip link set lo up")

        info(f"{a}: {intfA} -> {ipa}\n")
        net.get(a).cmd(f"ip addr add {ipa} dev {intfA}")
        net.get(a).cmd(f"ip link set {intfA} up")

        info(f"{b}: {intfB} -> {ipb}\n")
        net.get(b).cmd(f"ip addr add {ipb} dev {intfB}")
        net.get(b).cmd(f"ip link set {intfB} up")

if __name__ == '__main__':
    setLogLevel('info')
    topo = MyTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=None)
    net.start()

    assign_ips(net, topo)

    print("testing the output for x")
    print(net.get('x').intfList())
    print(net.get('x').cmd('ip -br addr'))

    info("*** Testing connectivity (pingAll)\n")
    net.pingAll()

    CLI(net)
    net.stop()
