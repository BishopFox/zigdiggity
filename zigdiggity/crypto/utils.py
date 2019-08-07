from Crypto.Cipher import AES
from Crypto.Util import Counter
import struct

from scapy.layers.dot15d4 import *
from scapy.layers.zigbee import *
import struct

conf.dot15d4_protocol = 'zigbee'

DEFAULT_TRANSPORT_KEY = b'ZigBeeAlliance09'

BLOCK_SIZE = 16
MIC_SIZE = 4

def block_xor(block1, block2):
  return bytes([_a ^ _b for _a, _b in zip(block1, block2)])

def zigbee_sec_hash(aInput):
  # construct the whole input
  zero_padding_length = (((BLOCK_SIZE-2) - len(aInput) % BLOCK_SIZE) - 1) % BLOCK_SIZE
  padded_input = aInput + b'\x80' + b'\x00' * zero_padding_length + struct.pack(">H", 8*len(aInput))
  number_of_blocks = int(len(padded_input)/BLOCK_SIZE)
  key = b'\x00'*BLOCK_SIZE
  for i in range(number_of_blocks):
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(padded_input[BLOCK_SIZE*i:BLOCK_SIZE*(i+1)])
    key = block_xor(ciphertext, padded_input[BLOCK_SIZE*i:BLOCK_SIZE*(i+1)])
  return key

def zigbee_sec_key_hash(key, aInput):
  ipad = b'\x36'*BLOCK_SIZE
  opad = b'\x5c'*BLOCK_SIZE
  key_xor_ipad = block_xor(key, ipad)
  key_xor_opad = block_xor(key, opad)
  return zigbee_sec_hash(key_xor_opad + zigbee_sec_hash(key_xor_ipad + aInput))

def zigbee_trans_key(key):
  return zigbee_sec_key_hash(key, b'\x00')

def zigbee_decrypt(key, nonce, extra_data, ciphertext, mic):

  cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
  cipher.update(extra_data)
  text = cipher.decrypt(ciphertext)
  try:
    cipher.verify(mic)
    mic_valid = True
  except ValueError:
    mic_valid = False
  return (text, mic_valid)

def zigbee_encrypt(key, nonce, extra_data, text):
  
  cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
  cipher.update(extra_data)

  ciphertext, mic = cipher.encrypt_and_digest(text)

  return (ciphertext, mic)

def zigbee_get_packet_nonce(aPacket, extended_source):

  nonce = struct.pack('Q',*struct.unpack('>Q', extended_source)) + struct.pack('I', aPacket[ZigbeeSecurityHeader].fc) + struct.pack('B', bytes(aPacket[ZigbeeSecurityHeader])[0])
  return nonce

def zigbee_get_packet_header(aPacket):
  
  ciphertext = aPacket[ZigbeeSecurityHeader].data
  mic = aPacket[ZigbeeSecurityHeader].mic
  data_len = len(ciphertext) + len(mic)
 
  if ZigbeeAppDataPayload in aPacket:
      if data_len > 0:
        header = bytes(aPacket[ZigbeeAppDataPayload])[:-data_len]
      else:
        header = bytes(aPacket[ZigbeeAppDataPayload])
  else:
      if data_len > 0:
        header = bytes(aPacket[ZigbeeNWK])[:-data_len]
      else:
        header = bytes(aPacket[ZigbeeNWK])
  
  return header

def zigbee_packet_decrypt(key, aPacket, extended_source):
  
  new_packet = aPacket.copy()
  new_packet[ZigbeeSecurityHeader].nwk_seclevel = 5
  new_packet = Dot15d4FCS(bytes(new_packet))

  ciphertext = new_packet[ZigbeeSecurityHeader].data
  mic = new_packet[ZigbeeSecurityHeader].mic

  header = zigbee_get_packet_header(new_packet)
  nonce = zigbee_get_packet_nonce(new_packet, extended_source)
  
  payload, mic_valid =  zigbee_decrypt(key, nonce, header, ciphertext, mic)
  frametype = new_packet[ZigbeeNWK].frametype
  if frametype == 0 and mic_valid:
    payload = ZigbeeAppDataPayload(payload)
  elif frametype == 1 and mic_valid:
    payload = ZigbeeNWKCommandPayload(payload)
  
  return payload, mic_valid

def zigbee_packet_encrypt(key, aPacket, text, extended_source):
  
  if not ZigbeeSecurityHeader in aPacket:
      return b''

  new_packet = aPacket.copy()
  new_packet[ZigbeeSecurityHeader].nwk_seclevel = 5
  
  header = zigbee_get_packet_header(new_packet)
  nonce = zigbee_get_packet_nonce(new_packet, extended_source)

  data, mic = zigbee_encrypt(key, nonce, header, text)

  new_packet.data = data
  new_packet.mic = mic

  new_packet.nwk_seclevel = 0
  return Dot15d4FCS(bytes(new_packet))

