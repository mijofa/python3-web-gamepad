import re

import flask

from . import app
from . import gamepad_injector


@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/add_gamepad', methods=['POST'])
def add_gamepad():
    gamepad = flask.request.json

    if 'uinput' in gamepad['id']:
        print("Ignoring uinput device from browser")
        return "No thanks"

    # Javascript has a Gamepad.mapping field to determine what mapping the browser thinks it should use.
    #
    # It only really supports a "standard" mapping, which apparently X-box controllers normally aren't.
    # So I'm hacking my own xbox one in and taking some guesses at when to use it.
    # FIXME: Does this break X-Bone mappings?
    #        Does it fix them?
    # FIXME: Apparently Xbox 360 mappings are actually different depending on the web client OSs
    if not gamepad['mapping'] and 'X-Box' in gamepad['id']:
        assert len(gamepad['buttons']) == 11
        assert len(gamepad['axes']) == 8
        # FIXME: Different from 'standard'?
        gamepad['mapping'] = 'xbox'

    # On my system (Chrome on Linux) the id ends with "(Vendor: 28de Product: 11ff)", so let's use that.
    # We don't need this, but theoretically it'll help games setup a default mapping
    # NOTE: This won't match the ID field of removal and change updates events, but we don't care about the ID there
    usb_ids_re = re.match("(?P<name>.*) \\(Vendor: (?P<vendor>.*) Product: (?P<product>.*)\\)", gamepad['id'])
    if usb_ids_re:
        gamepad['id'] = usb_ids_re.group('name')
        # I think evdev.UInput expects the hex string to be converted to an int
        gamepad['usb_vendor'] = int(usb_ids_re.group('vendor'), 16)
        gamepad['usb_product'] = int(usb_ids_re.group('product'), 16)

    gamepad_injector.add_device(flask.session['uuid'], gamepad)
    return "Thanks"


@app.route('/remove_gamepad', methods=['POST'])
def remove_gamepad():
    gamepad = flask.request.json
    gamepad_injector.remove_device(flask.session['uuid'], gamepad)
    return "Thanks"
