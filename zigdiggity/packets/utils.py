import struct
from scapy.layers.dot15d4 import *
from scapy.layers.zigbee import *

def address(addr):
    if isinstance(addr, bytes):
        return struct.unpack('>H', addr)
    return addr

def extended_address(ext_addr):
    if isinstance(ext_addr, bytes):
        return struct.unpack('>Q', ext_addr)
    return ext_addr

def pan(panid):
    if isinstance(panid, bytes):
        return struct.unpack('>H', panid)[0]
    return panid

def extended_pan(ext_panid):
    if isinstance(ext_panid, bytes):
        return struct.unpack('>Q', ext_panid)[0]
    return ext_panid

def extended_address_bytes(ext_addr):
    if isinstance(ext_addr, bytes):
        return ext_addr
    return struct.pack('>Q', ext_addr)

def is_src_panid_present(packet):
    if packet is None:
        return None
    
    if Dot15d4FCS in packet:
        return packet.fcf_srcaddrmode != 0 and packet.fcf_panidcompress == 0
    else:
        return False

def get_extended_source(frame):
    if frame is None:
        return None

    if ZigbeeNWK in frame:
        if frame[ZigbeeNWK].flags & 16: # Extended source
            return frame[ZigbeeNWK].ext_src
    if ZigbeeSecurityHeader in frame:
        return frame[ZigbeeSecurityHeader].source
    return None

def get_source(frame):
    if frame is None:
        return None

    if Dot15d4FCS in frame:
        if frame[Dot15d4FCS].fcf_srcaddrmode == 2: # Short
            if Dot15d4Data in frame:
                return frame[Dot15d4Data].src_addr
            elif Dot15d4Cmd in frame:
                return frame[Dot15d4Cmd].src_addr
            elif Dot15d4Beacon in frame:
                return frame[Dot15d4Beacon].src_addr
    return None

def get_destination(packet):
    if packet is None:
        return None

    if Dot15d4FCS in packet:
        if packet[Dot15d4FCS].fcf_destaddrmode == 2: # Short
            if Dot15d4Data in packet:
                return packet[Dot15d4Data].dest_addr
            elif Dot15d4Cmd in packet:
                return packet[Dot15d4Cmd].dest_addr
    return None

def get_extended_destination(packet):
    if packet is None:
        return None

    if ZigbeeNWK in packet:
        if packet[ZigbeeNWK].flags & 8: # Extended dest
            return packet[ZigbeeNWK].ext_dst
    return None

def get_pan_id(packet):
    if packet is None:
        return None
    
    if Dot15d4FCS in packet:
        if Dot15d4Data in packet:
            if is_src_panid_present(packet):
                return packet[Dot15d4Data].src_panid
            else:
                return packet[Dot15d4Data].dest_panid
        elif Dot15d4Cmd in packet:
            if is_src_panid_present(packet):
                return packet[Dot15d4Cmd].src_panid
            else:
                return packet[Dot15d4Cmd].dest_panid
        elif Dot15d4Beacon in packet:
            return packet[Dot15d4Beacon].src_panid
    return None

def get_extended_pan_id(packet):
    if packet is None:
        return None
    
    if ZigBeeBeacon in packet:
        return packet[ZigBeeBeacon].extended_pan_id
    return None

def get_is_coordinator(packet):
    if packet is None:
        return None
    if Dot15d4Beacon in packet:
        return packet[Dot15d4Beacon].sf_pancoord
    return None

def get_sequence_number(packet):
    if packet is None:
        return None
    
    if Dot15d4FCS in packet:
        return packet[Dot15d4FCS].seqnum
    return None

def get_nwk_sequence(packet):
    if packet is None:
        return None
    
    if ZigbeeNWK in packet:
        return packet[ZigbeeNWK].seqnum
    return None

def get_frame_counter(packet):
    if packet is None:
        return None
    
    if ZigbeeSecurityHeader in packet:
        return packet[ZigbeeSecurityHeader].fc
    return None

def get_aps_counter(packet):
    if packet is None:
        return None
    
    if ZigbeeAppDataPayload in packet:
        return packet[ZigbeeAppDataPayload].counter
    return None

def get_zcl_sequence(packet):
    if packet is None:
        return None
    
    if ZigbeeClusterLibrary in packet:
        return packet[ZigbeeClusterLibrary].transaction_sequence
    return None

