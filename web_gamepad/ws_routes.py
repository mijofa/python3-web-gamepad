from . import sockets


@sockets.route('/echo_listener')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        if not ws.closed:
            print("RECIEVED:", message)
            ws.send(message)
