# evdev used because I don't think python-uinput is maintained anymore,
# and the documentation is lacking
import evdev
import evdev.ecodes


# Gets populated as each controller is added
# Will be a mapping of {UUID: {Index: UInput_device}}
active_devices = {}

# Javascript adds a mapping field to the gamepads for what the browser guesses the mapping is
# This maps that to UInput capabilities
mapping_capabilities = {
    'xbox': {
        ## As copied from the capabilities of Steam's X-box controller
        # {
        #  # ecodes.EV_SYN, I don't really know what it is or how to emulate it, so I'm leaving it out
        #  0: [0, 1, 3, 21],
        #  # ecodes.EV_KEY, this is all the button inputs
        #  1: [304, 305, 307, 308, 310, 311, 314, 315, 316, 317, 318],
        #  # ecodes.EV_ABS, this is the axes inputs
        #  3: [(0,
        #       AbsInfo(value=0, min=-32767, max=32767, fuzz=0, flat=128, resolution=0)),
        #      (1,
        #       AbsInfo(value=0, min=-32767, max=32767, fuzz=0, flat=128, resolution=0)),
        #      (2, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
        #      (3,
        #       AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),
        #      (4,
        #       AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),
        #      (5, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
        #      (16, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
        #      (17, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0))],
        #  # ecodes.EV_FF, I think this is the force-feedback/rumble output
        #  21: [80]}

        # FIXME: WTF is EV_SYN and how do I do it?
        #        I think it's effectively a regular 'ping' from the controller
        # evdev.ecodes.EV_SYN: [
        #     evdev.ecodes.SYN_REPORT,
        #     evdev.ecodes.SYN_CONFIG,
        #     evdev.ecodes.SYN_DROPPED,
        #     evdev.ecodes.EV_FF,  # FIXME: Is that right?
        # ],
        evdev.ecodes.EV_KEY: [
            evdev.ecodes.BTN_A,
            evdev.ecodes.BTN_B,
            evdev.ecodes.BTN_X,
            evdev.ecodes.BTN_Y,
            evdev.ecodes.BTN_TL,
            evdev.ecodes.BTN_TR,
            evdev.ecodes.BTN_SELECT,
            evdev.ecodes.BTN_START,
            evdev.ecodes.BTN_MODE,
            evdev.ecodes.BTN_THUMBL,
            evdev.ecodes.BTN_THUMBR,
        ],
        evdev.ecodes.EV_ABS: [
            (evdev.ecodes.ABS_X, evdev.AbsInfo(value=0, min=-32767, max=32767, fuzz=0, flat=128, resolution=0)),
            (evdev.ecodes.ABS_Y, evdev.AbsInfo(value=0, min=-32767, max=32767, fuzz=0, flat=128, resolution=0)),
            (evdev.ecodes.ABS_Z, evdev.AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
            (evdev.ecodes.ABS_RX, evdev.AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),
            (evdev.ecodes.ABS_RY, evdev.AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),
            (evdev.ecodes.ABS_RZ, evdev.AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
            (evdev.ecodes.ABS_HAT0X, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
            (evdev.ecodes.ABS_HAT0Y, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
        ]
        # FIXME: Add support for EV_FF
        # ecodes.EV_FF: [evdev.ecodes.FF_RUMBLE],
    },
    'standard': {
        # FIXME: WTF is EV_SYN and how do I do it?
        #        I think it's effectively a regular 'ping' from the controller
        # evdev.ecodes.EV_SYN: [
        #     evdev.ecodes.SYN_REPORT,
        #     evdev.ecodes.SYN_CONFIG,
        #     evdev.ecodes.SYN_DROPPED,
        #     evdev.ecodes.EV_FF,  # FIXME: Is that right?
        # ],
        evdev.ecodes.EV_KEY: [
            evdev.ecodes.BTN_A,
            evdev.ecodes.BTN_B,
            evdev.ecodes.BTN_X,
            evdev.ecodes.BTN_Y,
            evdev.ecodes.BTN_TL,
            evdev.ecodes.BTN_TR,
            evdev.ecodes.BTN_SELECT,
            evdev.ecodes.BTN_START,
            evdev.ecodes.BTN_MODE,
            evdev.ecodes.BTN_THUMBL,
            evdev.ecodes.BTN_THUMBR,
        ],
        evdev.ecodes.EV_ABS: [
            (evdev.ecodes.ABS_X, evdev.AbsInfo(value=2672, min=-32768, max=32767, fuzz=0, flat=128, resolution=0)),
            (evdev.ecodes.ABS_Y, evdev.AbsInfo(value=1869, min=-32768, max=32767, fuzz=0, flat=128, resolution=0)),
            (evdev.ecodes.ABS_Z, evdev.AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
            (evdev.ecodes.ABS_RX, evdev.AbsInfo(value=613, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
            (evdev.ecodes.ABS_RY, evdev.AbsInfo(value=280, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
            (evdev.ecodes.ABS_RZ, evdev.AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
            (evdev.ecodes.ABS_HAT0X, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
            (evdev.ecodes.ABS_HAT0Y, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
        ],
        # FIXME: Add support for EV_FF
        # evdev.ecodes.EV_FF: [
        #     evdev.ecodes.RUMBLE,
        #     evdev.ecodes.FF_PERIODIC,
        #     evdev.ecodes.FF_WAVEFORM_MIN,
        #     evdev.ecodes.FF_TRIANGLE,
        #     evdev.ecodes.FF_SINE,
        #     evdev.ecodes.FF_MAX_EFFECTS,
        # ],
    }
}


def add_device(user_identifier, gamepad_info):
    print(user_identifier, "DEBUG: Adding device", gamepad_info)

    assert user_identifier not in active_devices, "Controller already connected"
    assert gamepad_info['mapping'] in mapping_capabilities, "Sorry, controller not supported"
    gamepad_caps = mapping_capabilities[gamepad_info['mapping']]
    assert len(gamepad_info['buttons']) == len(gamepad_caps[evdev.ecodes.EV_KEY]), "Does not match expected button count"
    assert len(gamepad_info['axes']) == len(gamepad_caps[evdev.ecodes.EV_ABS]), "Does not match expected axes count"

    active_devices[user_identifier] = evdev.UInput(
        events=mapping_capabilities[gamepad_info['mapping']],
        name=gamepad_info['id'][:80],  # UInput names must be no longer than 80 characters
        vendor=gamepad_info.get('usb_vendor', 1),
        product=gamepad_info.get('usb_product', 1),
    )
    print(active_devices)
    dev = active_devices[user_identifier]  # noqa: F841


def remove_device(user_identifier):
    print(user_identifier, "DEBUG: Removing device")

    assert user_identifier in active_devices, "Controller not connected"

    # Close the UInput device and remove it from the stack
    active_devices[user_identifier].close()
    active_devices.pop(user_identifier)
