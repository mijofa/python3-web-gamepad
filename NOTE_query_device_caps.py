#!/usr/bin/python
# This is simply to assist with creating the capability mappings based on controllers plugged in to the computer directly
# It will need some manual massaging, especially around EV_SYN

# OBSOLETE. Use: evdev.util.resolve_ecodes_dict
# Honestly I should've used that from the beginning

import sys

import evdev

js = evdev.InputDevice(sys.argv[1])
caps = js.capabilities()
print(js, caps)
for ev_cap in caps:
    ev_cap_name = evdev.ecodes.EV[ev_cap]
    print(f'evdev.ecodes.{ev_cap_name}: [')
    assert ev_cap_name.startswith('EV_'), "Unexpected cap, I don't know how to handle this"
    ev_cap_dict = evdev.ecodes.__dict__[ev_cap_name[3:]]
    if ev_cap_name == 'EV_KEY':
        ev_cap_dict = ev_cap_dict.copy()
        ev_cap_dict.update(evdev.ecodes.BTN)
    for sub_cap in caps[ev_cap]:
        if isinstance(sub_cap, tuple):
            sub_cap_name = ev_cap_dict[sub_cap[0]]
            sub_cap_args = sub_cap[1]
            print(f'    (evdev.{sub_cap_name}, evdev.ecodes.{repr(sub_cap_args)}),')
        else:
            sub_cap_name = ev_cap_dict.get(sub_cap, sub_cap)
            print(f'    evdev.ecodes.{sub_cap_name},')
    print('],')
