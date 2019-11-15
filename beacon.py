#!/usr/bin/env python
import os
import sys
sys.path.append(os.getcwd() + "/zigdiggity")

import time
import signal
import random
import argparse
import hexdump
from scapy.layers.dot15d4 import *
from scapy.layers.zigbee import *

from zigdiggity.radios.raspbee_radio import RaspbeeRadio
from zigdiggity.radios.observer_radio import ObserverRadio
import zigdiggity.observers.utils as observer_utils
from zigdiggity.packets.dot15d4 import beacon_request
from zigdiggity.interface.console import print_notify
from zigdiggity.misc.timer import Timer
from zigdiggity.interface.components.logo import Logo

parser = argparse.ArgumentParser(description='Send a beacon request')
parser.add_argument('-c','--channel',action='store',type=int,dest='channel',required=True,help='Channel to use')
parser.add_argument('-d','--device',action='store',dest='device',default='/dev/ttyS0',help='Zigbee Radio device')
parser.add_argument('-s','--stdout',action='store_true',dest='stdout',required=False,help='dump traffic to stdout')
parser.add_argument('-t','--timeout',action='store',type=int,dest='timeout',default=5,help='response listen timeout')
parser.add_argument('-v','--verbose',action='store_true',dest='verbose',required=False,help='verbose logging')
parser.add_argument('-w','--wireshark',action='store_true',dest='wireshark',required=False,help='See all traffic in wireshark')
args = parser.parse_args()

logo = Logo()
logo.print()

hardware_radio = RaspbeeRadio(args.device)
radio = ObserverRadio(hardware_radio)

if args.wireshark:
    observer_utils.register_wireshark(radio)
    if args.verbose:
        print_notify("Registered Wireshark Observer")
if args.stdout:
    observer_utils.register_stdout(radio)
    if args.verbose:
        print_notify("Registered Stdout Observer")

radio.set_channel(args.channel)
radio.receive()

if args.verbose:
    print_notify("Sending the beacon request to channel %d" % radio.get_channel())

try:
    timer = Timer(args.timeout)
    radio.send_and_retry(beacon_request(random.randint(0,255)))
    while not timer.has_expired():
        radio.receive()
finally:
   radio.off()
