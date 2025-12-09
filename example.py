from mininet.net import Mininet
from mininet.node import Host, OVSSwitch
from mininet.topo import Topo
from mininet.cli import CLI

class MyTopo( Topo ):
    def build( self ):
        h1 = self.addHost( 'h1', ip='10.0.0.1/24' )
        h2 = self.addHost( 'h2', ip='10.0.1.1/24' )
        r1 = self.addHost( 'r1', ip='10.0.0.254/24' ) # Router
        s1 = self.addSwitch( 's1' )

        self.addLink( h1, s1 )
        self.addLink( r1, s1 )
        self.addLink( h2, r1, intfName1='r1-eth1', intfName2='h2-eth0' ) # Connect h2 to r1

        # Set up routing on r1
        # Add a route on r1 to reach h2's network (10.0.1.0/24) via h2-eth0 (its interface connected to h2)
        # Assuming r1 already has an IP on r1-eth0 (connected to s1)
        # For a simple direct connection to h2, you might not strictly need this if r1 is directly connected
        # but it demonstrates adding routes.
        r1.cmd( 'ip route add 10.0.1.0/24 dev r1-eth1' )

        # Set up default route on h1 to go through r1
        h1.cmd( 'ip route add default via 10.0.0.254' )

        # Set up default route on h2 to go through r1
        h2.cmd( 'ip route add default via 10.0.1.254' ) # Assuming r1 has 10.0.1.254 on r1-eth1

if __name__ == '__main__':
    topo = MyTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=None)
    net.start()

    # Now you can get the actual Host objects
    r1 = net.get('r1')
    h1 = net.get('h1')
    h2 = net.get('h2')

    # Configure routing
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')
    r1.cmd('ip route add 10.0.1.0/24 dev r1-eth1')
    h1.cmd('ip route add default via 10.0.0.254')
    h2.cmd('ip route add default via 10.0.1.254')

    # Test connectivity
    h1.cmd('ping -c 1 10.0.1.1')

    CLI(net)
    net.stop()
