import flask
import flask_sockets


app = flask.Flask(__name__)
sockets = flask_sockets.Sockets(app)


@sockets.route('/echo')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        print("RECIEVED:", message)
        ws.send(message)


@app.route('/')
def hello():
    return 'Hello World!'


if __name__ == "__main__":
    import gevent
    import geventwebsocket.handler
    server = gevent.pywsgi.WSGIServer(('', 5000), app, handler_class=geventwebsocket.handler.WebSocketHandler)
    server.serve_forever()
