import sys
from struct import *
import time

DELAY = 0.5
VERBOSE = "sensible" # on|off|sensible|silly
BUFSIZE = 1024
artnet_port = 6454


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

        for i in range(1,512):
            if full:
                data.append(0xFF)
            else:
                #data.append(random.randint(0, 255))
                data.append(0xF0)
        return gen_artnet_pkt(data)

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

def pktgen(displaycb):
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
        #if displaycb: doesn't work with an entire packet, hmmmmmm
            #displaycb(pkt)

        #sys.stdout.write(".")
        #sys.stdout.flush()
        time.sleep(DELAY)

def pktshow(displaycb):
    broadcast_addr = "255.255.255.255"
    print("          receiving from {} {}"
        .format(broadcast_addr, artnet_port))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    #bind might be required

    while True:
        pkt,addr = sock.recvfrom(BUFSIZE) #blocks

        if VERBOSE == "silly":
            print(hexdump(pkt))

        pkt = parse_artnet_pkt(pkt)
        displaycb(pkt)

        sys.stdout.write(".")
        sys.stdout.flush()
        #time.sleep(DELAY)

def guinonesense(displaycb):
    broadcast_addr = "255.255.255.255"
    print("          receiving from {} {}"
        .format(broadcast_addr, artnet_port))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    #bind might be required

    while True:
        pkt,addr = sock.recvfrom(BUFSIZE) #blocks

        if VERBOSE == "silly":
            print(hexdump(pkt))

        pkt = parse_artnet_pkt(pkt)
        displaycb(pkt)

        sys.stdout.write(".")
        sys.stdout.flush()
        #time.sleep(DELAY)


def hwdisplay():
    pyb.led(ledr, high)

def consoledisplay(pkt):
    print("something something packet")

if __name__ == "__main__":
    #guinonesense(hwdisplay)
    #pktshow(consoledisplay)
    pktgen(consoledisplay)
