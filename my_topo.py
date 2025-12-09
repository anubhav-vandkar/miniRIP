from mininet.net import Mininet
from mininet.node import OVSSwitch
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
            intfA = f"{a}-e{i}"
            intfB = f"{b}-e{i}"
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
        ipa = f"{subnet}.1/24"
        ipb = f"{subnet}.2/24"

        intfA = topo.link_map[(a, b)]
        intfB = topo.link_map[(b, a)]

        net.get(a).cmd(f"ip addr flush dev {intfA}")
        net.get(b).cmd(f"ip addr flush dev {intfB}")
        net.get(a).cmd(f"ip addr add {ipa} dev {intfA}")
        net.get(b).cmd(f"ip addr add {ipb} dev {intfB}")
        net.get(a).cmd(f"ip link set {intfA} up")
        net.get(b).cmd(f"ip link set {intfB} up")

        info(f"{a}: {intfA} -> {ipa}\n")
        info(f"{b}: {intfB} -> {ipb}\n")

def enable_forwarding(net):
    info("*** Enabling IPv4 forwarding on all hosts\n")
    for name in NODE_IDS:
        net.get(name).cmd("sysctl -w net.ipv4.ip_forward=1")

def add_neighbor_routes(net, topo):
    info("*** Adding neighbor routes (per-edge /30s)\n")

    for a, b in EDGES:
        ida = NODE_IDS[a]; idb = NODE_IDS[b]
        low, high = sorted((ida, idb))
        subnet = f"172.16.{low}{high}.0/30"
        # a sees b at .2 if a got .1; and vice versa
        ga = f"172.16.{low}{high}.2"
        gb = f"172.16.{low}{high}.1"

        intfA = topo.link_map[(a, b)]
        intfB = topo.link_map[(b, a)]

        net.get(a).cmd(f"ip route replace {subnet} dev {intfA}")
        net.get(b).cmd(f"ip route replace {subnet} dev {intfB}")

        if "default" not in net.get(a).cmd("ip route"):
            net.get(a).cmd(f"ip route add default via {ga}")
        if "default" not in net.get(b).cmd("ip route"):
            net.get(b).cmd(f"ip route add default via {gb}")

if __name__ == '__main__':
    setLogLevel('info')
    topo = MyTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=None)
    net.start()

    assign_ips(net, topo)
    enable_forwarding(net)
    add_neighbor_routes(net, topo)

    # Quick visibility
    for name in NODE_IDS:
        print(f"\n=== {name} ===")
        print(net.get(name).cmd("ip -br addr"))
        print(net.get(name).cmd("ip route"))

    info("\n*** Testing connectivity (pingAll)\n")
    net.pingAll()

    CLI(net)
    net.stop()