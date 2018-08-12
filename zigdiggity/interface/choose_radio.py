from colors import *
from zigdiggity.datastore.radios import Radio
from zigdiggity.utils.radios import KillerBeeRadio
from killerbee.kbutils import *
import time

ZBID_ATTEMPTS = 5

def radio_table(device_list):

    Color.pl("")
    Color.pl("    NUM    USB  TYPE")
    Color.pl("   ----  -----  ---------------")

    counter = 1

    for device in device_list:
        Color.pl("   %4s  %5s  %-15s" % (counter, device[0], device[1]))
        counter += 1

    Color.pl("")

def ask_which_radios(database_session):

    # Check for radios in the database session
    listener_cached = database_session.query(Radio).filter_by(was_listener=True).first()
    sender_cached = database_session.query(Radio).filter_by(was_listener=False).first()

    if (not listener_cached is None and not sender_cached is None):

        #Check that the radios work
        try:
            Color.pl("{.} Testing cached radios.")
            listener = KillerBeeRadio(listener_cached.device_string)
            sender = KillerBeeRadio(sender_cached.device_string)
            listener.close()
            sender.close()

            Color.pl("{+} Using cached radios.")
            return {"listener":listener_cached.device_string, "sender":sender_cached.device_string}
        except:
            # There was a problem with the radios, remove the cache and find new ones
            database_session.query(Radio).delete()
            database_session.commit()


    Color.pl("{.} Finding Radios...")
    Color.pl("{.} Attempting to find the killerbee radios. ")

    device_list = None

    for i in range(ZBID_ATTEMPTS):
        Color.oneliner("{.}    On attempt {C}%s {W}of {C}%s{W} " % (i+1, ZBID_ATTEMPTS))
        try:
            device_list = devlist(None, None, None, None)
            break
        except:
            pass

    if (device_list == None):
        Color.pl("\n{!} Radios could not be located. Please make sure they're connected and try again.")
        exit(1)

    if len(device_list) < 2:
        Color.pl("\n{!} WARNING: All tools require the use of two separate radios.")
        Color.pl("{!} Please make sure you have two radios connected.")
        exit(2)
    
    Color.pl("\n{+} Radios Found.")

    # Interface table
    radio_table(device_list)

    listener_choice = 0
    while(not listener_choice):

        listener_input = Color.prompt("{?} Please select the listener:")

        try:
            listener_choice = int(listener_input)
        except:
            Color.pl("{!} Not a valid choice. Please try again.")
            continue

        if (listener_choice < 1 or listener_choice > len(device_list)):
            Color.pl("{!} Invalid selection. Please try again.")
            listener_choice = 0

    sender_choice = 0
    while(not sender_choice):

        sender_input = Color.prompt("{?} Please select the sender:")

        try:
            sender_choice = int(sender_input)
        except:
            Color.pl("{!} Not a valid choice. Please try again.")
            continue

        if (sender_choice < 1 or sender_choice > len(device_list)):
            Color.pl("{!} Invalid selection. Please try again.")
            sender_choice = 0
        elif sender_choice == listener_choice:
            Color.pl("{!} The listener cannot also be the sender.")
            sender_choice = 0

    listener_string = device_list[listener_choice-1][0]
    sender_string = device_list[sender_choice-1][0]

    # Set the radio cache
    database_session.add(Radio(device_string=listener_string, was_listener=True, radio_type="KB"))
    database_session.add(Radio(device_string=sender_string, was_listener=False, radio_type="LB"))
    database_session.commit()

    return {"listener":listener_string, "sender":sender_string}

