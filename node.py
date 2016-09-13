### Author: tj <tj@enoti.me>
### Description: Scottish Consulate Techno Disco(Node edition)
### Category: Other
### License: BSD 3

import sys
import os
from ustruct import *
import time
import socket
import machine
import neopixel

DELAY = 5
VERBOSE = "sensible" # on|off|sensible|silly
BUFSIZE = 1024
artnet_port = 6454
PIXELCOUNT = 40
np = None

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
#    broadcast_addr = "255.255.255.255" # we should bind to this
    broadcast_addr = "0.0.0.0" #the emfbadge doesn't behave here
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

def chunks(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]

def alloff():
    allcolour(( 0, 0, 0))

def allcolour(colour):
    for x in range(PIXELCOUNT):
        np[x] = colour
    np.write() 

def drawdata(data):
    alloff()

    pixels = list(chunks( data[:3*PIXELCOUNT], 3))
    for x in range(PIXELCOUNT):
        np[x] = (pixels[0])
    np.write()

def networkinit(): 
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('57North', 'thiswifiisnotforyou')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())  

if __name__ == "__main__":
    print("starting")

    np = neopixel.NeoPixel(machine.Pin(2), PIXELCOUNT)

    np[0] = (255, 0, 0)
    np.write()
    time.sleep(1)

    np[0] = ( 0, 255, 0)
    np.write()
    time.sleep(1)

    np[0] = ( 0, 0, 255)
    np.write()
    time.sleep(1)

    allcolour( ( 0, 0, 0))
    pktshow(drawdata)
