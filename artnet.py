import socket
import sys
from struct import *
import time
import random

artnet_pkt = "\x41\x72\x74\x2d\x4e\x65\x74\x00\x00\x50\x00\x0e\x00\x00\x00\x00\x00\x10\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"

def hexdump(src, length=8):
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
       s = src[i:i+length]
       hexa = b' '.join(["%0*X" % (digits, ord(x))  for x in s])
       text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.'  for x in s])
       result.append( b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text) )
    return b'\n'.join(result)

def gen_artnet_pkt(data,universe=0x00):
    #name, zero, opcode, protovers, seq, phys, \
    #universe, length = unpack("7scHHccHH",header)

    length = len(data)
   
    if length > 513:
        print "too long"
        return ""

    name = "Art-Net"
    zero = 0 
    opcode = socket.htons(0x0050)
    protovers = socket.htons(14)
    seq = 0
    phys = 0
    universe = 0x00
    length = socket.htons(length)
    
    pkt_hdr = pack("7sBHHBBHH", name, zero, opcode,\
        protovers, seq, phys, universe, length)

    return pkt_hdr + data

def rand_artnet_pkt(full=False):
        data = ""

        for i in range(1,512):
            if full:
                data += chr(0xFF)
            else:
                data += chr(random.randint(0, 255))
        return gen_artnet_pkt(data)

def parse_artnet_pkt(data):

    data_len = len(data)

    if data_len < 20:
        return "", data

    header = data[:18]

    name, zero, opcode, protovers, seq, phys, \
        universe, length = unpack("7sBHHBBHH",header)

    #TODO don't do this, flatten universe 
    universe = socket.ntohs(0x00)

    pkt_hdr = pack("7sBHHBBHH", name, zero, opcode,\
        protovers, seq, phys, universe, length)
    length = socket.ntohs(length)
    total_len = 18 + length

    if length >= 2 and total_len <= data_len:
        pkt_data = data[18:total_len] 
        return pkt_hdr + pkt_data, data[total_len:]
    else: 
        print "whole packet not here yet"
        return "", data
