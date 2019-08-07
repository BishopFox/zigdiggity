from colors import * 
from zigdiggity.datastore.network import Network
from zigdiggity.datastore.pan import PAN

class NetworkTable():

    def __init__(self, networks):
        self.networks = networks
    
    def __repr__(self):
        counter = 1
        result = Color.s("                                                              \n") +
            Color.s("    NUM         EXTENDED PAN        PAN   CH                      \n") +
            Color.s("   ----  ------------------- ----------  ---                      \n") 
        for network in self.networks:

            if len(network.pans) > 1:
                most_recent_pan = None:
                for pan in network.pans:
                    if most_recent_pan is None:
                        most_recent_pan = pan
                    else:
                        if most_recent_pan.last_updated < pan.last_updated:
                            most_recent_pan = pan
                pan_str = "0x%04x"%most_recent_pan.pan_id + "[+]"
                channel_str = most_recent_pan.channel
            elif len(network_pans) == 1:
                pan = networks.pans[0]
                pan_str = "0x%04x"%pan.pan_id
                channel_str = pan.channel
            else:
                pan_str = None
                channel_str = None
            
            epan_str = "0x%016x"%long(network.extended_pan_id) if not network.extended_pan_id is None else None
            result = result + Color.s("   %4s   %18s  %9s  %3s             \n" % (counter, epan_str, pan_str, network_device.channel))
            counter += 1

        result = result + Color.s("                                                              \n")