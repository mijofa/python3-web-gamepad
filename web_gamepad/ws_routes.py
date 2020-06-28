import flask

from . import sockets


@sockets.route('/echo_listener')
def echo_socket(ws):
    print(flask.session['uuid'], "connected")
    ws.send("Greetings " + str(flask.session['uuid']))
    while not ws.closed:
        message = ws.receive()
        if message:
            print(flask.session['uuid'], "recieved:", message)
            ws.send(message)
    print(flask.session['uuid'], "disconnected")
