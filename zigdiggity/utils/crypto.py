import zigbee_transkey
from scapy.layers.zigbee import *
from scapy.layers.dot15d4 import *
from killerbee.scapy_extensions import *

DEFAULT_ZB_KEY = "ZigBeeAlliance09"

def extract_network_key(packet, extended_source):
    if ZigbeeSecurityHeader in packet:
        packet[ZigbeeSecurityHeader].source = extended_source
        key = zigbee_transkey.calc_transkey(DEFAULT_ZB_KEY)
        decrypted_payload = kbdecrypt(packet, key)
        if decrypted_payload.cmd_identifier == 0x05:
            if decrypted_payload.data[0] == '\x01':
                return decrypted_payload.data[1:17]
