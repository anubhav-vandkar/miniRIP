from mininet.net import Mininet
from mininet.node import Host, OVSSwitch
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel, info

NODE_IDS = {
    'u':1,
    'v':2,
    'w':3,
    'ex':4,
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
        for n in NODE_IDS:
            self.addHost(n)
        for a,b in EDGES:
            self.addLink(a,b)

def bring_up_all_interfaces(net):
    for host in net.hosts:
        for intf in host.intfList():
            if str(intf) != 'lo':
                host.cmd(f"ip link set {intf.name} up")

def assign_ips(net):
    for i, (a, b) in enumerate(EDGES):
        ha = net.get(a)
        hb = net.get(b)

        intfA, intfB = ha.connectionsTo(hb)[0]
        intfA = intfA.name
        intfB = intfB.name

        subnet = f"10.0.{i}.0/30"
        ipa = f"10.0.{i}.1/30"
        ipb = f"10.0.{i}.2/30"

        ha.cmd(f"ip addr flush dev {intfA}")
        hb.cmd(f"ip addr flush dev {intfB}")
        ha.cmd(f"ip addr add {ipa} dev {intfA}")
        hb.cmd(f"ip addr add {ipb} dev {intfB}")
        ha.cmd(f"ip link set {intfA} up")
        hb.cmd(f"ip link set {intfB} up")

        info(f"{a}-{b}: {intfA}={ipa}, {intfB}={ipb}\n")


if __name__ == "__main__":
    setLogLevel('info')
    topo = MyTopo()
    net = Mininet(topo=topo, controller=None)
    net.start()

    assign_ips(net)

    bring_up_all_interfaces(net)

    for h in net.hosts:
        print(h.name, h.cmd("ip -br addr"))

    print(net.get('w').cmd("ip link"))

    print(net.get('u').cmd("ping -c1 10.0.0.2"))  # ping ex on edge 0
    print(net.get('v').cmd("ping -c1 10.0.1.2"))  # ping w on edge 1
    print(net.get('v').cmd("ping -c1 10.0.2.2"))  # ping w
    print(net.get('w').cmd("ping -c1 10.0.2.1"))  # ping v


    # info("\n* Immediate neighbor tests should PASS\n")
    # for a,b in EDGES:
    #     ida,idb = NODE_IDS[a], NODE_IDS[b]
    #     lo,hi = sorted([ida,idb])
    #     ip = f"172.16.{lo}{hi}.{idb}"
    #     print(net.get(a).cmd(f"ping -c1 {ip}"))

    CLI(net)
    net.stop()