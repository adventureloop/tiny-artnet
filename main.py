import sys

from artnet import *

usage = """usage:
    tcpartnet_bridge.py pktgen
"""

DELAY = 0.5
VERBOSE = "sensible" # on|off|sensible|silly
BUFSIZE = 1024
artnet_port = 6454

def hexdump(src, length=8):
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
       s = src[i:i+length]
       hexa = b' '.join(["%0*X" % (digits, ord(x))  for x in s])
       text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.'  for x in s])
       result.append( b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text) )
    return b'\n'.join(result)

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

def consoledisplay():
    print("CONSOLE!!!")

if __name__ == "__main__":
    guinonesense(hwdisplay)
