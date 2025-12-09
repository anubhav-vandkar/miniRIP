from mininet.net import Mininet
from mininet.node import Host, OVSSwitch
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel, info


NODE_IDS = {
    'u':1,
    'v':2,
    'ex':4,
    'w':3,
    'y':5,
    'z':6
}

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
        for h in NODE_IDS:
            self.addHost(h)

        for a, b in EDGES:
            self.addLink(a, b)

def get_intf_name(node, neighbor):
    node_obj = node
    for intf in node_obj.intfList():
        link = intf.link
        if link is None:
            continue
        intf1, intf2 = link.intf1, link.intf2
        # Check which endpoint is the neighbor
        if intf1.node == node_obj and intf2.node == neighbor:
            return intf1.name
        if intf2.node == node_obj and intf1.node == neighbor:
            return intf2.name
    raise Exception(f"No interface between {node.name} and {neighbor.name}")

def assign_ips(net):
    info("*** Assigning IPs using real Mininet interfaces\n")

    for a, b in EDGES:
        na = net.get(a)
        nb = net.get(b)

        ida = NODE_IDS[a]
        idb = NODE_IDS[b]
        low, high = sorted((ida, idb))
        subnet = f"172.16.{low}{high}"
        ipa = f"{subnet}.1/30"
        ipb = f"{subnet}.2/30"

        intfA = get_intf_name(na, nb)
        intfB = get_intf_name(nb, na)

        info(f"{a} {intfA} <- {ipa}\n")
        na.cmd(f"ip addr add {ipa} dev {intfA}")
        na.cmd(f"ip link set {intfA} up")

        info(f"{b} {intfB} <- {ipb}\n")
        nb.cmd(f"ip addr add {ipb} dev {intfB}")
        nb.cmd(f"ip link set {intfB} up")

if __name__ == "__main__":
    setLogLevel('info')

    topo = MyTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=None)
    net.start()

    assign_ips(net)

    info("*** Testing neighbor connectivity\n")
    for a,b in EDGES:
        h = net.get(a)
        print(h.cmd(f"ping -c1 172.16.{min(NODE_IDS[a],NODE_IDS[b])}{max(NODE_IDS[a],NODE_IDS[b])}.{NODE_IDS[b]}"))


    info("*** Testing DIRECT neighbor connectivity\n")
    for a, b in EDGES:
        ida = NODE_IDS[a]
        idb = NODE_IDS[b]
        low, high = sorted((ida, idb))
        subnet = f"172.16.{low}{high}"

        # a's neighbor IP
        if ida < idb:
            target_for_a = f"{subnet}.2"
            target_for_b = f"{subnet}.1"
        else:
            target_for_a = f"{subnet}.1"
            target_for_b = f"{subnet}.2"

        na = net.get(a)
        nb = net.get(b)

        print(f"{a} -> {b}:")
        print(na.cmd(f"ping -c1 -W1 {target_for_a}"))

        print(f"{b} -> {a}:")
        print(nb.cmd(f"ping -c1 -W1 {target_for_b}"))

    info("*** Testing full pingAll (multi-hop will fail without routing)\n")
    net.pingAll()

    CLI(net)
    net.stop()