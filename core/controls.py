"""
Input system: mouse look and keyboard movement.
"""
from __future__ import annotations

from dataclasses import dataclass

from direct.showbase.ShowBase import ShowBase
from panda3d.core import KeyboardButton, WindowProperties

from core.camera import CameraRig


@dataclass
class ControlSystem:
    """
    Minimal first-person style controls:
    - RMB drag: yaw/pitch
    - WASD: planar local movement
    - R/F: world Z up/down
    """
    base: ShowBase
    camera_rig: CameraRig
    move_speed: float = 10.0
    mouse_sens: float = 0.15

    def __post_init__(self) -> None:
        self._rmb_held = False
        self._last_mouse = None  # OS pointer snapshot

    # bindings
    def bind_mouse_right_drag(self) -> None:
        self.base.accept("mouse3", self._on_rmb, [True])
        self.base.accept("mouse3-up", self._on_rmb, [False])

    def bind_keyboard_defaults(self) -> None:
        self._kb = self.base.mouseWatcherNode.is_button_down

    # per frame
    def update(self, dt: float) -> None:
        self._update_mouse_look()
        self._update_keyboard(dt)

    # internals
    def _on_rmb(self, down: bool) -> None:
        self._rmb_held = down
        wp = WindowProperties()
        wp.setCursorHidden(down)
        self.base.win.requestProperties(wp)
        if down:
            self._last_mouse = self.base.win.getPointer(0)

    def _update_mouse_look(self) -> None:
        if not self._rmb_held or not self.base.mouseWatcherNode.hasMouse():
            return
        cur = self.base.win.getPointer(0)
        dx = cur.getX() - self._last_mouse.getX()
        dy = cur.getY() - self._last_mouse.getY()
        self._last_mouse = cur

        self.camera_rig.add_yaw_pitch(
            dyaw=-dx * self.mouse_sens,
            dpitch=-dy * self.mouse_sens,
        )

    def _update_keyboard(self, dt: float) -> None:
        speed = self.move_speed
        x = 0.0
        y = 0.0
        z = 0.0

        kb = KeyboardButton.ascii_key
        is_down = self._kb

        if is_down(kb(b"w")):
            y += 1.0
        if is_down(kb(b"s")):
            y -= 1.0
        if is_down(kb(b"a")):
            x -= 1.0
        if is_down(kb(b"d")):
            x += 1.0
        if is_down(kb(b"r")):
            z += 1.0
        if is_down(kb(b"f")):
            z -= 1.0

        if x or y or z:
            # normalize planar vector if needed
            mag = (x * x + y * y) ** 0.5
            if mag > 0.0:
                x /= mag
                y /= mag
            self.camera_rig.move_local(x * speed * dt, y * speed * dt, z * speed * dt)

