import serial
import struct
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
        self.serial = serial.Serial(self.device, DEFAULT_BAUD_RATE, timeout=1)
        self.serial.write(bytearray(struct.pack("B", CMD_OFF)))

    def set_channel(self, channel):
        if (11 <= channel <= 26):
            set_channel_packet = bytearray(struct.pack("BB",CMD_SET_CHANNEL,channel))
            self.serial.write(set_channel_packet)
            self.channel = channel

    def on(self):
        pass

    def off(self):
        self.serial.write(bytearray(struct.pack("B", CMD_OFF)))
        self.serial.close()

    def receive(self):
        if self.state != STATE_RX:
            self.serial.write(bytearray(struct.pack("B",CMD_RX)))
            self.state = STATE_RX
        return self._process_receive()

    def receive_and_ack(self, panid=0x1337, addr=0x0000):
        if self.state != STATE_RX_AACK:
            self.serial.write(struct.pack("B",CMD_RX_AACK) + struct.pack("HH",panid,addr))
            self.state = STATE_RX_AACK
        return self._process_receive()

    def _process_receive(self):
        length = self.serial.read()
        if len(length) > 0:
            intLength = int.from_bytes(length, "big")

            if intLength > 127:
                if intLength == 0xff:
                    next_byte = self.serial.read()
                    if len(next_byte) > 0:
                        next_length = int.from_bytes(next_byte, "big")
                        message = self.serial.read(next_length)
                        print("DEBUG: " + str(message))
                elif intLength == 0xf0:
                    rssi = self.serial.read()
                    next_length = self.serial.read()
                    next_length_int = int.from_bytes(next_length, "big")
                    packet = self.serial.read(next_length_int)
                    if next_length_int < 2:
                        return None

                    if STATE_RX_WMETADATA:
                        result = dict()
                        result["rssi"]=rssi
                        result["frame"]=Dot15d4FCS(packet)
                        return result
                    else:
                        return None
                return None
            
            recv_start = time.time()
            packet = self.serial.read(intLength)
            recv_end = time.time()
            self.add_recv_time(recv_end - recv_start)
            
            if intLength <= 2:
                return None
            
            if self.state==STATE_RX_WMETADATA:
                return None

            return Dot15d4FCS(packet)
        else:
            return None

    def send(self, packet):
        if not Dot15d4FCS in packet:
            packet = packet + b'00'

        send_start = time.time()
        self.serial.write(struct.pack("BB", CMD_TX, len(packet)) + bytes(packet))
        send_end = time.time()
        self.add_send_time(send_end - send_start)

        self.state = STATE_TX

    def send_and_retry(self, packet):
        if not Dot15d4FCS in packet:
            packet = packet + b'00'

        send_start = time.time()
        self.serial.write(struct.pack("BB", CMD_TX_ARET, len(packet)) +  bytes(packet))
        send_end = time.time()
        self.add_send_time(send_end - send_start)

        self.state = STATE_TX_ARET

    def load_frame(self, packet):
        if not Dot15d4FCS in packet:
            packet = packet + b'00'

        self.serial.write(struct.pack("BB", CMD_LOAD_FRAME, len(packet)) +  bytes(packet))

    def fire_frame(self):
        self.serial.write(struct.pack("B", CMD_FIRE_FRAME))
        self.state = STATE_TX

    def fire_and_retry(self):
        self.serial.write(struct.pack("B", CMD_FIRE_ARET))
        self.state = STATE_TX_ARET

    def receive_with_metadata(self):
        if self.state != STATE_RX_WMETADATA:
            self.serial.write(bytearray(struct.pack("B",CMD_RX_WMETADATA)))
            self.state = STATE_RX_WMETADATA
        return self._process_receive()
        
