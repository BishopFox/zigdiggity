from zigdiggity.interface.colors import *

def single_channel_prompt():
    channel = 0
    while channel == 0:
        channel_input = console_prompt("Please choose a channel ({G}11{W}-{G}25{W}): ")
        try:
            channel = int(channel_input)
            if channel < 11 or channel > 25:
                print_error("Channel must be between 11 and 25.")
                channel = 0
                continue
        except:
            print_error("Invalid channel.")
    return channel

def multi_channel_prompt():
    channels = []
    while len(channels) == 0:
        channel_raw = console_prompt("Please choose a channel to scan ({G}11{W}-{G}25{W}) or '{G}all{W}' [{G}all{W}]:")
        if (channel_raw.lower() == "all" or len(channel_raw) == 0):
            for i in range(11,26):
                channels.append(i)
        else:
            try:
                channel = int(channel_raw)
                if channel < 11 or channel > 25:
                    print_error("Channel must be between 11 and 25.")
                    channel = 0
                    continue
                else:
                    channels.append(channel)
            except:
                print_error("Invalid Channel.")
                continue
    return channels