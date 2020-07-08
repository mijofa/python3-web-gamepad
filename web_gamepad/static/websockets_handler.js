// FIXME: This whole thing only handles a single websocket per page
//        Perhaps if more is required we should be using socket.io instead though

function websocket_init(wsUri) {
    // WebSocket() doesn't accept relative URLs directly
    wsUri = new URL(wsUri, window.location.href);
    wsUri.protocol = wsUri.protocol.replace('https', 'wss').replace('http', 'ws')
  
    websocket = new WebSocket(wsUri);
    // FIXME: Use event listeners properly?
    websocket.onopen    = function(evt) { websocket_onOpen(evt) };
    websocket.onclose   = function(evt) { websocket_onClose(evt) };
    websocket.onmessage = function(evt) { websocket_onMessage(evt) };
    websocket.onerror   = function(evt) { websocket_onError(evt) };
}

function websocket_onOpen(evt) {
    write_debug("Websocket connected");

    // Find the connection state indicator
    websocket_connection_status = document.getElementById("websocket_connection_status");
    // Update it with the current state
    websocket_connection_status.classList.add("connected");
    // Remove the old state, whatever it may have been
    websocket_connection_status.classList.remove("uninitialised");
    websocket_connection_status.classList.remove("disconnected");
}

function websocket_onClose(evt) {
    write_debug("Websocket disconnected");

    // Find the connection state indicator
    websocket_connection_status = document.getElementById("websocket_connection_status");
    // Update it with the current state
    websocket_connection_status.classList.add("disconnected");
    // Remove the old state, whatever it may have been
    websocket_connection_status.classList.remove("uninitialised");
    websocket_connection_status.classList.remove("connected");
}

function websocket_onMessage(evt)
{
//   write_debug('Websocket recieved: ' + evt.data);
    message = JSON.parse(evt.data);
    if (message['command'] != 'ping') {
        write_debug('Command recieved: ' + message['command'])
    }
    if (message['command'] == "ffEffectPlay") {
        gamepad_ffEffectPlay(message['data'])
    } else if (message['command'] == "ffEffectReset") {
        gamepad_ffEffectReset()
    }
}

function websocket_onError(evt)
{
  write_debug('Websocket error: ' + evt.data);
}

function websocket_sendMessage(message)
{
//  write_debug("Websocket sent: " + message);
  websocket.send(message);
}
