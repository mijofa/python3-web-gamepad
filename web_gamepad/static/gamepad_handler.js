function gamepad_init() {
    window.addEventListener("gamepadconnected", gamepad_onOpenGamepad);
    window.addEventListener("gamepaddisconnected", gamepad_onCloseGamepad);
}

function gamepad_onOpenGamepad(evt) {
    write_debug("Gamepad added: "+evt.gamepad.id);
    console.log(evt.gamepad);
}
function gamepad_onCloseGamepad(evt) {
    write_debug("Gamepad lost: "+evt.gamepad.id);
    console.log(evt.gamepad);
}
