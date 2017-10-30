"""
Created on Oct 12, 2016

@author: mwitt_000
"""

import network
import link
import threading
from time import sleep

# configuration parameters
router_queue_size = 0  # 0 means unlimited

# may need to increase...
simulation_time = 1  # give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = []  # keeps track of objects, so we can kill their threads

    # create network nodes
    # add hosts to list
    # TODO: #3 Add more hosts and links ( Host1, Host2, Host3(server), RouterA, RouterB, RouterC, RouterD )
    client1 = network.Host(1)
    object_L.append(client1)
    server1 = network.Host(2)
    object_L.append(server1)

    # add routers to list
    router_a = network.Router(name='A', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_a)

    # create a Link Layer to keep track of links between network nodes
    # add LinkLayer to list
    link_layer = link.LinkLayer()
    object_L.append(link_layer)

    # add all the links to the LinkLayer
    link_layer.add_link(link.Link(client1, 0, router_a, 0, 50))
    link_layer.add_link(link.Link(router_a, 0, server1, 0, 30))

    # start all the objects
    # TODO: #3 Start new object threads
    thread_L = [threading.Thread(name=client1.__str__(), target=client1.run),
                threading.Thread(name=server1.__str__(), target=server1.run),
                threading.Thread(name=router_a.__str__(), target=router_a.run),
                threading.Thread(name="Network", target=link_layer.run)]

    for t in thread_L:
        t.start()

        # create a string 70 chars long to send, 5 chars are added to the begining number
    data = ''

    for i in range(65, 145):
        data += chr(i)

    print(data)

    # send message -> destination, source, data
    # client(host 1) sending to server(host 2)
    source = 1
    destination = 2
    pkt_id = 1  # this will increment with each packet from the same source
    client1.udt_send(destination, source, pkt_id, data, 30)

    # give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    # join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")

    # writes to host periodically
