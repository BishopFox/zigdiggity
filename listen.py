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

parser = argparse.ArgumentParser(description='Listen to a Zigbee traffic on a channel')
parser.add_argument('-c', '--channel', action='store',type=int, required=True,help='Channel to use')
args = parser.parse_args()

logo = Logo()
logo.print()

hardware_radio = RaspbeeRadio("/dev/ttyS0")
radio = ObserverRadio(hardware_radio)
observer_utils.register_wireshark(radio)

radio.set_channel(args.channel)

print_notify("Listening to channel %d" % radio.get_channel())

while(1):
    result = radio.receive()
