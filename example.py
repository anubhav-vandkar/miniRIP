from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class MyTopo(Topo):
    def build(self):
        # Define hosts and switch
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.1.1/24')
        r1 = self.addHost('r1')  # IPs will be added later
        s1 = self.addSwitch('s1')

        # Connect h1 and r1 to switch
        self.addLink(h1, s1)
        self.addLink(r1, s1)

        # Connect h2 directly to r1
        self.addLink(h2, r1, intfName1='h2-eth0', intfName2='r1-eth1')

if __name__ == '__main__':
    setLogLevel('info')
    topo = MyTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=None)
    net.start()

    # Get host objects
    h1 = net.get('h1')
    h2 = net.get('h2')
    r1 = net.get('r1')

    # Assign IPs to r1 interfaces
    r1.cmd('ifconfig r1-eth0 10.0.0.254/24')
    r1.cmd('ifconfig r1-eth1 10.0.1.254/24')

    # Enable IP forwarding on r1
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Add routes
    r1.cmd('ip route add 10.0.1.0/24 dev r1-eth1')
    h1.cmd('ip route add default via 10.0.0.254')
    h2.cmd('ip route add default via 10.0.1.254')

    # Test connectivity
    info("*** Testing connectivity from h1 to h2\n")
    print(h1.cmd('ping -c 3 10.0.1.1'))

    CLI(net)
    net.stop()
