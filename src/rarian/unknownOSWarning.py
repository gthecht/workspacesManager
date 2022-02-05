import sys


def unknown_OS_Warning():
    # need to make it work for linux
    raise TypeError("unknown system platform", sys.platform)
