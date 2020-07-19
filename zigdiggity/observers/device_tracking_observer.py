from datastore.devices import Device
from datastore.networks import Network
from datastore import database_session

class DeviceTrackingObserver(Observer):

    def notify(self, channel, packet):

        if not Dot15d4FCS in packet:
            return

        pan_id = data_utils.get_pan_id_by_packet(packet)
        addr = data_utils.get_short_address_by_packet(packet)
        epan_id = data_utils.get_extended_pan_by_packet(packet)
        eaddr = data_utils.get_full_address_by_packet(packet)
        is_coord = data_utils.get_is_coordinator_by_packet(packet)

        pan, network = self.network_track(channel, pan_id, epan_id)
        device = self.device_track(pan, network, addr, eaddr, is_coord)
        self.track_frame_counter(device, packet)
        self.check_for_key_transport(device, network, packet)

    def network_track(self, channel, pan_id, epan_id):

        pan = None
        network = None

        # Ignore broadcast PAN
        if pan_id == 0xffff or pan_id == 0xfffc:
            pan_id = None

        if channel is not None and pan_id is not None:
            pan = database_session.query(PAN).filter_by(channel=channel, pan_id=pan_id)
            if pan is None:
                pan = PAN()
                pan.channel = channel
                pan.pan_id = pan_id

        if epan_id is not None:
            network = database_session.query(Network).filter_by(extended_pan_id=epan_id)
            if network is None:
                network = Network()
                network.extended_pan_id = epan_id
            if pan is not None:
                if pan.network_id != network.id:
                    if pan.network_id is None:
                        pan.network_id = network.id
                    else:
                        unknown_network = data_util.get_unknown_network()
                        pan.network_id = unknown_network.id

        return (pan, network)

    def device_track(self, pan, network, addr,  eaddr, is_coord):

        # Extended address is the most specific identfier of a device
        if eaddr is not None:
            device = database_session.query(Device).filter(extended_address=eaddr).first()

        # If we know the device is attached to a specific network, we can find it using that network
        if device is None and network is not None and not data_utils.is_unknown_network(network) and addr is not None:
            result = database_session.query(Device,PAN,Network).filter(Device.address=addr, Network.id=network.id).orderBy(Device.last_updated.desc()).first()
            device = result.Device

        if device is None and pan is not None and addr is not None:
            device = database_session.query(Device).filter(pan_id=pan.id, address=addr).first()

        if device is None:
            device = Device()

        if pan is not None:
            device.pan_id = pan.id
        if addr is not None:
            device.address = address
        if eadder is not None:
            device.extended_address = extended_address
        if is_coord is not None:
            device.is_coord = is_coord

        return device

    def track_frame_counter(self, device, packet):

        if ZigbeeSecurityHeader in packet and device is not None:
            device.frame_counter = packet[ZigbeeSecurityHeader].fc
            data_utils.commit_changes()

    def check_for_key_transport(self, device, network, packet):

        if ZigbeeSecurityHeader in packet and packet[ZigbeeSecurityHeader].key_type == 0x2:

            if device.extended_address is not None:
                extended_source = device.extended_address
                key = crypto_utils.calculate_transport_key(DEFAULT_TRANSPORT_KEY)

                ciphertext = packet[ZigbeeSecurityHeader].data # TODO: ensure this is the ciphertext
                tag = packet[ZigbeeSecurityHeader].mic # TODO: ensure this is the authentication code
                nonce = crypto_utils.get_nonce_from_packet(packet)

                plaintext = crypto_utils.decrypt_ccm(key, nonce, ciphertext, tag)

                # extract the key
                #TODO
                extracted_key = None

                if extracted_key is not None:
                    network.nwk_key = extracted_key
