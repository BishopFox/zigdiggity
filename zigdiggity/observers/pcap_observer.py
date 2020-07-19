import os
import subprocess
from zigdiggity.misc.pcap_writer import PcapWriter
from zigdiggity.observers.observer import Observer

DLT_IEEE802_15_4 = 195

class WiresharkObserver(Observer):
    
    def __init__(self):
        args = dict(
            args = ['wireshark', '-ki', '-'],
            stdin = subprocess.PIPE,
            stderr = open(os.devnull,'w'),
            preexec_fn = os.setpgrp
        )
        self.process = subprocess.Popen(**args)
        self.writer = PcapWriter(self.process.stdin, DLT_IEEE802_15_4) # custom writer until scapy's gets better

    def notify(self, channel, packet):
        self.writer.write(bytes(packet))
    
    def close(self):
        self.writer.close()
