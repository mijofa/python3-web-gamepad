from . import app
from . import http_routes  # noqa: F401
from . import ws_routes  # noqa: F401

if __name__ == "__main__":
    import gevent
    import geventwebsocket.handler
    # FIXME: Make the port number (at least) definable as a command line argument
    server = gevent.pywsgi.WSGIServer(('', 5000), app, handler_class=geventwebsocket.handler.WebSocketHandler)
    server.serve_forever()
