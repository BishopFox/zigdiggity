from zigdiggity.radios.radio import Radio
from zigdiggity.observers.observer import Observer

class ObserverRadio(Radio):

    def __init__(self, radio):
        self.radio = radio

        self.receive_observers = []
        self.send_observers = []
        self.loaded_frame = []
    
    def set_channel(self, channel):
        self.radio.set_channel(channel)
   
    def get_channel(self):
        return self.radio.get_channel()

    def off(self):
        self.radio.off()
    
    def receive(self):
        frame = self.radio.receive()
        channel = self.radio.channel
        if frame is not None:
            self.notify_observers(self.receive_observers, channel, frame)
        return frame
    
    def receive_and_ack(self, panid=0x0000, addr=0x0000):
        frame = self.radio.receive_and_ack(panid=panid, addr=addr)
        channel = self.radio.channel
        if frame is not None:
            self.notify_observers(self.receive_observers, channel, frame)
        return frame
    
    def send(self, frame):
        channel = self.radio.channel
        if frame is not None:
            self.notify_observers(self.send_observers, channel, frame)
        self.radio.send(frame)
    
    def send_and_retry(self, frame):
        channel = self.radio.channel
        if frame is not None:
            self.notify_observers(self.send_observers, channel, frame)
        self.radio.send(frame)

    def load_frame(self, frame):
        self.loaded_frame = frame
        self.radio.load_frame(frame)
    
    def fire_frame(self):
        self.radio.fire_frame()
        channel = self.radio.channel
        if self.loaded_frame is not None:
            self.notify_observers(self.send_observers, channel, self.loaded_frame)
    
    def fire_and_retry(self):
        self.radio.fire_and_retry()
        channel = self.radio.channel
        if self.loaded_frame is not None:
            self.notify_observers(self.send_observers, channel, self.loaded_frame)
    
    def receive_with_metadata(self):
        result = self.radio.receive_with_metadata()
        channel = self.radio.channel
        if result is not None:
            self.notify_observers(self.receive_observers, channel, result["frame"])
        return result

    def notify_observers(self, observers, channel, frame):
        for observer in observers:
            observer.notify(channel, frame)

    def add_receive_observer(self, observer):
        if isinstance(observer, Observer):
            self.receive_observers.append(observer)
    
    def add_send_observer(self, observer):
        if isinstance(observer, Observer):
            self.send_observers.append(observer)
    
    def add_observer(self, observer):
        if isinstance(observer, Observer):
            self.receive_observers.append(observer)
            self.send_observers.append(observer)

    def avg_send(self):
        return self.radio.avg_send
    
    def avg_recv(self):
        return self.radio.avg_recv

    def avg_sniff_change(self):
        return self.radio.avg_sniff_change
    
    def add_send_time(self, seconds):
        self.radio.add_send_time(seconds)
    
    def add_recv_time(self, seconds):
        self.radio.add_recv_time(seconds)
    
    def add_sniff_change_time(self, seconds):
        self.radio.add_sniff_change_time(seconds)
