import threading

# evdev used because I don't think python-uinput is maintained anymore,
# and the documentation is lacking
import evdev
import evdev.ecodes

from . import ws_routes
from .evdev_workaround import UInput

# Gets populated as each controller is added
# Will be a mapping of {UUID: UInput_device}
active_devices = {}


class FF_handler(object):
    # Normally threads can't be restarted, but I want this one to be restartable
    _thread = None

    def start(self):
        if self._thread and self._thread.is_alive():
            # Already running, ignore request
            return
        else:
            # It's either finished or never been started
            self._thread = threading.Thread(target=self.run)
            self._thread.start()

    def _upload_effect(self, user_identifier, effect):
        js = active_devices[user_identifier]
        if effect.id in js.ff_effects:
            ws_routes.reset_ff_effect(user_identifier)
        js.ff_effects[effect.id] = effect

    def _convert_effect(self, effect):
        # Turns the evdev.ff.effect into a JSON object for Javascript to understand
        # TODO: Figure out the ramp up/down things rather than just the basic rumble effect
        js_effect = {}
        js_effect['startDelay'] = effect.ff_replay.delay
        js_effect['duration'] = effect.ff_replay.length
        # FIXME: Is 0xffff a legitimate max?
        js_effect['weakMagnitude'] = min(1, effect.u.ff_rumble_effect.weak_magnitude / 0xffff)
        js_effect['strongMagnitude'] = min(1, effect.u.ff_rumble_effect.strong_magnitude / 0xffff)
        return js_effect

    def run(self):  # noqa: C901
        while active_devices:
            # Copying the keys list so as to let the dict get updated during iteration
            for user_identifier in list(active_devices.keys()):
                try:
                    js = active_devices[user_identifier]
                    ev = js.read_one()
                except (KeyError, OSError):
                    # Device has been closed or removed from list
                    continue
                if ev:
                    # FF works by uploading a programmed rumble pattern,
                    # then later on playing that rumble pattern,
                    # and deleting them all when finished
                    if ev.type == evdev.ecodes.EV_UINPUT:
                        # This is the upload
                        if ev.code == evdev.ecodes.UI_FF_UPLOAD:
                            upload = js.begin_upload(ev.value)
                            print("Event uploading", upload.effect_id, ev.value)
                            self._upload_effect(user_identifier, upload.effect)
                            js.end_upload(upload)
                        # This is the deleting
                        elif ev.code == evdev.ecodes.UI_FF_ERASE:
                            erase = js.begin_erase(ev.value)
                            assert erase.effect_id in js.ff_effects
                            js.end_erase(erase)
                            # FIXME: This resets all effects, not just the one being erased
                            if ev.code in js.ff_effects:
                                print(f"{user_identifier} erasing and resetting ff effect")
                                ws_routes.reset_ff_effect(user_identifier)
                                js.ff_effects.pop(erase.effect_id)
                    elif ev.type == evdev.ecodes.EV_FF:
                        # And this is the playback
                        if ev.value:
                            js_effect = self._convert_effect(js.ff_effects[ev.code])
                            print(f"{user_identifier} playing ff effect {js_effect}")
                            ws_routes.send_ff_effect(user_identifier, js_effect)
                        else:
                            if ev.code in js.ff_effects:
                                print(f"{user_identifier} resetting ff effect")
                                ws_routes.reset_ff_effect(user_identifier)

        print("Thread finished")


ff_thread = FF_handler()


class actually_an_axis(object):
    def __init__(self, cap, absinfo, multiplier=1):
        # D-Pad buttons use the same axis with different multipliers
        assert multiplier in (-1, 1)

        self.axis_cap = (cap, absinfo)
        self.multiplier = multiplier

    def __str__(self):
        return f"<actually_an_axis object {self.axis_cap} * {self.multiplier}>"


