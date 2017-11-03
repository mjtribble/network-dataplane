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
    # add hosts to list
    # TODO: #3 Add more hosts and links ( host_1, Host2, host_3(server), RouterA, RouterB, RouterC, RouterD )
    host_1 = network_3.Host(1)
    object_L.append(host_1)
    host_2 = network_3.Host(2)
    object_L.append(host_2)

    # adding another server
    host_3 = network_3.Host(3)
    host_4 = network_3.Host(4)
    object_L.append(host_3)
    object_L.append(host_4)

    # add routers to list
    router_a = network_3.Router(name='A', intf_count=2, max_queue_size=router_queue_size)
    router_b = network_3.Router(name='B', intf_count=1, max_queue_size=router_queue_size)
    router_c = network_3.Router(name='C', intf_count=1, max_queue_size=router_queue_size)
    router_d = network_3.Router(name='D', intf_count=2, max_queue_size=router_queue_size)
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
    #second and fourth element pertains to the interface, changing them to work with routing table
    link_layer.add_link(link_3.Link(host_1, 0, router_a, 0, 50))     #from client 1 and two on interface 0, forward to router a
    link_layer.add_link(link_3.Link(router_a, 0, router_b, 0, 30))
    link_layer.add_link(link_3.Link(router_b, 0, router_d, 0, 30))
    link_layer.add_link(link_3.Link(router_d, 0, host_3, 0, 30))

    link_layer.add_link(link_3.Link(host_2, 0, router_a, 1, 50))
    link_layer.add_link(link_3.Link(router_a, 1, router_c, 0, 30))
    link_layer.add_link(link_3.Link(router_c, 0, router_d, 1, 30))
    link_layer.add_link(link_3.Link(router_d, 1, host_4, 0, 30))

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

    data = ''

    for i in range(43, 123):
        data += chr(i)

    print('Initial Data: ' + data)

    # send message -> destination, source, data
    # client(host 1) sending to server(host 2)
    source = 2
    destination = 4
    pkt_id = 1  # this will increment with each packet from the same source
    host_1.udt_send(destination, source, pkt_id, data, min_mtu)

    # give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    # join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")

    # writes to host periodically
