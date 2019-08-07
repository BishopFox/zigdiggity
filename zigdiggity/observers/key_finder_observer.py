from zigdiggity.packets.utils import get_extended_source, extended_address_bytes, get_pan_id
from zigdiggity.packets.aps import is_transport_key
import zigdiggity.crypto.utils as crypto_utils

class KeyFinderObserver():

    def __init__(self):
        pass

    def notify(self, channel, frame):
        if is_transport_key(frame):
            if get_extended_source(frame) is not None:
                extended_source_bytes = extended_address_bytes(get_extended_source(frame))
                decrypted, valid = crypto_utils.zigbee_packet_decrypt(crypto_utils.zigbee_trans_key(crypto_utils.DEFAILT_TRANSPORT_KEY), frame, extended_source_bytes)
                if valid:
                    print_notify("Network key acquired for PAN 0x%04x" % get_pan_id(frame))
                    network_key = bytes(decrypted)[2:18]
                    print_info("Extracted key is 0x%s" % network_key.hex())
