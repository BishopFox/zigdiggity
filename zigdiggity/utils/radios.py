import killerbee
import time
from scapy.layers.dot15d4 import Dot15d4FCS, conf 

conf.dot15d4_protocol = 'zigbee'

class Radio():

    channel = 0

    # Statistics for the radio
    total_send_time = 0
    send_count = 0
    total_recv_time = 0
    recv_count = 0
    total_sniff_change_time = 0
    sniff_change_count = 0

    def set_channel(self, channel):
        pass

    def get_channel(self):
        return channel

    def recv(self):
        pass

    def send(self, packet):
        pass

    def sniffer(self, sniffer_on):
        pass

    def close(self):
        pass

    def avg_send(self):
        if self.send_count == 0: return 0
        return self.total_send_time / self.send_count

    def avg_recv(self):
        if self.recv_count == 0: return 0
        return self.total_recv_time / self.recv_count

    def avg_sniff_change(self):
        if self.sniff_change_count == 0: return 0
        return self.total_sniff_change_time / self.sniff_change_count

    def add_send_time(self, seconds):
        self.total_send_time += seconds
        self.send_count += 1

    def add_recv_time(self, seconds):
        self.total_recv_time += seconds
        self.recv_count += 1

    def add_sniff_change_time(self, seconds):
        self.total_sniff_change_time += seconds
        self.sniff_change_count += 1

class KillerBeeRadio(Radio):

    kb = None
    sniff = False

    def __init__(self, device_string):

        self.kb = killerbee.KillerBee(device_string)

    def set_channel(self, channel):
        
        self.sniffer(False)
        self.channel = channel
        self.kb.set_channel(channel)

    def recv(self):

        recv_start = time.time()

        try:
            raw_packet = self.kb.pnext()
            self.sniff = True
        except:
            return None

        recv_end = time.time()

        self.add_recv_time(recv_end - recv_start)

        if not raw_packet is None:
            return Dot15d4FCS(raw_packet['bytes'])

    def send(self, packet):

        send_start = time.time()

        if Dot15d4FCS in packet:
            self.kb.inject(str(packet)[:-2])
        else:
            self.kb.inject(str(packet))

        send_end = time.time()
        self.add_send_time(send_end - send_start)

    def sniffer(self, sniffer_on):
        
        if self.sniff == sniffer_on:
            pass
        else:
            sniff_start = time.time()
            if sniffer_on:
                self.kb.sniffer_on()
            else:
                self.kb.sniffer_off()
            sniff_end = time.time()
            self.add_sniff_change_time(sniff_end - sniff_start)

        self.sniff = sniffer_on

    def close(self):
        self.kb.close()
