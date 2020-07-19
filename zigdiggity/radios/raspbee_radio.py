import serial
import struct
import sys
import time
from zigdiggity.radios.radio import Radio
from scapy.layers.dot15d4 import Dot15d4FCS, conf

conf.dot15d4_protocol = 'zigbee'

CMD_OFF = 0x30
CMD_RX = 0x31
CMD_TX = 0x32
CMD_RX_AACK = 0x33
CMD_TX_ARET = 0x34
CMD_SET_CHANNEL = 0x35
CMD_LOAD_FRAME = 0x36
CMD_FIRE_FRAME = 0x37
CMD_FIRE_ARET = 0x38
CMD_RX_WMETADATA = 0x39
DEFAULT_BAUD_RATE = 38400

STATE_OFF = 0x00
STATE_RX = 0x01
STATE_TX = 0x02
STATE_RX_AACK = 0x03
STATE_TX_ARET = 0x04
STATE_ON = 0x05
STATE_RX_WMETADATA = 0x06

class RaspbeeRadio(Radio):

    def __init__(self, device):
        self.device = device
        self.state = STATE_OFF
        self.serial = serial.Serial(self.device, DEFAULT_BAUD_RATE, timeout=1, inter_byte_timeout=0.5)
        self.serial.write(bytearray(struct.pack("B", CMD_OFF)))
        self.serial.flush()

    def set_channel(self, channel):
        if (11 <= channel <= 26):
            set_channel_packet = bytearray(struct.pack("BB",CMD_SET_CHANNEL,channel))
            self.serial.write(set_channel_packet)
            self.serial.flush()
            self.channel = channel

    def on(self):
        pass

    def off(self):
        self.serial.write(bytearray(struct.pack("B", CMD_OFF)))
        self.serial.flush()
        self.serial.close()

    def receive(self):
        if self.state != STATE_RX:
            self.serial.write(bytearray(struct.pack("B",CMD_RX)))
            self.serial.flush()
            self.state = STATE_RX
        return self._process_receive()

    def receive_and_ack(self, panid=0x1337, addr=0x0000):
        if self.state != STATE_RX_AACK:
            self.serial.write(struct.pack("B",CMD_RX_AACK) + struct.pack("HH",panid,addr))
            self.serial.flush()
            self.state = STATE_RX_AACK
        return self._process_receive()

    def _process_receive(self):
        try:
            length = self.serial.read()
            print("receiving {0}".format(len(length)))
            if len(length) > 0:
                # intLength = int.from_bytes(length, "big")
                #length_bytes = bytes(str(length).encode('utf-8'))
                if (len(length) == 1):
                    intLength = ord(length)
                else:
                    intLength = struct.unpack('>i', length)[0]

                if intLength > 127:
                    if intLength == 0xff:
                        next_byte = self.serial.read()
                        if len(next_byte) > 0:
                            if (len(next_byte) == 1):
                                # next_length = int.from_bytes(next_byte, "big")
                                next_length = ord(next_byte)
                            else:
                                # next_length = int.from_bytes(next_byte, "big")
                                next_length = struct.unpack('>i', next_byte)[0]
                            print("BBB Reading: {0} bytes".format(next_length))
                            message = self.serial.read(next_length)
                            print("BBB Got: {0} bytes".format(len(message)))
                            print("DEBUG: " + str(message))
                            return None
                    elif intLength == 0xf0:
                        rssi = self.serial.read()
                        next_length = self.serial.read()
                        # next_length_int = int.from_bytes(next_length, "big")
                        if (len(next_length) == 1):
                            # next_length = int.from_bytes(next_byte, "big")
                            next_length_int = ord(next_length)
                        else:
                            # next_length = int.from_bytes(next_byte, "big")
                            next_length_int = struct.unpack('>i', next_length)[0]
                        if next_length_int < 3:
                            print("too short")
                            return None
                        print("CCC Reading: {0} bytes".format(next_length_int))
                        packet = self.serial.read(next_length_int)
                        print("CCC Got: {0} bytes".format(len(packet)))
                        if len(packet) != next_length_int:
                            # Receive timeout occurred - discard.
                            print("incomplete packet 111")
                            return None

                        if STATE_RX_WMETADATA:
                            print("RSSI = {0}".format(rssi))
                            result = dict()
                            result["rssi"]=rssi
                            result["frame"]=Dot15d4FCS(packet)
                            return result
                        else:
                            print("unexpected state 111")
                            return None
                    print("unexpected length: {0}".format(intLength))
                    return None

                recv_start = time.time()
                print("AAA Reading: {0} bytes".format(intLength))
                packet = self.serial.read(intLength)
                print("AAA Got: {0} bytes".format(len(packet)))
                recv_end = time.time()
                self.add_recv_time(recv_end - recv_start)

                if len(packet) != intLength or intLength < 5:
                    # Receive timeout occurred, or bad data - discard.
                    print("incomplete packet 222")
                    return None

                if self.state==STATE_RX_WMETADATA:
                    print("unexpected state 222")
                    return None

                try:
                    print("Creating Dot154d4 Packet")
                    pkt = Dot15d4FCS(packet)
                    return pkt
                except Exception as e:
                    print("Failed to decode packet: {0}".format(e), file=sys.stderr)
                    return None
            else:
                return None
        except serial.serialutil.SerialException as se:
            #traceback.print_exc(file=sys.stdout)
            return None

    def send(self, packet):
        if not Dot15d4FCS in packet:
            packet = packet + b'00'

        send_start = time.time()
        self.serial.write(struct.pack("BB", CMD_TX, len(packet)) + bytes(packet))
        self.serial.flush()
        send_end = time.time()
        self.add_send_time(send_end - send_start)

        self.state = STATE_TX

    def send_and_retry(self, packet):
        if not Dot15d4FCS in packet:
            packet = packet + b'00'

        send_start = time.time()
        self.serial.write(struct.pack("BB", CMD_TX_ARET, len(packet)) +  bytes(packet))
        self.serial.flush()
        send_end = time.time()
        self.add_send_time(send_end - send_start)

        self.state = STATE_TX_ARET

    def load_frame(self, packet):
        if not Dot15d4FCS in packet:
            packet = packet + b'00'

        self.serial.write(struct.pack("BB", CMD_LOAD_FRAME, len(packet)) +  bytes(packet))
        self.serial.flush()

    def fire_frame(self):
        self.serial.write(struct.pack("B", CMD_FIRE_FRAME))
        self.serial.flush()
        self.state = STATE_TX

    def fire_and_retry(self):
        self.serial.write(struct.pack("B", CMD_FIRE_ARET))
        self.serial.flush()
        self.state = STATE_TX_ARET

    def receive_with_metadata(self):
        if self.state != STATE_RX_WMETADATA:
            self.serial.write(bytearray(struct.pack("B",CMD_RX_WMETADATA)))
            self.serial.flush()
            self.state = STATE_RX_WMETADATA
        return self._process_receive()
