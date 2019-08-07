def scan_length_prompt():
    seconds_input = console_prompt("How long would you like to scan each channel? [default: {G}5{W}")
    try:
        seconds = int(seconds_input)
    except:
        seconds = DEFAULT_SCAN_TIME
    print_info("Scanning each channel for %s seconds" % seconds)
    return seconds