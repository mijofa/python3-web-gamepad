var websocket_uri = "../change_gamepad";
var gamepad_open_uri = "../add_gamepad";
var gamepad_close_uri = "../remove_gamepad";

var debug_element;
var gamepad_inputLoopIntervalID;

function init() {
    debug_element = document.getElementById("debug_output");

    // Initialise websocket_handler.js
    websocket_init(websocket_uri);

    // Initialise gamepad_handler.js
    gamepad_init();

    // FIXME: I'm no longer using *any* of the offical GamepadEvents and am instead simply using it to create my own
    window.addEventListener("gamepadSelected", function(evt) {
        write_debug("Gamepad selected: "+evt.gamepad.id);

        // Send device addition info via POST request with JSON
        post_gamepad_data(gamepad_open_uri, evt.gamepad);

        // Run the gamepad input loop 50 times per second
        if (!gamepad_inputLoopIntervalID) {
            write_debug("Starting input loop")
            gamepad_inputLoopIntervalID = window.setInterval(gamepad_inputLoopOnce, 20);
        }
    });
    window.addEventListener("gamepadDisabled", function() {
        write_debug("Gamepad disabled");

        gamepad_updateSelector();

        // End the input event loop if that was the last gamepad
        write_debug("Ending input loop")
        clearInterval(gamepad_inputLoopIntervalID);
        gamepad_inputLoopIntervalID = null

        // Send device removal info via POST request with JSON
        post_gamepad_data(gamepad_close_uri);
    });
    window.addEventListener("gamepadInputUpdate", function(evt) {
        websocket_sendMessage(JSON.stringify(evt.gamepad, gamepad_jsonReplacer));
    });
}

function post_gamepad_data(uri, data = null) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', uri, true);
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    if (data) {
        xhr.send(JSON.stringify(data, gamepad_jsonReplacer));
    } else {
        xhr.send()
    }
}


function write_debug(message) {
    console.debug(message)
    message_element = document.createElement("p");
    message_element.innerText = message;
    debug_element.prepend(message_element);
}

window.addEventListener("load", init, false);
