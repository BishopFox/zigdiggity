import packets
import time
import threading
from threading import Event
from zigdiggity.datastore.devices import Device
import signal
import datetime

DEFAULT_SCAN_TIME = 5

def find_networks_listener(listener, seconds, database_session, channel):

    start_time = time.time()
    while(time.time() < start_time + seconds and not stop_threads.isSet()):
        packet = listener.recv()
    
        if packet is None:
            continue

        packets.add_to_datasource(packet, database_session, channel)

def find_networks_sender(sender, seconds):

    start_time = time.time()
    while(time.time() < start_time + seconds and not stop_threads.isSet()):
        sender.send(packets.beacon_request())
        time.sleep(1)
    stop_threads.set()

def handle_interrupt(signal, frame):
    stop_threads.set()
    time.sleep(1)
    exit(1)

def find_networks(listener, sender, channel, database_session, seconds=DEFAULT_SCAN_TIME):
   
    listener.set_channel(channel)
    sender.set_channel(channel)

    global stop_threads 
    stop_threads = Event()

    listen_thread = threading.Thread(target=find_networks_listener, args=(listener, seconds, database_session, channel))
    send_thread = threading.Thread(target=find_networks_sender, args=(sender, seconds))

    listen_thread.daemon = True
    send_thread.daemon = True

    send_thread.start()
    listen_thread.start()

    signal.signal(signal.SIGINT, handle_interrupt)

    while not stop_threads.isSet():
        try:
            send_thread.join(timeout=1)
        except KeyboardInterrupt:
            stop_threads.set() 
