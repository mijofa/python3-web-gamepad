import sys
import json
import traceback

import flask

from . import sockets
from . import gamepad_injector

message_states = {}
active_websockets = {}


# AIUI, UInput needs specific "button A press down" actions,
# rather than "here's all the button states [0,1,0]" kind of thing.
# So we need to compare to the previous state to generate those actions.
# FIXME: Can we ask UInput what the current state is rather than trying to remember it?
def _diff_state(user_identifier, new_state):
    if user_identifier not in message_states:
        diffed_state = new_state
    else:
        diffed_state = {}
        # Iterate over the old top-level dict items,
        # ignoring any that haven't changed
        for k in message_states[user_identifier]:
            # These variabls are mostly to keep the line length down
            old_v = message_states[user_identifier][k]
            new_v = new_state[k]

            if old_v != new_v:
                if isinstance(new_v, list):
                    # And if the value is a list, then do similar iterating within that
                    diffed_state[k] = [None if new_v[i] == old_v[i] else new_v[i] for i in range(len(new_v))]
                    assert len(diffed_state[k]) == len(new_v)
                else:
                    diffed_state[k] = new_v

        # Catch any new top-level dict items that might be in the new state,
        # just in case we missed them because they weren't in the old state
        for k in new_state:
            if k not in message_states[user_identifier]:
                diffed_state[k] == new_state[k]

    message_states[user_identifier] = new_state
    return diffed_state


def send_ff_effect(user_identifier, effect):
    ws = active_websockets.get(user_identifier)
    if ws:
        message = {"command": "ffEffectPlay", "data": effect}
        ws.send(json.dumps(message))


def reset_ff_effect(user_identifier):
    ws = active_websockets.get(user_identifier)
    if ws:
        message = {"command": "ffEffectReset"}
        ws.send(json.dumps(message))


## This is the entry point for gamepad inputs after the device has been setup
@sockets.route('/change_gamepad')
def change_gamepad(ws):
    user_identifier = flask.session['uuid']

    if user_identifier in active_websockets:
        # Only one connection per user allowed at a time
        print(user_identifier, "already connected to websocket")
        ws.send('{"command": "error", "data": "Already connected ' + str(user_identifier) + '"}')
        ws.close()
    else:
        print(user_identifier, "connected to websocket")
        active_websockets[user_identifier] = ws

    ws.send('{"command": "ping", "data": "Greetings ' + str(user_identifier) + '"}')
    while not ws.closed:
        # FIXME: Do this in a non-blocking way so we can handle ff effects here in this same thread
        data = ws.receive()
        if data:  # We get am empty message as it closes  # FIXME: check ws.closed again?
            new_state = json.loads(data)
            try:
                if user_identifier not in gamepad_injector.active_devices:
                    message_states[user_identifier] = new_state
                else:
                    # print(user_identifier, "input changed:", )
                    changed_state = _diff_state(user_identifier, new_state)
                    if 'buttons' in changed_state and any(changed_state['buttons']):
                        gamepad_injector.press_buttons(user_identifier, changed_state['buttons'])
                    if 'axes' in changed_state and any((a is not None for a in changed_state['axes'])):
                        gamepad_injector.move_axes(user_identifier, changed_state['axes'])
            except:  # noqa: E722
                print('EXCEPTON', user_identifier, file=sys.stderr)
                traceback.print_tb(sys.exc_info()[2])
            ws.send('{"command": "ping", "data": "Thanks"}')

    print(user_identifier, "disconnected from websocket")
    gamepad_injector.remove_device(user_identifier)
    active_websockets.pop(user_identifier)
