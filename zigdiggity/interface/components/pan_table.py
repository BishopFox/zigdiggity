from zigdiggity.datastore.network import Network
from colors import *

class DeviceTable():

    def __init__(self, devices):
        self.devices = devices
    
    def __repr__(self):
        
        counter = 1

        result = Color.s("                                                                     \n") +
            Color.s("    NUM         EXTENDED PAN     PAN   CH    ADDR        EXTENDED ADDR\n") +
            Color.s("   ----  -------------------  ------  ---  ------ --------------------\n")
        
        for device in devices:
            pan_str = "0x%04x"%device.pan.pan_id if device.pan is not None and device.pan.pan_id is not None else None
            channel_str = device.pan.channel if device.pan is not None and device.pan.channel is not None else None
            addr_str = "0x%04x"%device.address if device.address is not None else None
            extrended_address_str = "0x%016x"%long(device.extended_address) if device.extended_address is not None else None
            extended_pan_str = "0x%016x"%long(device.pan.) if device.pan is not None and device.pan.network is not None and device.pan.network.extended_pan_id is not None else None
            result = result + Color.s("   %4s  %19s  %6s  %3s  %6s  %19s\n" %(counter, extended_pan_str, pan_str, pan_str, address_str, extended_address_str)) 
            counter += 1
        result = result + Color.s("                                                                        \n")
        return result