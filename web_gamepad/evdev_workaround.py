import time

import evdev


class UInput(evdev.UInput):
    def _find_device(self):
        # For some reason I can't understand,
        # when I set the name of the device to something not already recognised as a controller,
        # the device itself takes a bit longer to be ready to open.
        #
        # The _find_device() code already has a delay of 0.1 while it waits,
        # this just delays longer.
        #
        # My initial attempt to fix this was to just rerun _find_device if the first time failed.
        # But that fails when adding a device with the same name as a previously connected device,
        # because then _find_device will find the previous device instead of the new one.
        #
        # FIXME: Report this upstream, get it fixed properly
        #        Why is this even necessary? Does the UInput C code not return the device node upon creation?
        # FIXME: Do we really give a shit about the device name anyway?
        # FIXME: Perhaps wrap the __init__ function and watch only for new devices that weren't there earlier?
        time.sleep(0.2)
        return super()._find_device()
