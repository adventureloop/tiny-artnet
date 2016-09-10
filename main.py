### Author: tj <tj@enoti.me>
### Description: Scottish Consulate Techno Disco
### Category: Other
### License: BSD 3

import sys
import os
from struct import *
import time
import socket
import ugfx
import buttons

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
    return gen_artnet_pkt(os.urandom(512))

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

def pktgen(displaycb):
    broadcast_addr = "255.255.255.255"
    print("       sending to: {} {} every {} seconds"
        .format(broadcast_addr, artnet_port, DELAY))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  #required on a unix system

    while True:
        pkt = rand_artnet_pkt()

        sock.sendto(pkt, (broadcast_addr, artnet_port))
        #if displaycb: doesn't work with an entire packet, hmmmmmm
            #displaycb(pkt)

        #sys.stdout.write(".")
        #sys.stdout.flush()
        time.sleep(DELAY)

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
    width = 10
    selx = selected[0]*width
    sely = selected[1]*width

    data = list(data)
    if(len(data) < 512):
        data.extend([0] * (512 - len(data))) #pad out to 512 bytes

    for x in range(0, 32):
        for y in range(0, 16):
            val = data[x*16+y]
            if x == 0:
                print(val)
            colour = ugfx.html_color(int("0x{:02X}{:02X}{:02X}".format(val,val,val)))

            container.area(x*width, y*width, width, width, colour)
            container.box(x*width, y*width, width, width, ugfx.ORANGE)

            container.box(selx, sely, width, width, ugfx.WHITE)
            container.show()

    container.show()
    processbuttons()

def processbuttons():
    if buttons.is_pressed("JOY_RIGHT"):
        selected[0] = selected[0] + 1
    elif buttons.is_pressed("JOY_LEFT"):
        selected[0] = selected[0] - 1
    elif buttons.is_pressed("JOY_DOWN"):
        selected[1] = selected[0] + 1
    elif buttons.is_pressed("JOY_UP"):
        selected[1] = selected[0] - 1

    if selected[0] > 320:
        selected[0] = 320
    if selected[0] < 0:
        selected[0] = 0

    if selected[1] > 160:
        selected[1] = 160
    if selected[1] < 0:
        selected[1] = 0
        
    if buttons.is_pressed("BTN_A"):
            index = selected[0]*selected[1]+selected[1]
            val = data[index] + 10
            if val > 255:
                val = 255
            data[index] = val
    if buttons.is_pressed("BTN_B"):
            index = selected[0]*selected[1]+selected[1]
            val = data[index] - 10
            if val < 0:
                val = 0
            data[index] = val 

#if __name__ == "__main__":
print("starting")

ugfx.init()
ugfx.clear()
ugfx.set_default_font(ugfx.FONT_SMALL)
container = ugfx.Container(0, 80,320,160)

pktshow(drawdata)
