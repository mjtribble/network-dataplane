"""
Created on Oct 12, 2016

@author: mwitt_000
"""

import network_2
import link_2
import threading
from time import sleep

# configuration parameters
router_queue_size = 0  # 0 means unlimited

# may need to increase...
<<<<<<< HEAD:simulation.py
simulation_time = 5  # give the network sufficient time to transfer all packets before quitting
=======
simulation_time = 5 # give the network1 sufficient time to transfer all packets before quitting
>>>>>>> 8afe9bc33159e9e141b68078996e5a012e029739:Part2/simulation_2.py

if __name__ == '__main__':
    object_L = []  # keeps track of objects, so we can kill their threads

    # create network1 nodes
    # add hosts to list
    # TODO: #3 Add more hosts and links ( Host1, Host2, Host3(server), RouterA, RouterB, RouterC, RouterD )
    client1 = network_2.Host(1)
    object_L.append(client1)
    server1 = network_2.Host(2)
    object_L.append(server1)

    #adding another server
    client2 = network.Host(3)
    server2 = network.Host(4)
    object_L.append(client2)
    object_L.append(server2)

    # add routers to list
<<<<<<< HEAD:simulation.py
    router_a = network.Router(name='A', intf_count=4, max_queue_size=router_queue_size)
    router_b = network.Router(name='B', intf_count=4, max_queue_size=router_queue_size)
    router_c = network.Router(name='C', intf_count=4, max_queue_size=router_queue_size)
    router_d = network.Router(name='D', intf_count=4, max_queue_size=router_queue_size)
=======
    router_a = network_2.Router(name='A', intf_count=1, max_queue_size=router_queue_size)
>>>>>>> 8afe9bc33159e9e141b68078996e5a012e029739:Part2/simulation_2.py
    object_L.append(router_a)
    object_L.append(router_b)
    object_L.append(router_c)
    object_L.append(router_d)

    # create a Link Layer to keep track of link1s between network1 nodes
    # add LinkLayer to list
    link_layer = link_2.LinkLayer()
    object_L.append(link_layer)

    # add all the links to the LinkLayer
    # specify the mtu at the end.
<<<<<<< HEAD:simulation.py
    #second and fourth element pertains to the interface, changing them to work with routing table
    # link_layer.add_link(link.Link(client1, 0, router_a, 1, 50))     #from client 1 and two on interface 0, forward to router a
    # link_layer.add_link(link.Link(router_a, 1, router_b, 2, 30))
    # link_layer.add_link(link.Link(router_b, 2, router_d, 3, 30))
    # link_layer.add_link(link.Link(router_d, 3, client2, 0, 30))

    link_layer.add_link(link.Link(server1, 0, router_a, 1, 50))
    link_layer.add_link(link.Link(router_a, 1, router_c, 2, 30))
    link_layer.add_link(link.Link(router_c, 2, router_d, 3, 30))
    link_layer.add_link(link.Link(router_d, 3, server2, 0, 30))
=======
    link_layer.add_link(link_2.Link(client1, 0, router_a, 0, 50))
    link_layer.add_link(link_2.Link(router_a, 0, server1, 0, 30))
>>>>>>> 8afe9bc33159e9e141b68078996e5a012e029739:Part2/simulation_2.py

    # this is the minimum of the link layer's mtu's and sent in to the udt for fragment sizing.
    min_mtu = 30

    # start all the objects
    # TODO: #3 Start new object threads
    thread_L = [threading.Thread(name=client1.__str__(), target=client1.run),
                threading.Thread(name=server1.__str__(), target=server1.run),
                threading.Thread(name=client2.__str__(), target=client2.run),
                threading.Thread(name=server2.__str__(), target=server2.run),
                threading.Thread(name=router_a.__str__(), target=router_a.run),
                threading.Thread(name=router_b.__str__(), target=router_b.run),
                threading.Thread(name=router_c.__str__(), target=router_c.run),
                threading.Thread(name=router_d.__str__(), target=router_d.run),
                threading.Thread(name="Network", target=link_layer.run)]

    for t in thread_L:
        t.start()

    data = ''

    for i in range(43, 50):
        data += chr(i)

<<<<<<< HEAD:simulation.py
    print('Initial Data: ' + data)

=======
>>>>>>> 8afe9bc33159e9e141b68078996e5a012e029739:Part2/simulation_2.py
    # send message -> destination, source, data
    # client(host 1) sending to server(host 2)
    source = 1
    destination = 3
    pkt_id = 1  # this will increment with each packet from the same source
    server1.udt_send(destination, source, pkt_id, data, min_mtu)

    # # give the network1 sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    # join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")

    # writes to host periodically
