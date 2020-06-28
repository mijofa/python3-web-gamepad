function websocket_init(wsUri) {
    // WebSocket() doesn't accept relative URLs directly
    wsUri = new URL(wsUri, window.location.href);
    wsUri.protocol = wsUri.protocol.replace('https', 'wss').replace('http', 'ws')
  
    websocket = new WebSocket(wsUri);
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
  write_debug('Websocket recieved: ' + evt.data);
//  websocket.close();
}

function websocket_onError(evt)
{
  write_debug('Websocket error: ' + evt.data);
}

function websocket_sendMessage(message)
{
  write_debug("Websocket sent: " + message);
  websocket.send(message);
}
