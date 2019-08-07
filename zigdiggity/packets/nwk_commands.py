from zigdiggity.packets.utils import extended_address, address, pan
from zigdiggity.packets.dot15d4 import dot15d4_data_stub
from scapy.layers.dot15d4 import *
from scapy.layers.zigbee import *

def is_rejoin_response(frame):

    if frame is None:
        return False
    
    if ZigbeeNWKCommandPayload in frame and frame[ZigbeeNWKCommandPayload].cmd_identifier == 7:
        return True
    
    return False

def insecure_rejoin(source, destination, pan_id, extended_source, seq_num=0, nwk_seq_num=0):

    extended_source = extended_address(extended_source)
    source = address(source)
    destination = address(destination)
    pan_id = pan(pan_id)
    
    dot15d4_data = dot15d4_data_stub(seq_num, pan_id, source, destination)

    nwk = ZigbeeNWK()
    nwk.frametype=1
    nwk.proto_version=2
    nwk.flags=['extended_src']
    nwk.ext_src=extended_source
    nwk.source=source
    nwk.radius=30
    nwk.seqnum=nwk_seq_num

    nwk_command = ZigbeeNWKCommandPayload()
    nwk_command.cmd_identifier=6
    nwk_command.allocate_address=1

    return dot15d4_data / nwk / nwk_command
