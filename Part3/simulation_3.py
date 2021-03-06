"""
Created on Oct 12, 2016

@author: mwitt_000
"""

import network_3
import link_3
import threading
from time import sleep

# configuration parameters
router_queue_size = 0  # 0 means unlimited

# may need to increase...
simulation_time = 5  # give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = []  # keeps track of objects, so we can kill their threads

    # create network nodes
    host_1 = network_3.Host(1)
    host_2 = network_3.Host(2)
    host_3 = network_3.Host(3)
    host_4 = network_3.Host(4)

    # add hosts to list
    object_L.append(host_1)
    object_L.append(host_2)
    object_L.append(host_3)
    object_L.append(host_4)

    # create routing tables
    # [h1_dest, h1_out], [h2_dest, h2_out]
    table_a = ([3, 1], [3, 0])
    table_b = ([3, 0], [])
    table_c = ([], [3, 0])
    table_d = ([3, 0], [3, 0])

    # create routers
    router_a = network_3.Router(name='A', intf_count=2, max_queue_size=router_queue_size, routing_table=table_a)
    router_b = network_3.Router(name='B', intf_count=1, max_queue_size=router_queue_size, routing_table=table_b)
    router_c = network_3.Router(name='C', intf_count=1, max_queue_size=router_queue_size, routing_table=table_c)
    router_d = network_3.Router(name='D', intf_count=1, max_queue_size=router_queue_size, routing_table=table_d)

    # add routers to list
    object_L.append(router_a)
    object_L.append(router_b)
    object_L.append(router_c)
    object_L.append(router_d)

    # create a Link Layer to keep track of links between network nodes
    # add LinkLayer to list
    link_layer = link_3.LinkLayer()
    object_L.append(link_layer)

    # add all the links to the LinkLayer
    # specify the mtu at the end.
    # second and fourth element pertains to the interface, changing them to work with routing table
    # second = from interface, fourth = to interface

    # HOST 1 links
    link_layer.add_link(link_3.Link(host_1, 0, router_a, 0, 50))

    # HOST 2 links
    link_layer.add_link(link_3.Link(host_2, 0, router_a, 1, 50))

    # ROUTER A links
    link_layer.add_link(link_3.Link(router_a, 0, router_c, 0, 30))
    link_layer.add_link(link_3.Link(router_a, 1, router_b, 0, 30))

    # ROUTER B links
    link_layer.add_link(link_3.Link(router_b, 0, router_d, 0, 30))

    # ROUTER C links
    link_layer.add_link(link_3.Link(router_c, 0, router_d, 0, 30))

    # ROUTER D links
    link_layer.add_link(link_3.Link(router_d, 0, host_3, 0, 30))

    # this is the minimum of the link layer's mtu's and sent in to the udt for fragment sizing.
    min_mtu = 30

    # start all the objects
    # TODO: #3 Start new object threads
    thread_L = [threading.Thread(name=host_1.__str__(), target=host_1.run),
                threading.Thread(name=host_2.__str__(), target=host_2.run),
                threading.Thread(name=host_3.__str__(), target=host_3.run),
                threading.Thread(name=host_4.__str__(), target=host_4.run),
                threading.Thread(name=router_a.__str__(), target=router_a.run),
                threading.Thread(name=router_b.__str__(), target=router_b.run),
                threading.Thread(name=router_c.__str__(), target=router_c.run),
                threading.Thread(name=router_d.__str__(), target=router_d.run),
                threading.Thread(name="Network", target=link_layer.run)]

    for t in thread_L:
        t.start()

    # data = ''
    #
    # for i in range(43, 123):
    #     data += chr(i)

    pkt_id = 1  # this will increment with each packet from the same source

    data = 'This is the packet that has been sent from host 1 through router B to host 3'
    print('Initial Data Host 1: ' + data)

    # (destination, source,...)
    host_1.udt_send(3, 1, pkt_id, data, min_mtu)

    data = 'Hi hello how are you this is the lovely host number 2 sending through router c to host 3'
    print('Initial Data Host 1: ' + data)

    # (destination, source,...)
    host_2.udt_send(3, 2, pkt_id, data, min_mtu)

    # give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    # join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")

    # writes to host periodically
