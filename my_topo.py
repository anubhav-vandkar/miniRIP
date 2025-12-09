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
            # give each side a unique interface name
            intfA = f"{a}-eth{i}"
            intfB = f"{b}-eth{i}"
            self.addLink(a, b, intfName1=intfA, intfName2=intfB)
            self.link_map[(a, b)] = intfA
            self.link_map[(b, a)] = intfB
            
def assign_ips(net, topo):
    info("*** Assigning IPs (/30 per link)\n")

    for a, b in EDGES:
        ida = NODE_IDS[a]
        idb = NODE_IDS[b]
        low, high = sorted((ida, idb))

        subnet = f"172.16.{low}{high}"
        ipa = f"{subnet}.1/30"
        ipb = f"{subnet}.2/30"

        intfA = topo.link_map[(a, b)]
        intfB = topo.link_map[(b, a)]

        net.get(a).cmd(f"ip addr add {ipa} dev {intfA}")
        net.get(a).cmd(f"ip link set {intfA} up")

        net.get(b).cmd(f"ip addr add {ipb} dev {intfB}")
        net.get(b).cmd(f"ip link set {intfB} up")

        info(f"{a}: {intfA} -> {ipa}\n")
        info(f"{b}: {intfB} -> {ipb}\n")

if __name__ == '__main__':
    setLogLevel('info')
    topo = MyTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=None)
    net.start()

    assign_ips(net, topo)

    for name in NODE_IDS:
        net.get(name).cmd("sysctl -w net.ipv4.ip_forward=1")

    print("testing the output for x")
    print(net.get('x').intfList())
    print(net.get('x').cmd('ip -br addr'))

    info("*** Testing connectivity (pingAll)\n")
    net.pingAll()

    CLI(net)
    net.stop()