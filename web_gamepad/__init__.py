import flask
import flask_sockets

app = flask.Flask(__name__)
sockets = flask_sockets.Sockets(app)
