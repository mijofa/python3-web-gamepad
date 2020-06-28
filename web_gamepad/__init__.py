import os
import uuid

import flask
import flask_sockets

app = flask.Flask(__name__)
sockets = flask_sockets.Sockets(app)

# I'm not putting anything secure into this session,
# so I don't really care how secret this key is.
# However flask doesn't use sessions at all if I don't give it a secret key of some sort.
#
# I don't need it to be persistent after service restarts though,
# so it can be really secure by randomly generating a new key every restart.
app.secret_key = os.urandom(64)


# Since I don't care about user logins/etc,
# just dump a random uuid in for a differentiating them
@app.before_request
def make_session_identifiable():
    if 'uuid' not in flask.session:
        # FIXME: Let the user's add a username or something
        flask.session['uuid'] = uuid.uuid4()
