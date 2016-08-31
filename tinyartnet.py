import sys

PYVERSION = sys.implementation.name

if PYVERSION == "micropython": 
    import usocket as socket
    import utime
    import pyb
elif PYVERSION == "cpython":
    import socket 
    import time


from artnet import *

usage = """usage:
    tcpartnet_bridge.py pktgen
"""

startup_msg = """
        \033[34m__  _\033[39m                        \033[32m__             __ \033[39m
       \033[34m/ /_(_)___  __  __\033[39m\033[32m____ ______/ /_____  ___  / /_\033[39m
      \033[34m/ __/ / __ \/ / / \033[39m\033[32m/ __ `/ ___/ __/ __ \/ _ \/ __/\033[39m
     \033[34m/ /_/ / / / / /_/ \033[39m\033[32m/ /_/ / /  / /_/ / / /  __/ /_  \033[39m
     \033[34m\__/_/_/ /_/\__, /\033[39m\033[32m\__,_/_/   \__/_/ /_/\___/\__/  \033[39m
      \033[34m          /____/\033[39m
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

def pktgen():
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
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(DELAY)

def pktshow(output):
    broadcast_addr = "255.255.255.255"
    print("          receiving from {} {}"
        .format(broadcast_addr, artnet_port))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        pkt,addr = sock.recvfrom(BUFSIZE) #blocks

        if VERBOSE == "silly":
            print(hexdump(pkt))

        pkt = parse_artnet_pkt(pkt)
        output(pkt)

        sys.stdout.write(".")
        sys.stdout.flush()
        #time.sleep(DELAY)

def setuphardware():
    ledr = pyb.Pin("LED_RED",pyb.Pin.OUT)
    ledg = pyb.Pin("LED_GREEN",pyb.Pin.OUT)
    ledt = pyb.Pin("LED_TORCH",pyb.Pin.OUT)
    ledb = pyb.Pin("LED_BACKLIGHT",pyb.Pin.OUT)

def setupnetwork():
    nic = network.CC3100()
    nic.connect("ssid","password")

def hwdisplay():
    pyb.led(ledr, high)

def consoledisplay():
    print("CONSOLE!!!")

if __name__ == "__main__":

    mode = "pktgen" # pktgen|pktshow
    mode = "pktshow"
    mode = "pktgen"

    if VERBOSE == "sensible":
        print(startup_msg)
        print("                         {}".format(mode))

    outputcb = consoledisplay

    if PYVERSION == "cpython":
        if len(sys.argv) == 2:
            mode = sys.argv[1]
    if PYVERSION == "micropython":
        setuphardware()
        setupnetwork()
        outputcb = hwdisplay
    
    if mode == "pktgen":
        pktgen()
    if mode == "pktshow":
        pktshow(outputcb)
