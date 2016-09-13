import sys
import os
from struct import *
import time
import socket
import random

DELAY = 0.5
VERBOSE = "sensible" # on|off|sensible|silly
BUFSIZE = 1024
artnet_port = 6454

artnet_pkt = b"\x41\x72\x74\x2d\x4e\x65\x74\x00\x00\x50\x00\x0e\x00\x00\x00\x00\x00\x10\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"

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
        #data.append(0xFE)
        data.append(random.randint(0,255))
    return gen_artnet_pkt(data)

def pktgen(addr="255.255.255.255"):
#    broadcast_addr = "255.255.255.255"
    broadcast_addr = addr
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

if __name__ == "__main__":
    addr = "255.255.255.255"
    print(len(sys.argv))
    if len(sys.argv) == 2: 
        addr = sys.argv[1]
    pktgen(addr)
