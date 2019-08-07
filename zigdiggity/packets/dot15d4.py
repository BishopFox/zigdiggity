from zigdiggity.packets.utils import extended_address, address, pan, extended_pan
from scapy.layers.dot15d4 import *
from scapy.layers.zigbee import *

def is_beacon_response(frame):

    if frame is None:
        return False
    
    if Dot15d4Beacon in frame and ZigBeeBeacon in frame:
        return True
    
    return False

def is_beacon_request(frame):

    if frame is None:
        return False

    if Dot15d4Cmd in frame and frame[Dot15d4Cmd].cmd_id==7:
        return True

    return False

def is_data_request(frame):

    if frame is None:
        return False

    if Dot15d4Cmd in frame and frame[Dot15d4Cmd].cmd_id==4:
        return True

    return False

def dot15d4_cmd_stub(seq_num):

    dot15d4 = Dot15d4FCS()
    dot15d4.fcf_frametype=3
    dot15d4.fcf_destaddrmode=2
    dot15d4.fcf_srcaddrmode=2
    dot15d4.fcf_panidcompress=1
    dot15d4.fcf_ackreq=1
    dot15d4.seqnum=seq_num
    return dot15d4

def dot15d4_data_stub(seq_num, panid, source, destination):

    dot15d4 = Dot15d4FCS()
    dot15d4.fcf_frametype=1
    dot15d4.fcf_destaddrmode=2
    dot15d4.fcf_srcaddrmode=2
    dot15d4.fcf_panidcompress=1
    dot15d4.fcf_ackreq=1
    dot15d4.seqnum=seq_num

    dot15d4_data = Dot15d4Data()
    dot15d4_data.dest_panid=panid
    dot15d4_data.dest_addr=destination
    dot15d4_data.src_addr = source

    return dot15d4 / dot15d4_data

def data_request(source, destination, pan_id, seq_num=0):

    source = address(source)
    destination = address(destination)
    pan_id = pan(pan_id)

    dot15d4 = dot15d4_cmd_stub(seq_num)

    dot15d4_cmd = Dot15d4Cmd()
    dot15d4_cmd.cmd_id=4
    dot15d4_cmd.dest_addr=destination
    dot15d4_cmd.src_addr=source
    dot15d4_cmd.dest_panid=pan_id

    return dot15d4 / dot15d4_cmd

def beacon_request(seq_num=0):

    dot15d4 = Dot15d4FCS()
    dot15d4.fcf_frametype=3
    dot15d4.fcf_destaddrmode=2
    dot15d4.seqnum = seq_num

    dot15d4_cmd = Dot15d4Cmd()
    dot15d4_cmd.cmd_id=7
    dot15d4_cmd.dest_addr=0xffff

    return dot15d4 / dot15d4_cmd

def beacon_response(pan_id, source=0x0000, extended_panid=0x0102030405060708, seq_num=0):

    pan_id = pan(pan_id)
    source = address(source)
    extended_panid = extended_pan(extended_panid)

    dot15d4 = Dot15d4FCS()
    dot15d4.fcf_frametype=0
    dot15d4.fcf_srcaddrmode=2
    dot15d4.fcf_destaddrmode=0
    dot15d4.seqnum=seq_num

    dot15d4_beacon = Dot15d4Beacon()
    dot15d4_beacon.src_panid=pan_id
    dot15d4_beacon.src_addr=source
    dot15d4_beacon.sf_pancoord=1

    zigbee_beacon = ZigBeeBeacon()
    zigbee_beacon.nwkc_protocol_version=2
    zigbee_beacon.stack_profile=2
    zigbee_beacon.end_device_capacity=1
    zigbee_beacon.router_capacity=1
    zigbee_beacon.extended_pan_id=extended_panid
    zigbee_beacon.tx_offset=0xffffff

    return dot15d4 / dot15d4_beacon / zigbee_beacon
