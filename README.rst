Notes
=====
I'm using flask_sockets instead of flask-socketio because in my (very short) experience with the default socket.io javascript,
it's a pain to work properly behind a reverse proxy.
And I don't want any extra complexities like that possibly slowing things down anyway.
