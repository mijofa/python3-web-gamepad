var debug_element;

function init() {
    debug_element = document.getElementById("debug_output");

    // Initialise websocket_handler.js
    websocket_init("../echo_listener");

    // Initialise gamepad_handler.js
    gamepad_init();

    gamepad_update = function(gamepad) {
        write_debug("Gamepad state changed "+g.index);
        write_debug(JSON.stringify(g, gamepad_jsonReplacer));
    }
    gamepad_onOpenGamepad = function(gamepad) {
        console.log("wheeeooo")
    }

    window.addEventListener("gamepadconnected", function(evt) {
        // TODO: Initiate an event loop if not already running
        // TODO: Send device addition info via PUSH request with JSON

        write_debug("Gamepad added: "+evt.gamepad.id);
        console.log(evt.gamepad);
    });
    window.addEventListener("gamepaddisconnected", function(evt) {
        // TODO: End any event loops that might be left running
        // TODO: Send device removal info via PUSH request with JSON

        write_debug("Gamepad lost: "+evt.gamepad.id);
        console.log(evt.gamepad);
    });
    window.addEventListener("gamepadchanged", function(evt) {
        // TODO: Send input changes via websocket with JSON

        write_debug("Gamepad changed: "+evt.gamepad.id)
        console.log(evt);
    });
}


function write_debug(message) {
    console.debug(message)
    message_element = document.createElement("p");
    message_element.innerText = message;
    debug_element.appendChild(message_element);
}

window.addEventListener("load", init, false);
