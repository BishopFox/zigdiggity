from colors import *
from devices import display_devices_overwritable
import zigdiggity.utils.scanner as scanner

def scanning(channel):
    Color.oneliner("{.} Scanning channel: {G}%s{W} " % channel)

def scanning_complete():
    Color.oneliner("{+} Scanning complete.                  \n")

def scanning_interface(listener, sender, channels, datasource, seconds):
    previous_lines = 0
    for channel in channels:
        previous_lines = display_devices_overwritable(datasource, previous_lines)
        scanning(channel)
        scanner.find_networks(listener, sender, channel, datasource, seconds)

    display_devices_overwritable(datasource, previous_lines)
    scanning_complete()

