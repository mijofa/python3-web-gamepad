import pprint
import json

import flask

from . import sockets

message_states = {}


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


## This is the entry point for gamepad inputs after the device has been setup
@sockets.route('/change_gamepad')
def change_gamepad(ws):
    print(flask.session['uuid'], "connected to websocket")
    ws.send("Greetings " + str(flask.session['uuid']))
    while not ws.closed:
        new_state = json.loads(ws.receive())
        if new_state:  # We get an empty message as it closes
            print(flask.session['uuid'], "input changed:", )
            pprint.pprint(_diff_state(flask.session['uuid'], new_state))
            ws.send("Thanks")

    print(flask.session['uuid'], "disconnected from websocket")
