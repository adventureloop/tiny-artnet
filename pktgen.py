import sys
import os
from struct import *
import time
import socket
import random

DELAY = 5
VERBOSE = "sensible" # on|off|sensible|silly
BUFSIZE = 1024
artnet_port = 6454

artnet_pkt = "\x41\x72\x74\x2d\x4e\x65\x74\x00\x00\x50\x00\x0e\x00\x00\x00\x00\x00\x10\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"

container = None
selected = [0,0]

def gen_artnet_pkt(data,universe=0x00):
    length = len(data)

    if length > 513:
        print("too long")
        return ""

    name = b"Art-Net"
    zero = 0 
    opcode = 0x0050
    protovers = 14
    seq = 0
    phys = 0
    
    pkt_hdr = pack("!7sBHHBBHH", name, zero, opcode,\
        protovers, seq, phys, universe, length)

    return pkt_hdr + data

def rand_artnet_pkt(full=False):
    data = bytearray()
    for x in range(512):
        data.append(random.randint(0, 255))
    return data
    #return gen_artnet_pkt(os.urandom(512))

def parse_artnet_pkt(data):

    data_len = len(data)

    if data_len < 20:
        return "", data

    header = data[:18]

    name, zero, opcode, protovers, seq, phys, \
        universe, length = unpack("7sBHHBBHH",header)

    #TODO don't do this, it flattens the universe, who knows how many will die?
    #universe = 0x00

    pkt_hdr = pack("!7sBHHBBHH", name, zero, opcode,\
        protovers, seq, phys, universe, length)
    length = length
    total_len = 18 + length

    if length >= 2 and total_len <= data_len:
        pkt_data = data[18:total_len] 
#return pkt_hdr + pkt_data, data[total_len:] #I have no idea what this does
        return pkt_hdr, pkt_data
    else: 
        print("bad packet")
        return "", data

def pktgen():
    broadcast_addr = "255.255.255.255"
    print("       sending to: {} {} every {} seconds"
        .format(broadcast_addr, artnet_port, DELAY))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  #required on a unix system

    while True:
        pkt = rand_artnet_pkt()

        if VERBOSE == "silly":
            print(hexdump(pkt))

        sock.sendto(pkt, (broadcast_addr, artnet_port))

        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(DELAY)

def pktshow(displaycb):
    broadcast_addr = "255.255.255.255"
    broadcast_addr = "0.0.0.0"
    print("          receiving from {} {}"
        .format(broadcast_addr, artnet_port))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    sock.bind((broadcast_addr,artnet_port))

    while True:
        pkt,addr = sock.recvfrom(BUFSIZE) #blocks
        print("addr {}".format(addr))

        if VERBOSE == "silly":
            print(hexdump(pkt))

        pkt = parse_artnet_pkt(pkt)
        displaycb(pkt)

        sys.stdout.write(".")
        sys.stdout.flush()
        #time.sleep(DELAY)

if __name__ == "__main__":
    pktgen()

