### Author: tj <tj@enoti.me>
### Description: Scottish Consulate Techno Disco(Node edition)
### Category: Other
### License: BSD 3

import sys
import os
from struct import *
import time
import socket

DELAY = 5
VERBOSE = "sensible" # on|off|sensible|silly
BUFSIZE = 1024
artnet_port = 6454

def parse_artnet_pkt(data):
    data_len = len(data)

    if data_len < 20:
        return "", data
    print("packet len {}", data_len)

    header = data[:18]

    name, zero, opcode, protovers, seq, phys, \
        universe, length = unpack("!7sBHHBBHH",header)
    print("name: {}, zero: {}, opcode: {}, protovers: {}, seq: {}, phys: {}, universe: {}, length: {}".format(
        name, zero, opcode, protovers, seq, phys, universe, length))

    pkt_hdr = pack("!7sBHHBBHH", name, zero, opcode,\
        protovers, seq, phys, universe, length)
    artnet_pkt_len = 18 + length

    print("length {} total_len {} data_len {}".format(length, artnet_pkt_len, data_len))
    if length >= 2 and artnet_pkt_len  <= data_len:
        pkt_data = data[18:artnet_pkt_len] 
        return pkt_hdr, pkt_data
    else: 
        print("bad packet")
        return "", data

def pktshow(displaycb):
    broadcast_addr = "255.255.255.255" # we should bind to this
#    broadcast_addr = "0.0.0.0" #the emfbadge doesn't behave here
    print("          receiving from {} {}"
        .format(broadcast_addr, artnet_port))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #emfcamp badge doesn't support socket options
    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    sock.bind((broadcast_addr,artnet_port))

    while True:
        pkt,addr = sock.recvfrom(BUFSIZE) #blocks
        print("addr {}".format(addr))

        pkt_hdr, pkt_data = parse_artnet_pkt(pkt)
        displaycb(pkt_data)

def drawdata(data):
    print(data)

#if __name__ == "__main__":
print("starting")

ugfx.init()
ugfx.clear()
ugfx.set_default_font(ugfx.FONT_SMALL)
container = ugfx.Container(0, 80,320,160)

pktshow(drawdata)
