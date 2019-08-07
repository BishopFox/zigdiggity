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
        return self.channel

    def receive(self):
        pass

    def receive_and_ack(self):
        pass

    def send(self, packet):
        pass
    
    def send_and_retry(self, packet):
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
