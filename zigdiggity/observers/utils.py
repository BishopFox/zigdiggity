from zigdiggity.observers.wireshark_observer import WiresharkObserver
from zigdiggity.observers.key_finder_observer import KeyFinderObserver
from zigdiggity.observers.stdout_observer import StdoutObserver

def register_wireshark(radio):
    wireshark = WiresharkObserver()
    radio.add_observer(wireshark)

def register_stdout(radio):
    stdout = StdoutObserver()
    radio.add_receive_observer(stdout)

def register_key_finder(radio):
    key_finder = KeyFinderObserver()
    radio.add_receive_observer(key_finder)

def register_all(radio):
    register_wireshark(radio)
    register_key_finder(radio)
