import socket
import sys
from struct import *
import time
import random

usage = """usage:
    tcpartnet_bridge.py [server|client] artnet_addr artnet_port bridge_addr bridge_port"""

"It is \033[31mnot\033[39m intelligent to use \033[32mhardcoded ANSI\033[39m codes!"

startup_msg = """
     \033[31m___    ____  _______   ______________\033[39m   __    __       \033[32m________________\033[39m
    \033[31m/   |  / __ \/_  __/ | / / ____/_  __/\033[39m  / /    \ \     \033[32m/_  __/ ____/ __ \\\033[39m
   \033[31m/ /| | / /_/ / / / /  |/ / __/   / /\033[39m    / / _____\ \     \033[32m/ / / /   / /_/ /\033[39m
  \033[31m/ ___ |/ _, _/ / / / /|  / /___  / /\033[39m     \ \/_____/ /    \033[32m/ / / /___/ ____/\033[39m
 \033[31m/_/  |_/_/ |_| /_/ /_/ |_/_____/ /_/\033[39m       \_\    /_/    \033[32m/_/  \____/_/\033[39m
                                                                              
                        \033[34m____  ____  ________  ____________\033[39m
                       \033[34m/ __ )/ __ \/  _/ __ \/ ____/ ____/\033[39m
                      \033[34m/ __  / /_/ // // / / / / __/ __/\033[39m   
                     \033[34m/ /_/ / _, _// // /_/ / /_/ / /___\033[39m  
                    \033[34m/_____/_/ |_/___/_____/\____/_____/\033[39m
                                                           """
artnet_pkt = "\x41\x72\x74\x2d\x4e\x65\x74\x00\x00\x50\x00\x0e\x00\x00\x00\x00\x00\x10\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"

DELAY = 0.5
#FULL = True|False
FULL = False

def hexdump(src, length=8):
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
       s = src[i:i+length]
       hexa = b' '.join(["%0*X" % (digits, ord(x))  for x in s])
       text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.'  for x in s])
       result.append( b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text) )
    return b'\n'.join(result)

def server(artnet_addr,artnet_port,bridge_addr,bridge_port,):
    bridge_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bridge_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    bridge_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    artnet_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    artnet_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
    artnet_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 

    bridge_sock.bind((bridge_addr, bridge_port))
    bridge_sock.listen(1)

    conn, addr = bridge_sock.accept()
    print 'connect from:', addr, bridge_port

    ldata = ""

    while True:
        data = conn.recv(1024)
        if not data: 
            break

        ldata += (data)
        pkt, ldata = parse_artnet_pkt(ldata)
        
        if pkt:
            sys.stdout.write(".")
            sys.stdout.flush()
            artnet_sock.sendto(pkt, (artnet_addr, artnet_port))
    #        print hexdump(pkt)
            #artnet_sock.sendto(rand_artnet_pkt(), (artnet_addr, artnet_port))
        else:
            sys.stdout.write("|")
            sys.stdout.flush()

def client(artnet_addr,artnet_port,bridge_addr,bridge_port,):
    bridge_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bridge_sock.connect((bridge_addr, bridge_port))

    print "connected to", bridge_addr, bridge_port

    #listen for broadcast 
    artnet_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    artnet_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
    artnet_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 

    artnet_sock.bind((artnet_addr, artnet_port))

    while True:
        data, addr = artnet_sock.recvfrom(1024) # buffer size is 1024 bytes
        bridge_sock.send(data)
        #bridge_sock.send(rand_artnet_pkt())
        sys.stdout.write(".")
        sys.stdout.flush()
        #sendall(bridge_sock, data)

def pktgen(artnet_addr,artnet_port):
    print "sending to: ", artnet_addr, artnet_port, " every ", DELAY, " seconds"


    artnet_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    artnet_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
    artnet_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 

    #artnet_sock.bind((artnet_addr, artnet_port))
    #print(hexdump(pkt))

    broadcast_addr = "255.255.255.255"

    while True:
        pkt = rand_artnet_pkt()

        artnet_sock.sendto(pkt, (broadcast_addr, artnet_port))
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(DELAY)

def sendall(sock,msg):
    totalsent = 0
    while totalsent < len(msg):
        sent = sock.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent

#offset (bytes)  0   1   2   3
#0   'A'     'r'     't'     '-'
#4   'N'     'e'     't'     0
#8   Opcode ArtDMX (0x5000)  Protocol Version (14)
#12  Sequence    Physical    Universe
#16  Length (2 to 512, even)     Data    Data
#20   
#Data ...
#print(unpack("7sBHHBBHH","\x41\x72\x74\x2d\x4e\x65\x74\x00"))
#
#name = "Art-Net0"  7s # 8 bytes \x41\x72\x74\x2d\x4e\x65\x74
#zero                B # 1 byte  \x00
#opcode = 0x5000     H# 2 bytes \x50\x00
#protovers = 14      H# 2 bytes \x00\x14
#seq = 0             B# 1 byte  \x00
#phys = 0            B# 1 bytes \x00
#universe = 0        H# 2 bytes \x00\x00
#length = len(data)  H# 2 bytes \x00\x02
#data = data         # 2-512   \xff\xff

def gen_artnet_pkt(data):
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

def rand_artnet_pkt():
        data = ""

        for i in range(1,512):
            if FULL:
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

if __name__ == "__main__":

    if len(sys.argv) != 5:
        print(usage)
        sys.exit()

    print(startup_msg)

    mode = sys.argv[1]
    artnet_addr = sys.argv[2]
    artnet_port = 6454
    bridge_addr = sys.argv[3]
    bridge_port = int(sys.argv[4])

    print "                                 ", mode

    if mode == "server":
        server(artnet_addr, artnet_port, bridge_addr, bridge_port)
    elif mode == "client":
        client(artnet_addr, artnet_port, bridge_addr, bridge_port)
    elif mode == "pktgen":
        pktgen(artnet_addr, artnet_port)

