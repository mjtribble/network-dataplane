"""
Created on Oct 12, 2016

@author: mwitt_000
"""
import queue
import threading


# wrapper class for a queue of packets
class Interface:
    # @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize);
        self.mtu = None

    # get packet from the queue interface
    def get(self):
        try:
            return self.queue.get(False)
        except queue.Empty:
            return None

    # put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, block=False):
        self.queue.put(pkt, block)


# Implements a network layer packet (different from the RDT packet
# from programming assignment 2).
class NetworkPacket:
    # packet header encoding lengths
    length_S_length = 2
    pkt_id_S_length = 2
    flag_S_length = 2
    offset_S_length = 3
    dest_addr_S_length = 2
    source_addr_S_length = 2

    header_length = dest_addr_S_length \
                    + source_addr_S_length \
                    + pkt_id_S_length \
                    + flag_S_length \
                    + offset_S_length \
                    + length_S_length

    # @param dest_addr: address of the destination host
    # @param length: payload's length
    # @param id: packet's id
    # @param flag: packet payload
    # @param data_S: packet payload
    def __init__(self, length, pkt_id, flag, offset, dest_addr, source_addr, data_S, ):
        self.length = length
        self.pkt_id = pkt_id
        self.flag = flag
        self.offset = offset
        self.dest_addr = dest_addr
        self.source_addr = source_addr
        self.data_S = data_S

    # called when printing the object
    def __str__(self):
        return self.to_byte_S()

    # convert packet to a byte string for transmission over links
    # length, pkt_id, flag, offset, dest_addr, source_addr, data_S,
    def to_byte_S(self):
        byte_S = str(self.length).zfill(self.length_S_length)
        byte_S += str(self.pkt_id).zfill(self.pkt_id_S_length)
        byte_S += str(self.flag).zfill(self.flag_S_length)
        byte_S += str(self.offset).zfill(self.offset_S_length)
        byte_S += str(self.dest_addr).zfill(self.dest_addr_S_length)
        byte_S += str(self.source_addr).zfill(self.source_addr_S_length)
        byte_S += self.data_S
        return byte_S

    # extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        # length, pkt_id, flag, offset, dest_addr, source_addr, data_S,

        length = int(byte_S[0: NetworkPacket.length_S_length])
        byte_S = byte_S[NetworkPacket.length_S_length:]

        pkt_id = int(byte_S[0: NetworkPacket.pkt_id_S_length])
        byte_S = byte_S[NetworkPacket.pkt_id_S_length:]

        flag = int(byte_S[0: NetworkPacket.flag_S_length])
        byte_S = byte_S[NetworkPacket.flag_S_length:]

        offset = int(byte_S[0: NetworkPacket.offset_S_length])
        byte_S = byte_S[NetworkPacket.offset_S_length:]

        dest_addr = int(byte_S[0: NetworkPacket.dest_addr_S_length])
        byte_S = byte_S[NetworkPacket.dest_addr_S_length:]

        source_addr = int(byte_S[0: NetworkPacket.source_addr_S_length])
        byte_S = byte_S[NetworkPacket.source_addr_S_length:]

        data_S = byte_S

        # length, pkt_id, flag, offset, dest_addr, source_addr, data_S,
        return self(length, pkt_id, flag, offset, dest_addr, source_addr, data_S)


