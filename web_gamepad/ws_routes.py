import flask_sockets

from . import http_routes


sockets = flask_sockets.Sockets(http_routes.app)


@sockets.route('/echo_listener')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        print("RECIEVED:", message)
        ws.send(message)
