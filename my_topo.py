from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel, info

NODE_IDS = {'u':1,'v':2,'w':3,'x':4,'y':5,'z':6}
EDGES = [
    ('u','v'),
    ('u','x'),
    ('v','w'),
    ('v','x'),
    ('x','y'),
    ('x','w'),
    ('w','y'),
    ('w','z'),
    ('y','z'),
]

class MyTopo(Topo):
    def build(self):
        # Add hosts
        for name in NODE_IDS:
            self.addHost(name)
        # Direct host-host links with explicit, unique names
        self.link_map = {}  # (a,b) -> iface on 'a' connected to 'b'
        for i, (a, b) in enumerate(EDGES):
            ia = f"{a}-e{i}"
            ib = f"{b}-e{i}"
            self.addLink(a, b, intfName1=ia, intfName2=ib)
            self.link_map[(a, b)] = ia
            self.link_map[(b, a)] = ib

def assign_ips_and_up(net, topo):
    info("*** Assigning per-link /30 IPs and bringing interfaces up\n")
    for a, b in EDGES:
        ida, idb = NODE_IDS[a], NODE_IDS[b]
        low, high = sorted((ida, idb))
        subnet = f"172.16.{low}{high}"
        ipa = f"{subnet}.1/30"
        ipb = f"{subnet}.2/30"

        ia = topo.link_map[(a, b)]
        ib = topo.link_map[(b, a)]

        # Flush and assign IPs to the correct interfaces
        net.get(a).cmd(f"ip addr flush dev {ia}")
        net.get(b).cmd(f"ip addr flush dev {ib}")
        net.get(a).cmd(f"ip addr add {ipa} dev {ia}")
        net.get(b).cmd(f"ip addr add {ipb} dev {ib}")
        net.get(a).cmd(f"ip link set {ia} up")
        net.get(b).cmd(f"ip link set {ib} up")

        # IMPORTANT: remove any static ARP hacks (they break neighbor discovery)
        net.get(a).cmd(f"ip neigh flush dev {ia}")
        net.get(b).cmd(f"ip neigh flush dev {ib}")

        info(f"{a}: {ia} -> {ipa} | {b}: {ib} -> {ipb}\n")

def check_neighbors(net, topo):
    info("\n*** Neighbor ping sanity per edge\n")
    for a, b in EDGES:
        ida, idb = NODE_IDS[a], NODE_IDS[b]
        low, high = sorted((ida, idb))
        subnet = f"172.16.{low}{high}"
        ipa = f"{subnet}.1"
        ipb = f"{subnet}.2"
        print(f"\n[{a} -> {b}] ping {ipb}")
        print(net.get(a).cmd(f"ping -c 1 -W 1 {ipb}"))

if __name__ == '__main__':
    setLogLevel('info')
    topo = MyTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=None)
    net.start()

    assign_ips_and_up(net, topo)
    check_neighbors(net, topo)  # 1-hop only; no forwarding/routes yet

    # Visibility to catch misbindings
    for n in NODE_IDS:
        print(f"\n=== {n} ===")
        print(net.get(n).cmd("ip -br addr"))
        print(net.get(n).cmd("ip link"))
        print(net.get(n).cmd("arp -n"))

    CLI(net)
    net.stop()