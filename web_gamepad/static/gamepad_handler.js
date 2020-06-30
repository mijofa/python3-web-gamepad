// TODO: Handle FF/rumble events coming from the game/server

var gamepad_changedEvent = new Event('gamepadchanged')

var gamepad_selectorElement;

function gamepad_init() {
    if (navigator.getGamepads) {
        gamepad_selectorElement = document.getElementById("gamepad_selector");
        gamepad_selectorElement.addEventListener('change', gamepad_select);
        gamepad_updateSelector();
        document.getElementById("gamepad_identify_button").onclick = gamepad_identifySelectedGamepad;

        window.addEventListener("gamepadconnected", evt => gamepad_updateSelector());
        window.addEventListener("gamepaddisconnected", evt => gamepad_updateSelector());
        window.addEventListener("gamepaddisconnected", function (evt) {
            if (gamepad_isSelectedGamepad(evt.gamepad)) {
                gamepad_selectorElement.selectedIndex = 0
                window.dispatchEvent(new GamepadEvent('gamepadDisabled'));
            }
        });

        return true
    } else {
        // FIXME: What do we do here?

        return false
    }
}

function gamepad_updateSelector() {
    // I can't loop through removing only the options that aren't connected,
    // because while removing them the list gets smaller, and JS is dumb.
    //
    // So instead I have to create the new list of options up front,
    // and swap out the old list while trying to preserve the selected on.
    var new_options = [];

    null_option = document.createElement('option');
    null_option.innerText = "Disabled";
    null_option.value = 'null';  // Comes out as a string, but that's good enough
    if (! gamepad_selectorElement.selectedOptions[0] || gamepad_selectorElement.selectedOptions[0].value == 'null') {
        null_option.selected = true;
    }
    new_options.push(null_option);

    var connected_count = 0
    for (g of navigator.getGamepads()) {
        if (g && g.connected) {
            connected_count += 1;

            var option = document.createElement('option');
            option.value = g.index;
            option.innerText = g.id;
            if (gamepad_isSelectedGamepad(g)) {
                option.selected = true;
            }
            new_options.push(option);
        }
    }

    // FIXME: This feels like a dirty way to remove all children, but it does the job
    gamepad_selectorElement.innerHTML = ''

    // Add the new children back in
    // FIXME: Test with more than a single controller connected
    if (! connected_count) {
        gamepad_selectorElement.appendChild(null_option);

        var desc_option = document.createElement('option');
        desc_option.innerText = "None connected, push a button";
        desc_option.disabled = true;
        gamepad_selectorElement.appendChild(desc_option);
    } else {
        for (o of new_options) {
            gamepad_selectorElement.appendChild(o)
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

function gamepad_isSelectedGamepad(gamepad) {
    // Feels dumb to make this it's own function, but it'll get reused a lot
    if (! gamepad || gamepad_selectorElement.selectedOptions.length != 1) {
        return false
    } else {
        return gamepad_selectorElement.selectedOptions[0].value == gamepad.index
    }
    return false
}

var gamepad_prevSelected = 'null';
function gamepad_select() {
    console.log(gamepad_prevSelected);
    console.log(gamepad_selectorElement.selectedOptions[0].value);
    if (gamepad_prevSelected == gamepad_selectorElement.selectedOptions[0].value) {
        // No change, do nothing
        return true;
    } else if (gamepad_selectorElement.selectedOptions[0].value == 'null') {
        window.dispatchEvent(new GamepadEvent('gamepadDisabled'));
    } else {
        for (g of navigator.getGamepads()) {
            if (g && gamepad_isSelectedGamepad(g)) {
                // FIXME: Should I really be using GamepadEvent here?
                if (gamepad_prevSelected != 'null') {
                    // Previously had a different gamepad selected, so disable first
                    window.dispatchEvent(new GamepadEvent('gamepadDisabled'));
                } else if (gamepad_prevSelected == gamepad_selectorElement.selectedOptions[0].value) {
                    // Already connected to the same gamepad, do nothing
                } else {
                    window.dispatchEvent(new GamepadEvent('gamepadSelected', {'gamepad': g}));
                }
            }
        }
    }
    gamepad_prevSelected = gamepad_selectorElement.selectedOptions[0].value
    return true;
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

// To reduce network trafic, I only want to upload the new state when something actually changes.
// I need this outside of the scope of the LoopOnce function so that it remains persistent for every loop.
var gamepad_oldState;
function gamepad_inputLoopOnce() {
    // Javascripts gamepad stuff doesn't use events and requires polling
    // LoopForever() is a thing to be done elsewhere

    // "for (i of ..." is equivalent to Python's "for i in ..."
    for (g of navigator.getGamepads()) {
        if (g && g.connected && gamepad_isSelectedGamepad(g)) {
            if (gamepad_oldState != g) {
                // Update the oldState variable for the next loop
                gamepad_oldState = g;
                // FIXME: Should I really be using GamepadEvent here?
                window.dispatchEvent(new GamepadEvent('gamepadInputUpdate', {'gamepad': g}));
            }
        }
    }
}

// Help Javascript's JSON parser understand Javascript's Gamepad objects
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