# FIXME: Do I really need to use the list length as the keys?
# Only really tested with X-Box One & X-Box 360 controllers
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
    # # Untested Switch Pro Controller layout
    # # I have no idea what order these belong in, because for some reason my controller only works on Linux via Steam
    # # FIXME: Test from Windows
    # 18: [
    #     evdev.ecodes.BTN_TRIGGER,
    #     evdev.ecodes.BTN_THUMB,
    #     evdev.ecodes.BTN_THUMB2,
    #     evdev.ecodes.BTN_TOP,
    #     evdev.ecodes.BTN_TOP2,
    #     evdev.ecodes.BTN_PINKIE,
    #     evdev.ecodes.BTN_BASE,
    #     evdev.ecodes.BTN_BASE2,
    #     evdev.ecodes.BTN_BASE3,
    #     evdev.ecodes.BTN_BASE4,
    #     evdev.ecodes.BTN_BASE5,
    #     evdev.ecodes.BTN_BASE6,
    #     # WTF are these?
    #     300,
    #     301,
    #     302,
    #     evdev.ecodes.BTN_DEAD,
    #     evdev.ecodes.BTN_TRIGGER_HAPPY1,
    #     evdev.ecodes.BTN_TRIGGER_HAPPY2,
    # ],
    # # Actual layout as reported by a PS3 controller plugged into boros.cyber
    # 17: [
    #     evdev.ecodes.BTN_SOUTH,  # Same as BTN_A
    #     evdev.ecodes.BTN_EAST,   # Same as BTN_B
    #     evdev.ecodes.BTN_NORTH,  # Same as BTN_X
    #     evdev.ecodes.BTN_WEST,   # Same as BTN_Y
    #     evdev.ecodes.BTN_TL,
    #     evdev.ecodes.BTN_TR,
    #     evdev.ecodes.BTN_TL2,
    #     evdev.ecodes.BTN_TR2,
    #     evdev.ecodes.BTN_SELECT,
    #     evdev.ecodes.BTN_START,
    #     evdev.ecodes.BTN_MODE,
    #     evdev.ecodes.BTN_THUMBL,
    #     evdev.ecodes.BTN_THUMBR,
    #     evdev.ecodes.BTN_DPAD_UP,
    #     evdev.ecodes.BTN_DPAD_DOWN,
    #     evdev.ecodes.BTN_DPAD_LEFT,
    #     evdev.ecodes.BTN_DPAD_RIGHT,
    # ],
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
    6: [
        (evdev.ecodes.ABS_X, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=128, resolution=0)),
        (evdev.ecodes.ABS_Y, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=128, resolution=0)),
        (evdev.ecodes.ABS_Z, evdev.AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        (evdev.ecodes.ABS_RX, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (evdev.ecodes.ABS_RY, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (evdev.ecodes.ABS_RZ, evdev.AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
    ],
    # FIXME: What about analog D-pad but not triggers?
    # 6: [
    #     (evdev.ecodes.ABS_X, evdev.AbsInfo(value=0, min=0, max=65535, fuzz=0, flat=4095, resolution=0)),
    #     (evdev.ecodes.ABS_Y, evdev.AbsInfo(value=0, min=0, max=65535, fuzz=0, flat=4095, resolution=0)),
    #     (evdev.ecodes.ABS_Z, evdev.AbsInfo(value=0, min=0, max=65535, fuzz=255, flat=4095, resolution=0)),
    #     (evdev.ecodes.ABS_RZ, evdev.AbsInfo(value=0, min=0, max=65535, fuzz=255, flat=4095, resolution=0)),
    #     (evdev.ecodes.ABS_HAT0X, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
    #     (evdev.ecodes.ABS_HAT0Y, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
    # ],
    4: [
        (evdev.ecodes.ABS_X, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=128, resolution=0)),
        (evdev.ecodes.ABS_Y, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=128, resolution=0)),
        (evdev.ecodes.ABS_RX, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (evdev.ecodes.ABS_RY, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
    ],
    # FIXME: Entirely untested PS3 layout
    # # Actual layout as reported by a PS3 controller plugged into boros.cyber
    # 6: [
    #     (evdev.ecodes.ABS_X, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=15, resolution=0),
    #     (evdev.ecodes.ABS_Y, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=15, resolution=0),
    #     (evdev.ecodes.ABS_Z, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=15, resolution=0),
    #     (evdev.ecodes.ABS_RX, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=15, resolution=0),
    #     (evdev.ecodes.ABS_RY, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=15, resolution=0),
    #     (evdev.ecodes.ABS_RZ, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=15, resolution=0),
    # ],
    10: [
        (evdev.ecodes.ABS_X, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=128, resolution=0)),
        (evdev.ecodes.ABS_Y, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=128, resolution=0)),
        (evdev.ecodes.ABS_Z, evdev.AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        (evdev.ecodes.ABS_RZ, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (evdev.ecodes.ABS_MT_TOUCH_MAJOR, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (evdev.ecodes.ABS_MT_TOUCH_MINOR, evdev.AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
        (evdev.ecodes.ABS_MT_WIDTH_MAJOR, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (evdev.ecodes.ABS_MT_WIDTH_MINOR, evdev.AbsInfo(value=0, min=0, max=1023, fuzz=0, flat=0, resolution=0)),
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
#        evdev.ecodes.EV_FF: [evdev.ecodes.FF_RUMBLE],
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

    js_dev = UInput(
        events=gamepad_caps,
        name=gamepad_info['id'][:80],  # UInput names must be no longer than 80 characters
        vendor=gamepad_info.get('usb_vendor', 1),
        product=gamepad_info.get('usb_product', 1),
    )

    # Querying the capabilities later actually returns something entirely different.
    # So instead I need to make sure the mapping info stays with the device.
    js_dev.mapping = gamepad_mapping
    js_dev.ff_effects = {}  # Used in FF_handler
    active_devices[user_identifier] = js_dev
    ff_thread.start()
    # dev = active_devices[user_identifier]; breakpoint()


def remove_device(user_identifier):
    print(user_identifier, "DEBUG: Removing device")

    if user_identifier in active_devices:
        # Close the UInput device and remove it from the stack
        active_devices[user_identifier].close()
        active_devices.pop(user_identifier)
