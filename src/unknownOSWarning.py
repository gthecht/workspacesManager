import sys

def unknownOSWarning():
    # need to make it work for linux
    raise TypeError("unknown system platform", sys.platform)