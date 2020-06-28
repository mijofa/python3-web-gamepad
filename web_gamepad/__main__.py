from . import http_routes
from . import ws_routes

if __name__ == "__main__":
    import gevent
    import geventwebsocket.handler
    server = gevent.pywsgi.WSGIServer(('', 5000), http_routes.app, handler_class=geventwebsocket.handler.WebSocketHandler)
    server.serve_forever()
