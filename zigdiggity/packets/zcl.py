from zigdiggity.packets.utils import extended_address, address, pan, extended_pan, extended_address_bytes
from zigdiggity.packets.nwk import nwk_stub
from zigdiggity.packets.dot15d4 import dot15d4_data_stub
from zigdiggity.packets.security import security_header_stub
import zigdiggity.crypto.utils as crypto_utils
from scapy.layers.dot15d4 import *
from scapy.layers.zigbee import *

def encrypted_unlock(panid, source, destination, extended_source, key, frame_counter=0, seq_num=0, nwk_seq_num=0, aps_counter=0, zcl_seq_num=0):

    panid = pan(panid)
    source = address(source)
    destination = address(destination)
    extended_source = extended_address(extended_source)

    extended_source_bytes = extended_address_bytes(extended_source)

    aps_payload = ZigbeeAppDataPayload()
    aps_payload.aps_frametype=0
    aps_payload.deliver_mode=2
    aps_payload.frame_control=4
    aps_payload.cluster=0x0101
    aps_payload.profile=0x0104
    aps_payload.dst_endpoint=0xff # Broadcast
    aps_payload.src_endpoint=1
    aps_payload.counter=aps_counter

    zcl = ZigbeeClusterLibrary()
    zcl.zcl_frametype=1
    zcl.transaction_sequence=zcl_seq_num
    zcl.command_identifier=1

    payload = aps_payload / zcl

    dot15d4_data = dot15d4_data_stub(seq_num, panid, source, destination)
    nwk = nwk_stub(source, destination, nwk_seq_num)
    security_header = security_header_stub(extended_source, frame_counter)
    unencrypted_frame_part = dot15d4_data / nwk / security_header

    return crypto_utils.zigbee_packet_encrypt(key, unencrypted_frame_part, bytes(payload), extended_source_bytes)
