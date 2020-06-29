var gamepad_changedEvent = new Event('gamepadchanged')

function gamepad_init() {
    // Does this browser even support gamepads?
    if (navigator.getGamepads) {
        return true
    } else {
        return false
    }
}


// To reduce network trafic, I only want to upload the new state when something actually changes.
// I need this outside of the scope of the LoopOnce function so that it remains persistent for every loop.
//
// Using a dict instead of a list because I want it based on the .index rather than just the location in a list.
// The list location might change when certain devices come/go, but the .index will stay.
var gamepads_oldState = {}

function gamepad_inputLoopOnce() {
    // Javascripts gamepad stuff doesn't use events and requires polling
    // I'm leaving LoopForever() as a thing to be done elsewhere

    var connected_count = 0

    // "for (i of ..." is equivalent to Python's "for i in ..."
    for (g of navigator.getGamepads()) {
        if (g && g.connected) {
            connected_count += 1;
            if (gamepads_oldState[g.index] != g) {
                // FIXME: Should I really be using GamepadEvent here?
                window.dispatchEvent(new GamepadEvent('gamepadchanged', {'gamepad': g}));
                gamepads_oldState[g.index] = g;
            }
        }
    }

    // FIXME: Fucking Javascript
    // getGamepads() returns a list of length:4 regardless of how many gamepads are actually connected.
    // This means we can't just check the length and instead have to iterate through the list checking each individual item.
    // Thankfully we're already doing some of that
    if (connected_count) {
        // Find the connection state indicator
        gamepad_connection_status = document.getElementById("gamepad_connection_status");
        // Update it with the current state
        gamepad_connection_status.classList.add("connected");
        // Remove the old state, whatever it may have been
        gamepad_connection_status.classList.remove("uninitialised");
        gamepad_connection_status.classList.remove("disconnected");
    } else {
        // Find the connection state indicator
        gamepad_connection_status = document.getElementById("gamepad_connection_status");
        // Update it with the current state
        gamepad_connection_status.classList.add("disconnected");
        // Remove the old state, whatever it may have been
        gamepad_connection_status.classList.remove("uninitialised");
        gamepad_connection_status.classList.remove("connected");
    }
}

// Javascript's JSON parser can't understand Javascript's Gamepad objects
function gamepad_jsonReplacer(key, value) {
    console.log('key '+key);
    console.log('value '+value);
    // Key is the object to be stringified
    // Value is the string JSON has already tried to do
    if (Gamepad.prototype.isPrototypeOf(value)) {
        // It's a Gamepad object, turn it into an array
        // spec: https://w3c.github.io/gamepad/#dom-gamepad
        //
        // NOTE: Technically we're losing the information that this was in fact a Gamepad object
        return {
            'id': value.id,
            'index': value.index,
            'connected': value.connected,
            'timestamp': value.timestamp,
            'mapping': value.mapping,
            'axes': value.axes,
            'buttons': value.buttons,
        }
    } else if (GamepadButton.prototype.isPrototypeOf(value)) {
        // It's a button object, turn it into an array
        // spec: https://w3c.github.io/gamepad/#dom-gamepadbutton
        //
        // NOTE: Technically we're losing the information that this was in fact a GamepadButton object
        return {
            'pressed': value.pressed,
            'touched': value.touched,
            'value': value.value,
        }
    } else {
        // Not something I know how to specifically handle, so don't
        return value
    }
}
