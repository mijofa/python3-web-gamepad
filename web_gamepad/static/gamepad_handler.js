// TODO: Handle FF/rumble events coming from the game/server

var gamepad_changedEvent = new Event('gamepadchanged')

var gamepad_selectorElement;

function gamepad_init() {
    if (navigator.getGamepads) {
        gamepad_selectorElement = document.getElementById("gamepad_selector");
        gamepad_updateSelector();
        document.getElementById("gamepad_identify_button").onclick = gamepad_identifySelectedGamepad;

        return true
    } else {
        // FIXME: How do we handle this?

        return false
    }
}

function gamepad_anyConnected() {
    // FIXME: Fucking Javascript
    // getGamepads() returns a list of length:4 regardless of how many gamepads are actually connected.
    // This means we can't just check the length and instead have to iterate through the list checking each individual item.
    for (g of navigator.getGamepads()) {
        if (g && g.connected) {
            return true;
        }
    }
    return false;
}

function gamepad_updateSelector() {
    // I can't loop through removing only the options that aren't connected,
    // because while removing them the list gets smaller, and JS is dumb.
    //
    // So instead I have to create the new list of options up front,
    // and swap out the old list while trying to preserve the selected on.
    var new_options = [];
    var connected_count = 0
    for (g of navigator.getGamepads()) {
        if (g && g.connected) {
            connected_count += 1;

            option = document.createElement('option');
            option.value = g.index;
            option.innerText = g.id;
            if (gamepad_selectorElement.selectedOptions.length && g.index == gamepad_selectorElement.selectedOptions[0].value) {
                option.selected = true;
            }
            new_options.push(option);
        }
    }

    // FIXME: This feels like a dirty way to remove all children, but it does the job
    gamepad_selectorElement.innerHTML = ''

    // Add the new children back in
    // FIXME: Test with more than a single controller connected
    if (new_options.length != 1) {
        option = document.createElement('option');
        option.innerText = "None connected, push a button";
        option.disabled = true;
        gamepad_selectorElement.appendChild(option);
    } else {
        for (o of new_options) {
            gamepad_selectorElement.appendChild(option)
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

function gamepad_identifySelectedGamepad() {
    // Simply vibrates the selected gamepad for half a second
    for (g of navigator.getGamepads()) {
        if (g && gamepad_isSelectedGamepad(g) && g.connected) {
            g.vibrationActuator.playEffect("dual-rumble", {
                startDelay: 0,
                duration: 500,
                weakMagnitude: 1.0,
                strongMagnitude: 1.0
            });
        }
    }
}

function gamepad_isSelectedGamepad(gamepad) {
    // Feels dumb to make this it's own function, but it's a large snippet of code to copy around
    if (gamepad_selectorElement.selectedOptions.length != 1) {
        return false
    } else {
        return gamepad_selectorElement.selectedOptions[0].value == gamepad.index
    }
}

// To reduce network trafic, I only want to upload the new state when something actually changes.
// I need this outside of the scope of the LoopOnce function so that it remains persistent for every loop.
//
// Using a dict instead of a list because I want it based on the .index rather than just the location in a list.
// The list location might change when certain devices come/go, but the .index will stay.
var gamepads_oldState = {}
// FIXME: Make this only monitor the one selected gamepad
function gamepad_inputLoopOnce() {
    // Javascripts gamepad stuff doesn't use events and requires polling
    // I'm leaving LoopForever() as a thing to be done elsewhere

    // "for (i of ..." is equivalent to Python's "for i in ..."
    for (g of navigator.getGamepads()) {
        if (g && g.connected) {
            if (gamepads_oldState[g.index] != g) {
                // FIXME: Should I really be using GamepadEvent here?
                gamepads_oldState[g.index] = g;
                if (gamepad_isSelectedGamepad(g)) {
                    window.dispatchEvent(new GamepadEvent('gamepadchanged', {'gamepad': g}));
                }
            }
        }
    }
}

// Javascript's JSON parser can't understand Javascript's Gamepad objects
function gamepad_jsonReplacer(key, value) {
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
