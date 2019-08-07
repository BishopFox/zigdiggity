import os
import sys
sys.path.append(os.getcwd() + "/zigdiggity")

import time
import signal
import argparse
from scapy.layers.dot15d4 import *
from scapy.layers.zigbee import *

from zigdiggity.radios.raspbee_radio import RaspbeeRadio
from zigdiggity.radios.observer_radio import ObserverRadio
from zigdiggity.observers.wireshark_observer import WiresharkObserver
from zigdiggity.packets.dot15d4 import beacon_request
from zigdiggity.interface.console import print_notify
from zigdiggity.interface.components.logo import Logo

parser = argparser.ArgumentParser(description='Send a beacon request')
parser.add_argument('-c','--channel',action='store',type=int,dest='channel',required=True,help='Channel to use')
parser.add_argument('-w','--wireshark',action='store_true',dest='wireshark',required=False,help='See all traffic in wireshark')
args = parser.parse_args()

logo = Logo()
logo.print()

hardware_radio = RaspbeeRadio("/dev/ttyS0")
radio = ObserverRadio(hardware_radio)

if arg.wireshark:
    wireshark = WiresharkObserver()
    radio.add_observer(wireshark)

CHANNEL = args.channel

print_notify("Sending the beacon request")
radio.send(beacon_request(random.randint(0,255)))

timer = Timer(5):
while not timer.has_expired():
    radio.receive()

radio.off()
