### Author: tj <tj@enoti.me>
### Description: Scottish Consulate Techno Disco Controller
### Category: Other
### License: BSD 3

import sys
import os
from struct import *
import time
import socket
import ugfx
import buttons
import wifi
import gc

DELAY = 0.5
BUFSIZE = 600
artnet_port = 6454

container = None
textcontainer = None
selected = [0,0]
transmitter = True
universe = 0
selectuniverse = False

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

    return pkt_hdr + bytes(data)

def rand_artnet_pkt(full=False):
    return gen_artnet_pkt(os.urandom(512))

def parse_artnet_pkt(data, pktuniverse=0x0):
    data_len = len(data)

    if data_len < 20:
        return "", data

    header = data[:18]

    name, zero, opcode, protovers, seq, phys, \
        universe, length = unpack("!7sBHHBBHH",header)
    #print("name: {}, zero: {}, opcode: {}, protovers: {}, seq: {}, phys: {}, universe: {}, length: {}".format( name, zero, opcode, protovers, seq, phys, universe, length))

    if pktuniverse != universe:
        print("pktuniverse {} != filter universe {}".format(pktuniverse, universe))
        return pkt_hdr, []

    pkt_hdr = pack("!7sBHHBBHH", name, zero, opcode,\
        protovers, seq, phys, universe, length)
    artnet_pkt_len = 18 + length

    #print("length {} total_len {} data_len {}".format(length, artnet_pkt_len, data_len))
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

    pktdata = []

    start = time.ticks_ms()
    while True:
        #pktdata = os.urandom(512)
        if time.ticks_diff(start, time.ticks_ms()) > 500:
            sock.sendto(gen_artnet_pkt(pktdata, universe), (broadcast_addr, artnet_port))
            start = time.ticks_ms()

        if displaycb: 
            pktdata = displaycb(pktdata)
        #time.sleep(DELAY)
        if not transmitter:
            print("no more transmitting")
            return

def pktshow(displaycb):
    broadcast_addr = "0.0.0.0" #these boards aren't happy with the broadcast addr
    print("          receiving from {} {}"
        .format(broadcast_addr, artnet_port))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    sock.bind((broadcast_addr,artnet_port))

    while True:
        pkt,addr = sock.recvfrom(BUFSIZE) #blocks

        pkt_hdr, pkt_data = parse_artnet_pkt(pkt, universe)
        displaycb(pkt_data)
        if transmitter:
            print("no more receiving")
            return

def drawdata(data):
    width = 10
    selx = selected[0]*width
    sely = selected[1]*width

    data = list(data)
    if(len(data) < 512):
        data.extend([0] * (512 - len(data))) #pad out to 512 bytes

    for y in range(0, 16):
        for x in range(0, 32):
            val = data[y*32+x] 
            colour = ugfx.html_color(int("0x{:02X}{:02X}{:02X}".format(val,val,val)))

            container.area(x*width, y*width, width, width, colour)
            container.box(x*width, y*width, width, width, ugfx.ORANGE)

            container.box(selx, sely, width, width, ugfx.WHITE)
            container.show()

    container.show()
    return processbuttons(data)

def processbuttons(data):
    global transmitter
    global selected
    global selectuniverse
    global universe

    if buttons.is_pressed("JOY_RIGHT"):
        selected[0] = selected[0] + 1
    elif buttons.is_pressed("JOY_LEFT"):
        selected[0] = selected[0] - 1
    elif buttons.is_pressed("JOY_DOWN"):
        selected[1] = selected[1] + 1
    elif buttons.is_pressed("JOY_UP"):
        selected[1] = selected[1] - 1

    if selected[0] > 320:
        selected[0] = 320
    if selected[0] < 0:
        selected[0] = 0

    if selected[1] > 160:
        selected[1] = 160
    if selected[1] < 0:
        selected[1] = 0

    if buttons.is_pressed("JOY_CENTER"):
        if selectuniverse:
            selectuniverse = False
        else:
            selectuniverse = True
        drawtext(textcontainer) #only draw when something changes

    inc = 30
    if buttons.is_pressed("BTN_A"):
        if selectuniverse:
            universe = universe + 1
            if universe > 65535:
                universe = 0
            drawtext(textcontainer) #only draw when something changes
        else:
            index = selected[1]*32+selected[0]
            
            val = data[index] + inc
            if val > 255:
                val = 255
            data[index] = val
    if buttons.is_pressed("BTN_B"):
        if selectuniverse:
            universe = universe - 1
            if universe < 0:
                universe = 65535
            drawtext(textcontainer) #only draw when something changes
        else:
            index = selected[1]*32+selected[0]
            val = data[index] - inc
            if val < 0:
                val = 0
            data[index] = val 

    if buttons.is_pressed("BTN_MENU"):
        if transmitter:
            transmitter = False
        else:
            transmitter = True
    return data

def tinyartnet():
    while True:
        if transmitter:
            pktgen(drawdata)
        else:
            pktshow(drawdata)

        print("{} bytes free".format(gc.mem_free()))
#        gc.collect()
#        print("{} bytes free".format(gc.mem_free()))

def drawtext(con):
    con.clear()
    con.set_default_font(ugfx.FONT_NAME)
    con.text(0, 5, "TINY-ARTNET", ugfx.GREEN)
    con.set_default_font(ugfx.FONT_TITLE)
    con.text(2, 50, "UNIVERSE 01", ugfx.YELLOW)

    if selectuniverse:
        con.box(0, 50, 320, 50)
    con.set_default_font(ugfx.FONT_SMALL)
    con.show()
    

print("starting")

buttons.init()
ugfx.init()
ugfx.clear(ugfx.BLACK)

"""
ugfx.set_default_font(ugfx.FONT_NAME)
ugfx.text(0, 5, "TINY-ARTNET", ugfx.GREEN)
ugfx.set_default_font(ugfx.FONT_TITLE)
ugfx.text(2, 50, "UNIVERSE 01", ugfx.YELLOW)
ugfx.set_default_font(ugfx.FONT_SMALL)
"""

textcontainer = ugfx.Container(0, 0, 320, 80)
container = ugfx.Container(0, 80,320,160)

drawtext(textcontainer)
wifi.connect()

tinyartnet()
