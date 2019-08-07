import os
import sys
sys.path.append(os.getcwd() + "/zigdiggity")

import time
import argparse
from scapy.layers.dot15d4 import *
from scapy.layers.zigbee import *

from zigdiggity.radios.raspbee_radio import RaspbeeRadio
from zigdiggity.radios.observer_radio import ObserverRadio
from zigdiggity.observers.wireshark_observer import WiresharkObserver
from zigdiggity.interface.console import print_notify
import zigdiggity.crypto.utils as crypto_utils
from zigdiggity.misc.actions import *

parser = argparse.ArgumentParser(description='Attempt to find locks on a channel')
parser.add_argument('-c','--channel',action='store',type=int,dest='channel',required=True,help='Channel to use')
parser.add_argument('-w','--wireshark',action='store_true',dest='wireshark',required=False,help='See all traffic in wireshark')
args = parser.parse_args()

hardware_radio = RaspbeeRadio("/dev/ttyS0")
radio = ObserverRadio(hardware_radio)

if args.wireshark:
    wireshark = WiresharkObserver()
    radio.add_observer(wireshark)

radio.set_channel(args.channel)
print_notify("Current on channel %d" % args.channel)
find_locks(radio)

radio.off()
