"""
Camera rig and pose management.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from panda3d.core import NodePath, LVector3


@dataclass
class CameraRig:
    """
    Wraps the engine camera NodePath and exposes pose control.
    """
    camera_np: NodePath
    start_pos: Tuple[float, float, float]
    start_hpr: Tuple[float, float, float]
    pitch_limits: Tuple[float, float] = (-89.9, 89.9)

    def __post_init__(self) -> None:
        self.reset_pose()

    # pose
    def reset_pose(self) -> None:
        self.camera_np.setPos(*self.start_pos)
        self.camera_np.setHpr(*self.start_hpr)

    # rotation
    def add_yaw_pitch(self, dyaw: float, dpitch: float) -> None:
        h, p, r = self.camera_np.getHpr()
        p = max(self.pitch_limits[0], min(self.pitch_limits[1], p + dpitch))
        self.camera_np.setHpr(h + dyaw, p, r)

    # translation
    def move_local(self, dx: float, dy: float, dz_world: float) -> None:
        """
        Move relative to camera orientation in X/Y, and along world Z for Z.
        """
        q = self.camera_np.getQuat(render)
        right = q.xform(LVector3(1, 0, 0))
        fwd = q.xform(LVector3(0, 1, 0))
        delta = right * dx + fwd * dy + LVector3(0, 0, dz_world)
        self.camera_np.setPos(self.camera_np.getPos(render) + delta)

