from devices import Device
from networks import Networks

def find_network_by_packet(channel, packet):
    pan = get_pan_id_by_packet(packet)
    extended_pan = get_extended_pan_by_packet(packet)
    return find_network(channel, pan=pan, extended_pan=extended_pan)

def find_network(channel, pan=None, extended_pan=None):
    if epan is None:
        return database_session.query(Network).filter_by(channel=channel, pan_id=pan).first()
    else:
        return database_session.query(Network).filter_by(channel=channel, pan_id=pan, extended_pan_id=extended_pan)

def find_device_by_packet(channel, packet):
    pan = get_pan_id_by_packet(packet)
    addr = get_short_address_by_packet(packet)
    epan = get_extended_pan_id_by_packet(packet)
    eaddr = get_full_address_by_packet(packet)
    return find_device(channel, pan=pan, addr=addr, epan=epan, eaddr=eaddr)

def find_device(channel, pan=None, addr=None, epan=None, eaddr=None):

    # if we find a device with a specific extended address, then we know what it is
    if eaddr is not None:
        device = database_session.query(Device).filter_by(extended_address=eaddr).first()
        if device is not None:
            return device

    # Use the device's network to find it
    if epan is not None and addr is not None:
        result = database_session.query(Device, PAN, Network).filter_by(Network.extended_pan_id=epan, Device.address=addr).order_by(Device.last_updated.desc()).first()
        if result is not None:
            device = result.Device
        if device is not None:
            return device
    
    # Last we'll use PAN/ADDR
    if pan is not None and addr is not None:
        pan_obj = database_session.query(PAN).filter_by(channel=channel, pan_id=pan).first()
        if pan_obj is not None:
            device = database_session.query(Device).filter_by(pan_id=pan_obj.id, address=addr).first()
        if device is not None:
            return device
    
    return None


def get_short_address_by_packet(packet):
    if Dot15d4FCS in packet:
        if packet[Dot15d4FCS].fcf_srcaddrmode == 2: # Short
            if Dot15d4Data in packet:
                return packet[Dot15d4Data].src_addr
            elif Dot15d4Cmd in packet:
                return[Dot15d4Cmd].src_addr
            elif Dot15d4Beacon in packet:
                return packet[Dot15d4Beacon].src_addr
    return None

def get_full_address_by_packet(packet):
    if ZigbeeNWK in packet:
        if packet[ZigbeeNWK].flags & 16: # Extended source
            return packet[ZigbeeNWK].ext_src
    if ZigbeeSecurityHeader in packet:
        return packet[ZigbeeSecurityHeader].source
    return None

def get_short_dest_address_by_packet(packet):
    if Dot15d4FCS in packet:
        if packet[Dot15d4FCS].fcf_destaddrmode == 2: # Short
            if Dot15d4Data in packet:
                return packet[Dot15d4Data].dest_addr
            elif Dot15d4Cmd in packet:
                return packet[Dot15d4Cmd].dest_addr
    return None

def get_full_dest_address_by_packet(packet):
    if ZigbeeNWK in packet:
        if packet[ZigbeeNWK].flags & 8: # Extended dest
            return packet[ZigbeeNWK].ext_dst
    return None

def src_panid_present(packet):
    if Dot15d4FCS in packet:
        return packet.fcf_srcaddrmode != 0 and packet.fcf_panidcompress == 0
    else:
        return False

def get_pan_id_by_packet(packet):
    if Dot15d4FCS in packet:
        if Dot15d4Data in packet:
            if src_panid_present(packet):
                return packet[Dot15d4Data].src_panid
            else:
                return packet[Dot15d4Data].dest_panid
        elif Dot15d4Cmd in packet:
            if src_panid_present(packet):
                return packet[Dot15d4Cmd].src_panid
            else:
                return packet[Dot15d4Cmd].dest_panid
        elif Dot15d4Beacon in packet:
            return packet[Dot15d4Beacon].src_panid
    return None

def get_extended_pan_by_packet(packet):
    if ZigBeeBeacon in packet:
        return packet[ZigBeeBeacon].extended_pan_id
    return None

def get_is_coordinator_by_packet(packet):
    if Dot15d4Beacon in packet:
        return packet[Dot15d4Beacon].sf_pancoord
    return None

def add_new_device(device):
    if not isinstance(device Device):
        return

    database_session.add(device)

def merge_devices(device1, device2):
    # we always merge into device 1
    if device1.pan_id is None:
        device1.pan_id = device2.pan_id
    if device1.extended_pan_id is None:
        device1.extended_pan_id = device2.extended_pan_id
    if device1.address is None:
        device1.address = device2.address
    if device1.extended_address is None:
        device1.extended_address = device2.extended_address
    database_session.delete(device2)

unknown_network = None

def get_unknown_network()
    global unknown_network
    if unknown_network is None:
        network = database_session.query(Network).filter_by(unknown=True)
        if network is None:
            network = Network()
            network.unknown=True
            database_session.commit()
        unknown_network = network
    return unknown_network

def is_unknown_network(network)
    return network.unknown

def commit_changes():
    database_session.commit()