# Implements a network host for receiving and transmitting data
class Host:
    global receiveList_1, receiveList_2
    receiveList_1 = []
    receiveList_2 = []

    # @param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.in_intf_L = [Interface()]
        self.out_intf_L = [Interface()]
        self.stop = False  # for thread termination

    # called when printing the object
    def __str__(self):
        return 'Host_%s' % self.addr

    # This implements fragmentation of a packet
    # create a packet and enqueue for transmission
    # @param dest_addr: destination address for the packet
    # @param source_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dest_addr, source_addr, pkt_id, data_S, min_mtu):

        total_frag_size = min_mtu
        data_frag_size = total_frag_size - NetworkPacket.header_length
        pkt_data_length = len(data_S)
        temp_pkt_length = pkt_data_length
        offset = 0  # the offset is disregards the header length. Only finds the data

        while temp_pkt_length > data_frag_size:  # packet is too large, split it up
            flag = 1
            packet = NetworkPacket(total_frag_size, pkt_id, flag, offset, dest_addr, source_addr,
                                   data_S[:data_frag_size])
            self.out_intf_L[0].put(packet.to_byte_S())  # send packets always enqueued successfully
            print('%s: sending packet "%s" with id %d, and offset %d, out interface with mtu=%d'
                  % (self, packet, pkt_id, offset, self.out_intf_L[0].mtu))
            data_S = data_S[data_frag_size:]  # remaining data to be sent
            temp_pkt_length = len(data_S)  # sets the new length

            if temp_pkt_length <= data_frag_size:
                offset += temp_pkt_length
            else:
                offset += total_frag_size - NetworkPacket.header_length

        if temp_pkt_length <= data_frag_size:  # packet is the correct size
            flag = 0  # this is the only / last packet
            packet_size = temp_pkt_length + NetworkPacket.header_length
            packet = NetworkPacket(packet_size, pkt_id, flag, offset, dest_addr, source_addr, data_S)
            self.out_intf_L[0].put(packet.to_byte_S())  # send packets always enqueued successfully
            print('%s: sending packet "%s" with id %d, and offset %d, out interface with mtu=%d'
                  % (self, packet, pkt_id, offset, self.out_intf_L[0].mtu))

    # receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.in_intf_L[0].get()

        if pkt_S is not None:
            packet = NetworkPacket.from_byte_S(pkt_S)

            # Packet is from Host 1
            if packet.source_addr is 1:
                receiveList_1.append(pkt_S)
                # checks the flag of pkt_S if 0 all data has been sent else, keep receiving
                if packet.flag == 0:
                    raw_result_1 = ''

                    result1 = ''

                    # sorts list based on the headers, last element goes to the from of the list due to flag = 0,
                    # therefore we pop and append it to the end of the list to get it in order
                    # may need to change this for part 3
                    receiveList_1.sort()
                    receiveList_1.append(receiveList_1.pop(0))

                    for i in range(len(receiveList_1)):
                        data = receiveList_1[i]
                        packet = NetworkPacket.from_byte_S(data)
                        result1 += packet.data_S
                        raw_result_1 += data

                    print('%s: received packets "%s"' % (self, raw_result_1))

                    print('%s: parsed packet "%s"' % (self, result1))

            # Packet is from Host 2
            if packet.source_addr is 2:
                receiveList_2.append(pkt_S)

                # checks the flag of pkt_S if 0 all data has been sent else, keep receiving
                if packet.flag == 0:
                    raw_result_2 = ''

                    result2 = ''

                    # sorts list based on the headers, last element goes to the from of the list due to flag = 0,
                    # therefore we pop and append it to the end of the list to get it in order
                    # may need to change this for part 3
                    receiveList_2.sort()
                    receiveList_2.append(receiveList_2.pop(0))

                    for j in range(len(receiveList_2)):
                        data = receiveList_2[j]
                        packet = NetworkPacket.from_byte_S(data)
                        result2 += packet.data_S
                        raw_result_2 += data

                    print('%s: received packets "%s"' % (self, raw_result_2))

                    print('%s: parsed packet "%s"' % (self, result2))


    def run(self):
        print(threading.currentThread().getName() + ': Starting')
        while True:
            # receive data arriving to the in interface
            self.udt_receive()
            # terminate
            if self.stop:
                print(threading.currentThread().getName() + ': Ending')
                return


# Implements a multi-interface router described in class
# We have been using 3 in interfaces and 3 out interfaces
class Router:
    # @param name: friendly router name for debugging
    # @param intf_count: the number of input and output interfaces // should be 3?
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, intf_count, max_queue_size, routing_table):
        self.stop = False  # for thread termination
        self.name = name
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.route_table = routing_table

    # called when printing the object
    def __str__(self):
        return 'Router_%s' % self.name

    # look through the content of incoming interfaces and forward to
    # appropriate outgoing interfaces
    # TODO: #3 implement Router forwarding table for new topology and pass into the Router Constructor
    def forward(self):
        x = 0
        for i in range(len(self.in_intf_L)):
            pkt_S = None
            try:
                # get packet from interface i
                pkt_S = self.in_intf_L[i].get()

                # if packet exists make a forwarding decision
                if pkt_S is not None:

                    p = NetworkPacket.from_byte_S(pkt_S)  # parse a packet out

                    if p.source_addr is 1:
                        address = self.route_table[0]

                    if p.source_addr is 2:
                        address = self.route_table[1]

                    forward_int = address[1]

                    # send through A->B->D->Host3
                    # elif p.dest_addr==2 and p.source_addr==4:

                    self.out_intf_L[forward_int].put(p.to_byte_S(), True)
                    print('%s: forwarding packet "%s" from interface %d to %d with mtu %d'% (self, p, i, forward_int, self.out_intf_L[i].mtu))
            except queue.Full:
                print('%s: packet "%s" lost on interface %d to %d with mtu %d'
                      % (self, p, i, forward_int, self.out_intf_L[i].mtu))
                pass

    # thread target for the host to keep forwarding data
    def run(self):
        print(threading.currentThread().getName() + ': Starting')
        while True:
            self.forward()
            if self.stop:
                print(threading.currentThread().getName() + ': Ending')
                return
