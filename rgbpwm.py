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

DELAY = 5
VERBOSE = "sensible" # on|off|sensible|silly
BUFSIZE = 1024
artnet_port = 6454
leds = []

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

def alloff(colours):
    for c in colours:
        c.duty(0)

def drawdata(data):
    alloff(leds)
    leds[0].duty(data[0]*4)
    leds[1].duty(data[1]*4)
    leds[2].duty(data[2]*4)

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

print("starting")

p12 = machine.Pin(12, machine.Pin.OUT)
p13 = machine.Pin(13, machine.Pin.OUT)
p14 = machine.Pin(14, machine.Pin.OUT)

red = machine.PWM(p12)
green = machine.PWM(p14)
blue = machine.PWM(p13)

leds = [red, green, blue]

alloff(leds)

red.duty(500)
time.sleep(1)
alloff(leds) 

green.duty(500)
time.sleep(1)
alloff(leds) 

blue.duty(500)
time.sleep(1)
alloff(leds) 

red.duty(500)
green.duty(500)
blue.duty(500)
networkinit()
alloff(leds) 

pktshow(drawdata)
