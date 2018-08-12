from devices import display_devices_from_list
from networks import display_device_networks_from_list
from scanning import scanning_interface
from zigdiggity.datastore.devices import Device
from colors import *

DEFAULT_SCAN_TIME = 5
ALL_CHANNELS = [11,15,20,25,12,13,14,16,17,18,19,21,22,23,24]

def ask_which_channels_to_scan():

    while True:
        raw_channel = Color.prompt("{?} Which channel(s) would you like to scan? ({G}11{W}-{G}26{W}, {G}all{W}) [default: {G}all{W}]:")
        if len(raw_channel) == 0 or "all" == raw_channel.lower():
            scan_channels = ALL_CHANNELS
            Color.pl("{.} Scanning {G}all {W}channels.")
        else:
            try:
                channel_number = int(raw_channel)
            except:
                channel_number = 0
                Color.pl("{!} Invalid input. Please provide the channel you'd like to scan.")
                continue
            if 11 <= channel_number <= 25:
                scan_channels = [channel_number]
        
        if len(scan_channels) > 0:
            return scan_channels

def ask_how_long_to_scan():

    raw_seconds = Color.prompt("{?} How long would you like to scan each channel for? [default: {G}5{W}]:")
    
    try:
        seconds = int(raw_seconds)
    except:
        seconds = DEFAULT_SCAN_TIME

    Color.pl("{.} Scanning each channel for %s seconds"%seconds)
    return seconds


def ask_which_target(listener, sender, datastore):
    
    device_list = datastore.query(Device).order_by(Device.channel).all()
    if len(device_list) == 0:
        Color.pl("{.} No devices found in database.")
        scan_channels = ask_which_channels_to_scan()
    else:
        Color.pl("{.} Devices found in the database.")
        raw_yes_no = Color.prompt("{?} Would you like to scan anyway? ({G}Y{W}/{G}N{W}) [default: {G}N{W}]:")
        if len(raw_yes_no)>0 and raw_yes_no.lower()[0] == "y":
            scan_channels = ask_which_channels_to_scan()
        else:
            scan_channels = []

    if len(scan_channels) > 0:
        seconds = ask_how_long_to_scan()
        scanning_interface(listener, sender, scan_channels, datastore, seconds)

    # display device list for 
    result = {}

    while True:
        raw_dev_net = Color.prompt("{?} Would you like to attack a device or network? [{G}D{W}evice/{G}N{W}etwork/{G}C{W}hannel] (default: {G}N{W}etwork):")
        if len(raw_dev_net) > 0 and raw_dev_net.lower()[0] == "d":
            device_list = datastore.query(Device).order_by(Device.channel).all()
            #Display the devices
            display_devices_from_list(device_list)
            raw_dev_target = Color.prompt("{?} Which device would you like to target? [1-%s]:"%len(device_list))
            try:
                device_number = int(raw_dev_target)
            except:
                device_number = 0
            if 1 <= device_number <= len(device_list):
                result['target_type'] = "device"
                result['device'] = device_list[device_number-1]
                break
        elif len(raw_dev_net) > 0 and raw_dev_net.lower()[0] == "c":
            raw_channel_target = Color.prompt("{?} Which channel would you like to target? [11-25]:")
            try:
                channel_number = int(raw_channel_target)
            except:
                channel_number = 0
            if 11 <= channel_number <= 25:
                result['target_type'] = "channel"
                result['channel'] = channel_number
                break
        else:
            network_list = datastore.query(Device).group_by(Device.pan_id).group_by(Device.extended_pan_id).order_by(Device.channel).all()
            #Display the networks
            display_device_networks_from_list(network_list)
            raw_net_target = Color.prompt("{?} Which network would you like to target? [1-%s]:"%len(network_list))
            try:
                network_number = int(raw_net_target)
            except:
                network_number = 0
            if 1 <= network_number <= len(network_list):
                result['target_type'] = "network"
                result['network'] = network_list[network_number-1]
                break

    return result
        
