from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class MyTopo(Topo):
    def build(self):
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2')  # IP will be set later
        r1 = self.addHost('r1')  # IPs will be set later
        s1 = self.addSwitch('s1')

        self.addLink(h1, s1)
        self.addLink(r1, s1)
        self.addLink(h2, r1, intfName1='h2-eth0', intfName2='r1-eth1')

if __name__ == '__main__':
    setLogLevel('info')
    topo = MyTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=None)
    net.start()
    # Assign IPs
    h1 = net.get('h1')
    h2 = net.get('h2')
    r1 = net.get('r1')

    # Assign IPs
    h1.cmd('ifconfig h1-eth0 10.0.0.1/24')
    r1.cmd('ifconfig r1-eth0 10.0.0.254/24')
    r1.cmd('ifconfig r1-eth1 10.0.1.254/24')
    h2.cmd('ifconfig h2-eth0 10.0.1.1/24')

    # Enable IP forwarding
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Add routes
    h1.cmd('ip route add default via 10.0.0.254')
    h2.cmd('ip route add default via 10.0.1.254')

    # Test connectivity
    print(h1.cmd('ping -c 3 10.0.1.1'))
    print(h1.cmd('ip addr'))
    print(r1.cmd('ip addr'))
    print(h2.cmd('ip addr'))
    print(r1.cmd('ping -c 3 10.0.1.1'))

    CLI(net)
    net.stop()
