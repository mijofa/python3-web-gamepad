# evdev used because I don't think python-uinput is maintained anymore,
# and the documentation is lacking
import evdev
import evdev.ecodes


# Gets populated as each controller is added
# Will be a mapping of {UUID: {Index: UInput_device}}
active_devices = {}


class actually_an_axis(object):
    def __init__(self, cap, absinfo, multiplier=1):
        # D-Pad buttons use the same axis with different multipliers
        assert multiplier in (-1, 1)

        self.axis_cap = (cap, absinfo)
        self.multiplier = multiplier

    def __str__(self):
        return f"<actually_an_axis object {self.axis_cap} * {self.multiplier}>"


# FIXME: This is just for sbone. Something needs to be sorted out for everything.
button_order = [
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

# FIXME: Do I really need to use a dict with the list length as the keys?
assumed_button_caps = {
    17: [
        evdev.ecodes.BTN_A,
        evdev.ecodes.BTN_B,
        evdev.ecodes.BTN_X,
        evdev.ecodes.BTN_Y,
        evdev.ecodes.BTN_TL,
        evdev.ecodes.BTN_TR,
        actually_an_axis(evdev.ecodes.ABS_Z, evdev.AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        actually_an_axis(evdev.ecodes.ABS_RZ, evdev.AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        evdev.ecodes.BTN_SELECT,
        evdev.ecodes.BTN_START,
        evdev.ecodes.BTN_THUMBL,
        evdev.ecodes.BTN_THUMBR,
        actually_an_axis(evdev.ecodes.ABS_HAT0Y, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0), multiplier=-1),  # noqa: E501
        actually_an_axis(evdev.ecodes.ABS_HAT0Y, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
        actually_an_axis(evdev.ecodes.ABS_HAT0X, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0), multiplier=-1),  # noqa: E501
        actually_an_axis(evdev.ecodes.ABS_HAT0X, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
        evdev.ecodes.BTN_MODE,
    ],
    16: [
        evdev.ecodes.BTN_A,
        evdev.ecodes.BTN_B,
        evdev.ecodes.BTN_X,
        evdev.ecodes.BTN_Y,
        evdev.ecodes.BTN_TL,
        evdev.ecodes.BTN_TR,
        actually_an_axis(evdev.ecodes.ABS_Z, evdev.AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        actually_an_axis(evdev.ecodes.ABS_RZ, evdev.AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        evdev.ecodes.BTN_SELECT,
        evdev.ecodes.BTN_START,
        evdev.ecodes.BTN_THUMBL,
        evdev.ecodes.BTN_THUMBR,
        actually_an_axis(evdev.ecodes.ABS_HAT0Y, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0), multiplier=-1),  # noqa: E501
        actually_an_axis(evdev.ecodes.ABS_HAT0Y, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
        actually_an_axis(evdev.ecodes.ABS_HAT0X, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0), multiplier=-1),  # noqa: E501
        actually_an_axis(evdev.ecodes.ABS_HAT0X, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
    ],
    15: [
        evdev.ecodes.BTN_A,
        evdev.ecodes.BTN_B,
        evdev.ecodes.BTN_X,
        evdev.ecodes.BTN_Y,
        evdev.ecodes.BTN_TL,
        evdev.ecodes.BTN_TR,
        evdev.ecodes.BTN_SELECT,
        evdev.ecodes.BTN_START,
        evdev.ecodes.BTN_THUMBL,
        evdev.ecodes.BTN_THUMBR,
        actually_an_axis(evdev.ecodes.ABS_HAT0Y, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0), multiplier=-1),  # noqa: E501
        actually_an_axis(evdev.ecodes.ABS_HAT0Y, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
        actually_an_axis(evdev.ecodes.ABS_HAT0X, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0), multiplier=-1),  # noqa: E501
        actually_an_axis(evdev.ecodes.ABS_HAT0X, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
        evdev.ecodes.BTN_MODE,
    ],
    13: [
        evdev.ecodes.BTN_A,
        evdev.ecodes.BTN_B,
        evdev.ecodes.BTN_X,
        evdev.ecodes.BTN_Y,
        evdev.ecodes.BTN_TL,
        evdev.ecodes.BTN_TR,
        actually_an_axis(evdev.ecodes.ABS_Z, evdev.AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        actually_an_axis(evdev.ecodes.ABS_RZ, evdev.AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        evdev.ecodes.BTN_SELECT,
        evdev.ecodes.BTN_START,
        evdev.ecodes.BTN_THUMBL,
        evdev.ecodes.BTN_THUMBR,
        evdev.ecodes.BTN_MODE,
    ],
    11: [
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
}
assumed_axes_caps = {
    8: [
        (evdev.ecodes.ABS_X, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=128, resolution=0)),
        (evdev.ecodes.ABS_Y, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=128, resolution=0)),
        (evdev.ecodes.ABS_Z, evdev.AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        (evdev.ecodes.ABS_RX, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (evdev.ecodes.ABS_RY, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (evdev.ecodes.ABS_RZ, evdev.AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        (evdev.ecodes.ABS_HAT0X, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
        (evdev.ecodes.ABS_HAT0Y, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
    ],
    # FIXME: What about analog D-pad but not triggers?
    6: [
        (evdev.ecodes.ABS_X, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=128, resolution=0)),
        (evdev.ecodes.ABS_Y, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=128, resolution=0)),
        (evdev.ecodes.ABS_Z, evdev.AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        (evdev.ecodes.ABS_RX, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (evdev.ecodes.ABS_RY, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (evdev.ecodes.ABS_RZ, evdev.AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
    ],
    4: [
        (evdev.ecodes.ABS_X, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=128, resolution=0)),
        (evdev.ecodes.ABS_Y, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=128, resolution=0)),
        (evdev.ecodes.ABS_RX, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (evdev.ecodes.ABS_RY, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
    ],
}


def assume_caps_and_mapping(js_gamepad):
    mapping = {
        evdev.ecodes.EV_KEY: assumed_button_caps[len(js_gamepad['buttons'])],
        evdev.ecodes.EV_ABS: assumed_axes_caps[len(js_gamepad['axes'])],
    }
    caps = {
        evdev.ecodes.EV_KEY: [key for key in mapping[evdev.ecodes.EV_KEY]
                              if not isinstance(key, actually_an_axis)],
        evdev.ecodes.EV_ABS: [axis for axis in mapping[evdev.ecodes.EV_ABS]],
        # FIXME: Add support for EV_FF
        # ecodes.EV_FF: [evdev.ecodes.FF_RUMBLE],
    }

    for btn in mapping[evdev.ecodes.EV_KEY].copy():
        if isinstance(btn, actually_an_axis):
            if btn.axis_cap not in caps[evdev.ecodes.EV_ABS]:
                caps[evdev.ecodes.EV_ABS].append(btn.axis_cap)

    return caps, mapping


def press_buttons(user_identifier, buttons):
    # Note: thanks to _diff_state in ws_routes.py we don't need to worry about whether the buttons were pressed or not beforehand
    js_dev = active_devices[user_identifier]
    # btn_caps = js_dev.capabilities()[evdev.ecodes.EV_KEY]

    assert len(buttons) == len(js_dev.mapping[evdev.ecodes.EV_KEY])

    for n in range(len(buttons)):
        if buttons[n] is None:
            # No change to this button, so skip it
            continue

        if isinstance(js_dev.mapping[evdev.ecodes.EV_KEY][n], actually_an_axis):
            axis_map = js_dev.mapping[evdev.ecodes.EV_KEY][n]
            js_dev.write(evdev.ecodes.EV_ABS,
                         axis_map.axis_cap[0],
                         int(axis_map.axis_cap[1].max * buttons[n]['value']) * axis_map.multiplier)
        else:
            # if buttons[n]['pressed']:
            #     print("Pressing", n, evdev.ecodes.BTN[js_dev.mapping[evdev.ecodes.EV_KEY][n]])
            js_dev.write(evdev.ecodes.EV_KEY,
                         js_dev.mapping[evdev.ecodes.EV_KEY][n],
                         1 if buttons[n]['pressed'] else 0)

    js_dev.syn()


def move_axes(user_identifier, axes):
    js_dev = active_devices[user_identifier]

    assert len(axes) == len(js_dev.mapping[evdev.ecodes.EV_ABS])

    for n in range(len(axes)):
        if axes[n] is None:
            # No change to this axis, so skip it
            continue

        axis_map = js_dev.mapping[evdev.ecodes.EV_ABS][n]

        js_dev.write(evdev.ecodes.EV_ABS,
                     axis_map[0],
                     int(axis_map[1].max * axes[n]))

    js_dev.syn()


def add_device(user_identifier, gamepad_info):
    print(user_identifier, "DEBUG: Adding device", gamepad_info['id'],
          '# of buttons', len(gamepad_info['buttons']),
          '# of axes', len(gamepad_info['axes']))

    assert user_identifier not in active_devices, "Controller already connected"
    gamepad_caps, gamepad_mapping = assume_caps_and_mapping(gamepad_info)

    js_dev = evdev.UInput(
        events=gamepad_caps,
        name="Microsoft X-Box One pad",  # gamepad_info['id'][:80],  # UInput names must be no longer than 80 characters
        vendor=gamepad_info.get('usb_vendor', 1),
        product=gamepad_info.get('usb_product', 1),
    )
    # Querying the capabilities later actually returns something entirely different.
    # So instead I need to make sure the mapping info stays with the device.
    js_dev.mapping = gamepad_mapping
    active_devices[user_identifier] = js_dev
    dev = active_devices[user_identifier]  # noqa: F841


def remove_device(user_identifier):
    print(user_identifier, "DEBUG: Removing device")

    if user_identifier in active_devices:
        # Close the UInput device and remove it from the stack
        active_devices[user_identifier].close()
        active_devices.pop(user_identifier)
