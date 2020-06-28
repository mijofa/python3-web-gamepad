var debug_element;

function init() {
    debug_element = document.getElementById("debug_output");

    // Initialise websocket_handler.js
    websocket_init("../echo_listener");

    // Initialise gamepad_handler.js
    gamepad_init();
}

function write_debug(message) {
    console.debug(message)
    message_element = document.createElement("p");
    message_element.innerText = message;
    debug_element.appendChild(message_element);
}

window.addEventListener("load", init, false);
