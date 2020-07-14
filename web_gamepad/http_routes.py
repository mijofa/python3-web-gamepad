import re

import flask

from . import app
from . import gamepad_injector


# Blink/Chrome's gamepad ID ends with "(Vendor: 28de Product: 11ff)", so let's use that.
# NOTE: With gamepads recognised as "standard" it comes up as "(STANDARD GAMEPAD Vendor: 0079 Product: 0006)"
# Gecko/Firefox apparently starts the ID with "28de-11ff-" instead, we can use that too.
# FIXME: Can we get this info from Webkit?
usb_ids_re_blink = re.compile(r"(?P<name>.*) \((STANDARD GAMEPAD )?Vendor: (?P<vendor>.*) Product: (?P<product>.*)\)")
usb_ids_re_gecko = re.compile(r"(?P<vendor>[0-9A-Fa-f]{4})-(?P<product>[0-9A-Fa-f]{4})-(?P<name>.*)")


@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/add_gamepad', methods=['POST'])
def add_gamepad():
    gamepad = flask.request.json

    # Javascript has a Gamepad.mapping field to determine what mapping the browser thinks it should use.
    #
    # It only really supports a "standard" mapping, which apparently X-box controllers normally aren't.
    # So I'm hacking my own xbox one in and taking some guesses at when to use it.
    # NOTE: Xbox One controller gets a "standard" mapping, and it's ID is "Microsoft Controller"
    # FIXME: Apparently Xbox 360 mappings are actually different depending on the web client's OS
    if not gamepad['mapping'] and 'X-Box' in gamepad['id']:
        assert len(gamepad['buttons']) == 11, "Not the number of buttons expected from an Xbox 360 controller"
        assert len(gamepad['axes']) == 8, "Not the number of axes expected from an Xbox 360 controller"
        print("For reference. Xbox360 ID =", gamepad['id'])
        # FIXME: Different from 'standard'?
        gamepad['mapping'] = 'xb360'
    elif gamepad['mapping'] == 'standard' and gamepad['id'].startswith("Microsoft Controller"):
        # For some reason the browser seems to rename the Xbox One device ID.
        # It makes no sense to me why it would change this ID, but not the 360, but it does
        print("For reference. Xbone ID =", gamepad['id'])
        gamepad['id'] = 'Microsoft X-Box One pad (' + gamepad['id'].rpartition('(')[2]
        gamepad['mapping'] = 'xbone'

    usb_ids_re = usb_ids_re_blink.match(gamepad['id']) or usb_ids_re_gecko.match(gamepad['id'])
    if usb_ids_re:
        gamepad['id'] = usb_ids_re.group('name')
        # evdev.UInput expects an int object, not a hex string
        gamepad['usb_vendor'] = int(usb_ids_re.group('vendor'), 16)
        gamepad['usb_product'] = int(usb_ids_re.group('product'), 16)

    gamepad_injector.add_device(flask.session['uuid'], gamepad)
    return "Thanks"


@app.route('/remove_gamepad', methods=['POST'])
def remove_gamepad():
    gamepad_injector.remove_device(flask.session['uuid'])
    return "Thanks"
