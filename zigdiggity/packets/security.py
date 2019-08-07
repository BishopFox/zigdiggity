from scapy.layers.dot15d4 import *
from scapy.layers.zigbee import *

def security_header_stub(extended_source, frame_counter):

    stub = ZigbeeSecurityHeader()
    stub.key_type=1
    stub.fc=frame_counter
    stub.source=extended_source
    return stub
