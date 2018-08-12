from zigdiggity.datastore.devices import Device
from colors import *

UP_CHAR = '\x1B[1F'

def display_devices_from_list(device_list):

    counter = 1

    Color.pl("                                                                     ")
    Color.pl("    NUM         EXTENDED PAN     PAN   CH    ADDR        EXTENDED ADDR")
    Color.pl("   ----  -------------------  ------  ---  ------ --------------------")
    for device in device_list:
        extended_pan_hex = "0x%016x"%long(device.extended_pan_id) if not device.extended_pan_id is None else None
        pan_hex = "0x%04x"%device.pan_id if not device.pan_id is None else None
        address_hex = "0x%04x"%device.address if not device.address is None else None
        extended_address_hex = "0x%016x"%long(device.extended_address) if not device.extended_address is None else None
        Color.pl("   %4s  %19s  %6s  %3s  %6s  %19s" %(counter, extended_pan_hex, pan_hex, device.channel, address_hex, extended_address_hex)) 
        counter += 1
    Color.pl("                                                                        ")
    return counter

def display_devices(database_session):
    device_list = database_session.query(Device).order_by(Device.channel.asc()).all()
    return display_devices_from_list(device_list)

def display_devices_overwritable(database_session, previous_lines):

    if previous_lines > 0:
        Color.pl(UP_CHAR * (previous_lines + 4))
    return display_devices(database_session)
