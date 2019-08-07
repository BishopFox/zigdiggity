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

logo = Logo()
logo.print()

hardware_radio = RaspbeeRadio("/dev/ttyS0")
radio = ObserverRadio(hardware_radio)
observer_utils.register_wireshark(radio)

CHANNELS = [11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
for channel in CHANNELS:
    radio.set_channel(channel)

    print_notify("Listening to channel %d" % radio.get_channel())
    
    timer = Timer(10)
    while(not timer.has_expired()):
        result = radio.receive()
