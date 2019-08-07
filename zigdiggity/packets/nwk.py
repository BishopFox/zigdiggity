from scapy.layers.dot15d4 import *
from scapy.layers.zigbee import *

def nwk_stub(source, destination, seqnum, extended_source=None):

    stub = ZigbeeNWK()
    stub.frametype=0
    stub.discover_route=1
    stub.proto_version=2
    stub.flags=2
    stub.destination=destination
    stub.source=source
    stub.radius=30
    stub.seqnum=seqnum
    if extended_source is not None:
        stub.extended_source=extended_source
    return stub
