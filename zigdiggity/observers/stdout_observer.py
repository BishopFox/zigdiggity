import os
import subprocess
import hexdump

from zigdiggity.observers.observer import Observer
from scapy.layers.dot15d4 import *
from scapy.layers.zigbee import *

DOT154_FCF_TYPE_MASK            = 0x0007  #: Frame type mask

PACKET_TYPES = {
    "0": "Beacon",     #: Beacon frame
    "1": "Data",       #: Data frame
    "2": "Ack",        #: Acknowledgement frame
    "3": "Mac Cmd"     #: MAC Command frame
}

class StdoutObserver(Observer):

    def __init__(self):
        pass

    def notify(self, channel, packet):
        if packet == None:
            return

        fcf = struct.unpack("<H",bytes(packet)[0:2])[0] & DOT154_FCF_TYPE_MASK
        if (str(fcf) in PACKET_TYPES):
            print("Type:", PACKET_TYPES[str(fcf)])
        else:
            print("Type: Unknown")

        hexdump.hexdump(bytes(packet))
        return

    def close(self):
        pass
