"""
Created on Oct 12, 2016

@author: mwitt_000
"""

import network1
import link1
import threading
from time import sleep

# configuration parameters
router_queue_size = 0  # 0 means unlimited

# may need to increase...
simulation_time = 1  # give the network1 sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = []  # keeps track of objects, so we can kill their threads

    # create network1 nodes
    # add hosts to list
    client = network1.Host(1)
    object_L.append(client)
    server = network1.Host(2)
    object_L.append(server)

    # add routers to list
    router_a = network1.Router(name='A', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_a)

    # create a Link Layer to keep track of link1s between network1 nodes
    # add LinkLayer to list
    link_layer = link1.LinkLayer()
    object_L.append(link_layer)

    # add all the link1s to the LinkLayer
    link_layer.add_link(link1.Link(client, 0, router_a, 0, 50))

    # changed this from 50 to 30 via video.
    link_layer.add_link(link1.Link(router_a, 0, server, 0, 50))

    # start all the objects
    thread_L = [threading.Thread(name=client.__str__(), target=client.run),
                threading.Thread(name=server.__str__(), target=server.run),
                threading.Thread(name=router_a.__str__(), target=router_a.run),
                threading.Thread(name="Network", target=link_layer.run)]

    for t in thread_L:
        t.start()

    # create a string 70 chars long to send, 5 chars are added to the begining number
    testString = ''
    first = ''
    second = ''

    for i in range(80):
        testString += '~'

    if len(testString) >= 80:
        first = testString[0:40]
        second = testString[40:70]
    print (len(first))

    # create some send events
    client.udt_send(2, first)
    client.udt_send(2, second)

    # for i in range(3):
    #     client.udt_send(2, 'Hello %d' % i)  # client(host 1) sending to server(host 2)

    # # give the network1 sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    # join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")

    # writes to host periodically
