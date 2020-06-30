A lightweight webserver that will allow anyone to open the webpage and use it as a game controller proxy kind of thing.

This should make local multiplayer games work online when used in conjunction with something like Jitsi for screensharing,
without the non-local players needing to install (or buy) any client apps on their own devices.

A feature to be added in future is an onscreen virtual gamepad,
which should allow people to use their phones as the gamepad rather than needing one connected to the computer via USB.

Notes
=====
I'm using flask_sockets instead of flask-socketio because in my (very short) experience with the default socket.io javascript,
it's a pain to work properly behind a reverse proxy.
And I don't want any extra complexities like that possibly slowing things down anyway.


Bug with Steam controller
-------------------------
UPDATE: Confirmed to only be an issue with Steam simulating X-360 input
        Steam uses UInput, perhaps UInput is reconnecting all simulated devices when a new one is added?

It's getting a bit funky with my Steam controller, but I think that's because I'm running the client & server on the same system.
What seems to happen is this:
1. Steam controller emulating X-360 connects to Chrome at index:0
2. I select it
3. Chrome tells the server, then immediately sees a new X-360 controller (simulated by this) at index:1 and the Steam controller disappears
4. Chrome doesn't tell the server about it at all, and the Steam Controller doesn't seem to work at all.
5. I reboot the controller and press some buttons
6. Chrome still only sees one X-360 controller, but now it's back at index:0
7. I select it, and everything seems to work

I think there's a bug that when the Steam Controller disconnects, Chrome doesn't tell the server.
However Chrome shouldn't be seeing the controller disconnect at all, but I think that's chrome getting confused about the new controller appearing.
