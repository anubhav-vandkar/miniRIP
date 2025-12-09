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

        for router in NODE_IDS:
            self.addHost(router)

        self.ifidx = { h: 0 for h in NODE_IDS }

        self.link_map = {}

        for a, b in EDGES:
            a_eth = f"{a}-eth{self.ifidx[a]}"
            b_eth = f"{b}-eth{self.ifidx[b]}"

            self.addLink(a, b, intfName1=a_eth, intfName2=b_eth)

            self.link_map[(a, b)] = (a_eth, b_eth)

            self.ifidx[a] += 1
            self.ifidx[b] += 1

def assign_ips(net, topo):
    info("*** Assigning IPs (/30 per link)\n")

    for a, b in EDGES:
        ida = NODE_IDS[a]
        idb = NODE_IDS[b]
        low, high = sorted((ida, idb))
        subnet = f"172.16.{low}{high}"

        ipA = f"{subnet}.1/30"
        ipB = f"{subnet}.2/30"

        intfA, intfB = topo.link_map[(a, b)]

        info(f"{a}: {intfA} <- {ipA}\n")
        net.get(a).cmd(f"ip addr add {ipA} dev {intfA}")
        net.get(a).cmd(f"ip link set {intfA} up")

        info(f"{b}: {intfB} <- {ipB}\n")
        net.get(b).cmd(f"ip addr add {ipB} dev {intfB}")
        net.get(b).cmd(f"ip link set {intfB} up")


if __name__ == '__main__':
    setLogLevel('info')
    topo = MyTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=None)
    net.start()
    assign_ips(net, topo)

    info("\n*** Connectivity Test\n")
    net.pingAll()

    CLI(net)
    net.stop()