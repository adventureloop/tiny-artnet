import socket
import sys
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
VERBOSE = "sensible"

def hexdump(src, length=8):
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
       s = src[i:i+length]
       hexa = b' '.join(["%0*X" % (digits, ord(x))  for x in s])
       text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.'  for x in s])
       result.append( b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text) )
    return b'\n'.join(result)

def pktgen(artnet_port):
    broadcast_addr = "255.255.255.255"
    #print "sending to: ", broadcast_addr, artnet_port, " every ", DELAY, " seconds"
    print("sending to: {} {} every {} seconds".format(broadcast_addr, artnet_port, DELAY))

    artnet_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    artnet_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
    artnet_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 


    while True:
        pkt = rand_artnet_pkt()

        if VERBOSE == "silly":
            print(hexdump(pkt))

        artnet_sock.sendto(pkt, (broadcast_addr, artnet_port))
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(DELAY)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(usage)
        sys.exit()

    print(startup_msg)

    mode = sys.argv[1]
    artnet_port = 6454

    print("                                 {}".format(mode))

    if mode == "pktgen":
        pktgen(artnet_port)

