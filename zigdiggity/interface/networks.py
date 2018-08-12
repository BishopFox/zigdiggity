from colors import * 
from zigdiggity.datastore.devices import Device

def display_device_networks_from_list(network_device_list):

    counter = 1


    Color.pl("                                                              ")
    Color.pl("    NUM         EXTENDED PAN     PAN   CH                      ")
    Color.pl("   ----  ------------------- -------  ---                      ")
    for network_device in network_device_list:
        str_pan = "0x%04x"%network_device.pan_id if not network_device.pan_id is None else None
        str_epan = "0x%016x"%long(network_device.extended_pan_id) if not network_device.extended_pan_id is None else None
        Color.pl("   %4s   %18s  %6s  %3s             " % (counter, str_epan, str_pan, network_device.channel))
        counter += 1
    Color.pl("                                                              ")

        
