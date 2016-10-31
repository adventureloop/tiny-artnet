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


import sys
import os
from struct import *
import time
import socket
import random

READ_DELAY = 0.000450
DELAY = 1000 * READ_DELAY
VERBOSE = "sensible" # on|off|sensible|silly
BUFSIZE = 1024
artnet_port = 6454
THRESHOLD = 30

breathe_position = 0.1
breathe_direction = 1
breathe_step = 0.05

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

def breathe_pkt():
    global breathe_position
    global breathe_direction

    breathe_position = breathe_position+(breathe_direction*breathe_step)
    if breathe_position > 1.0
        breathe_direction = -1.0
    if breathe_position < 0.1
        breathe_direction = 1.0
    
    colour = int(breathe_position*256)
    data = bytearray()

    for x in range(512):
        data.append(colour)
    return gen_artnet_pkt(data)

def alert_pkt():
    data = bytearray()

    for x in range(512):
        if x % 3: 
            data.append(256)
    return gen_artnet_pkt(data)

def sensemotion(pin):
    counter = 0

    for x in range(100):
        if pin.value():
            counter = counter+1
        sleep(READ_DELAY)

    if counter > THRESHOLD:
        return True
    return False


def pktgen(pin, addr="255.255.255.255"):
    print("       sending to: {} {} every {} seconds"
        .format(addr, artnet_port, DELAY))

    while True:
        pkt = None
        if sensmotion(pin): #blocks for DELAY time
            pkt = alert_pkt()
        else: 
            pkt = breathe_pkt()

        if VERBOSE == "silly":
            print(hexdump(pkt))

        sock.sendto(pkt, (addr, artnet_port))

def networkinit(): 
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('ssid', 'passphrase')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())  
    


if __name__ == "__main__":
    addr = "255.255.255.255"

    pin = machine.Pin(14, machine.Pin.IN, None)
    pktgen(addr)
