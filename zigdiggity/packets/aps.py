from scapy.layers.dot15d4 import *
from scapy.layers.zigbee import *

def is_transport_key(frame):
    
    if frame is None:
        return False
    
    if ZigbeeAppDataPayload in frame and ZigbeeSecurityHeader in frame:
        if frame[ZigbeeAppDataPayload].aps_frametype == 1 and frame[ZigbeeSecurityHeader].key_type == 2:
            return True
        
    return False