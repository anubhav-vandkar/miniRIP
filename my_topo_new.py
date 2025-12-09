from mininet.net import Mininet
from mininet.node import Host, OVSSwitch
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel, info


NODE_IDS = {'u':1,'v':2,'ex':4,'w':3,'y':5,'z':6}

EDGES = [
    ('u','ex'),
    ('u','v'),
    ('u','w'),
    ('v','w'),
    ('v','ex'),
    ('ex','y'),
    ('ex','w'),
    ('w','y'),
    ('w','z'),
    ('y','z')
]

class MyTopo(Topo):
    def build(self):
        # Add router-nodes as hosts
        for name in NODE_IDS:
            self.addHost(name)

        # We will SHORT-CIRCUIT interface naming — the simplest safe method:
        # Every time we add a link, we assign the lowest free ethN on each host.
        self.ifaces = { n:0 for n in NODE_IDS }

        # Store mapping: (a,b) → (a-iface, b-iface)
        self.link_map = {}

        for a, b in EDGES:
            a_idx = self.ifaces[a]
            b_idx = self.ifaces[b]

            intfA = f"{a}-eth{a_idx}"
            intfB = f"{b}-eth{b_idx}"

            self.addLink(a, b, intfName1=intfA, intfName2=intfB)

            # Store mapping for later IP assignment
            self.link_map[(a, b)] = (intfA, intfB)
            self.link_map[(b, a)] = (intfB, intfA)

            # Increment interface counters
            self.ifaces[a] += 1
            self.ifaces[b] += 1


def assign_ips(net, topo):
    info("*** Assigning IPs to interfaces\n")

    for a, b in EDGES:
        ida = NODE_IDS[a]
        idb = NODE_IDS[b]
        low, high = sorted((ida, idb))
        subnet = f"172.16.{low}{high}"

        # IP of each router on that link
        ipa = f"{subnet}.{ida}/24"
        ipb = f"{subnet}.{idb}/24"

        intfA, intfB = topo.link_map[(a, b)]

        info(f"{a}: {intfA} -> {ipa}\n")
        net.get(a).cmd(f"ip addr add {ipa} dev {intfA}")
        net.get(a).cmd(f"ip link set {intfA} up")
        net.get(a).cmd(f"ip link set {intfA} mtu 1500")

        info(f"{b}: {intfB} -> {ipb}\n")
        net.get(b).cmd(f"ip addr add {ipb} dev {intfB}")
        net.get(b).cmd(f"ip link set {intfB} up")
        net.get(b).cmd(f"ip link set {intfB} mtu 1500")


if __name__ == '__main__':
    setLogLevel('info')
    topo = MyTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=None)
    net.start()

    assign_ips(net, topo)

    info("*** Testing connectivity (pingAll)\n")
    net.pingAll()

    CLI(net)
    net.stop()