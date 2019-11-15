#!/usr/bin/env python
import os
import sys
sys.path.append(os.getcwd() + "/zigdiggity")

import signal
import time
import argparse
from zigdiggity.radios.raspbee_radio import RaspbeeRadio
from zigdiggity.radios.observer_radio import ObserverRadio
import zigdiggity.observers.utils as observer_utils
from scapy.layers.dot15d4 import *
from scapy.layers.zigbee import *
from zigdiggity.interface.console import print_notify
from zigdiggity.interface.components.logo import Logo

def handle_interrupt(signal, frame):
    global interrupted
    print_notify("Exiting the current script")
    interrupted = True

parser = argparse.ArgumentParser(description='Listen to a Zigbee traffic on a channel')
parser.add_argument('-c', '--channel', action='store',type=int, required=True,help='Channel to use')
parser.add_argument('-d','--device',action='store',dest='device',default='/dev/ttyS0',help='Zigbee Radio device')
parser.add_argument('-s','--stdout',action='store_true',dest='stdout',required=False,help='dump traffic to stdout')
parser.add_argument('-w','--wireshark',action='store_true',dest='wireshark',required=False,help='See all traffic in wireshark')
args = parser.parse_args()

logo = Logo()
logo.print()

hardware_radio = RaspbeeRadio(args.device)
radio = ObserverRadio(hardware_radio)

if args.wireshark:
    observer_utils.register_wireshark(radio)
    print_notify("Registered Wireshark Observer")
if args.stdout:
    observer_utils.register_stdout(radio)
    print_notify("Registered Stdout Observer")

radio.set_channel(args.channel)

print_notify("Listening to channel %d" % radio.get_channel())

signal.signal(signal.SIGINT, handle_interrupt)
interrupted = False

while not interrupted:
    result = radio.receive()

radio.off()
