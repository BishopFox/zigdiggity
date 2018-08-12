from zigdiggity.interface.logo import print_logo
from zigdiggity.interface.choose_radio import ask_which_radios
from zigdiggity.interface.choose_target import ask_which_target
from zigdiggity.utils.radios import KillerBeeRadio

def start_and_get_targets(database_session):

    print_logo()
    radio_device_strings = ask_which_radios(database_session)

    sender = KillerBeeRadio(radio_device_strings['sender'])
    listener = KillerBeeRadio(radio_device_strings['listener'])
  
    # Cycle the listener to avoid issues
    sender.sniffer(True)
    listener.sniffer(False)
    listener.sniffer(False)
    listener.sniffer(True)

    result = {}
    
    result['listener'] = listener 
    result['sender'] = sender
    result['target'] = ask_which_target(listener, sender, database_session)

    return result
