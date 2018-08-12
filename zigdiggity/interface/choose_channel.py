from colors import *

def ask_which_channels():

    channel = 0
    all_channels = False
    
    while not all_channels and channel == 0:
        channel_raw = Color.prompt("{?} Please choose a channel to scan ({G}11{W}-{G}25{W}) or '{G}all{W}' [{G}all{W}]:")


        if (channel_raw.lower() == "all" or len(channel_raw) == 0):
            all_channels = True
        else:
            try:
                channel = int(channel_raw)
                if channel < 11 or channel > 25:
                    Color.pl("{!} Channel must be between 11 and 25.")
                    channel = 0
                    continue
            except:
                Color.pl("{!} Invalid Channel.")
                continue

        return {"all_channels":all_channels, "channel":channel}
