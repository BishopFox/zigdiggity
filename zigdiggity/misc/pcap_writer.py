import struct
import time

class PcapWriter():

    def __init__(self, file, linktype):
        print("initing...")
        self.linktype = linktype
        self.file = file
        self.header_present = False
        print("initted")

    def _write_header(self, packet):
        print("_write_header")
        self.header_present = True
        self.file.write(struct.pack("IHHIIII", 0xa1b2c3d4, 2, 4, 0, 0, 0xffff, self.linktype))
        self.file.flush()

    def _write_packet(self, packet, sec=None, usec=None, caplen=None, wirelen=None):
        if caplen is None:
            caplen = len(packet)
        if wirelen is None:
            wirelen = caplen
        if sec is None or usec is None:
            t = time.time()
            if sec is None:
                sec = int(t)
                usec = int(round((t-int(t))*1000000))
            elif usec is None:
                usec = 0
        print("_write_packet")
        self.file.write(struct.pack("IIII", sec, usec, caplen, wirelen))
        self.file.write(packet)
        self.file.flush()

    def write(self, packet):
        print("write")
        if not self.header_present:
            self._write_header(packet)
        self._write_packet(packet)

    def close(self):
        self.file.close()
