from zigdiggity.interface.colors import Color

DEBUG = True

def print_error(message):
    Color.pl("{!} " + message)

def print_info(message):
    Color.pl("{.} " + message)

def print_notify(message):
    Color.pl("{+} " + message)

def print_debug(message):
    if DEBUG:
        Color.pl("{.} " + message)

def console_prompt(message):
    return Color.prompt("{?} " + message)

