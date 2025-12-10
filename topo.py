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

def assign_ips(net):
    for a,b in EDGES:
        ha = net.get(a)
        hb = net.get(b)

        # Get actual Mininet interface names
        intfA = ha.connectionsTo(hb)[0][0].name
        intfB = ha.connectionsTo(hb)[0][1].name

        ida = NODE_IDS[a]
        idb = NODE_IDS[b]

        lo,hi = sorted([ida,idb])
        subnet = f"172.16.{lo}{hi}"

        ipa = f"{subnet}.{ida}/24"
        ipb = f"{subnet}.{idb}/24"

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

    info("\n* Immediate neighbor tests should PASS\n")
    for a,b in EDGES:
        ida,idb = NODE_IDS[a], NODE_IDS[b]
        lo,hi = sorted([ida,idb])
        ip = f"172.16.{lo}{hi}.{idb}"
        print(net.get(a).cmd(f"ping -c1 {ip}"))

    CLI(net)
    net.stop()