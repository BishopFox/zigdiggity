#!/usr/bin/env python
import os
import sys
sys.path.append(os.getcwd() + "/zigdiggity")

import time
import argparse
from zigdiggity.radios.raspbee_radio import RaspbeeRadio
from zigdiggity.radios.observer_radio import ObserverRadio
import zigdiggity.observers.utils as observer_utils
from scapy.layers.dot15d4 import *
from scapy.layers.zigbee import *
from zigdiggity.interface.console import print_notify
from zigdiggity.interface.components.logo import Logo
from zigdiggity.misc.timer import Timer

parser = argparse.ArgumentParser(description='Scan channels for Zigbee traffic')
parser.add_argument('-d','--device',action='store',dest='device',default='/dev/ttyS0',help='Zigbee Radio device')
parser.add_argument('-s','--stdout',action='store_true',dest='stdout',required=False,help='dump traffic to stdout')
parser.add_argument('-t','--timeout',action='store',type=int,dest='timeout',default=10,help='response listen timeout')
parser.add_argument('-w','--wireshark',action='store_true',dest='wireshark',required=False,help='See all traffic in wireshark')
args = parser.parse_args()

logo = Logo()
logo.print()

hardware_radio = RaspbeeRadio(args.device)
radio = ObserverRadio(hardware_radio)

if args.wireshark:
    observer_utils.register_wireshark(radio)
if args.stdout:
    observer_utils.register_stdout(radio)

CHANNELS = [11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]
for channel in CHANNELS:
    radio.set_channel(channel)

    print_notify("Listening to channel %d" % radio.get_channel())

    timer = Timer(args.timeout)
    while(not timer.has_expired()):
        result = radio.receive()

radio.off()
