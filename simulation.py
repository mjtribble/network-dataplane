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
    client = network.Host(1)
    object_L.append(client)
    server = network.Host(2)
    object_L.append(server)

    # add routers to list
    router_a = network.Router(name='A', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_a)

    # create a Link Layer to keep track of links between network nodes
    # add LinkLayer to list
    link_layer = link.LinkLayer()
    object_L.append(link_layer)

    # add all the links to the LinkLayer
    link_layer.add_link(link.Link(client, 0, router_a, 0, 50))

    # changed this from 50 to 30 via video.
    link_layer.add_link(link.Link(router_a, 0, server, 0, 30))

    # start all the objects
    thread_L = [threading.Thread(name=client.__str__(), target=client.run),
                threading.Thread(name=server.__str__(), target=server.run),
                threading.Thread(name=router_a.__str__(), target=router_a.run),
                threading.Thread(name="Network", target=link_layer.run)]

    for t in thread_L:
        t.start()

    # create some send events
    for i in range(3):
        client.udt_send(2, 'Sample data %d' % i)  # client(host 1) sending to server(host 2)

    # give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    # join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")

    # writes to host periodically