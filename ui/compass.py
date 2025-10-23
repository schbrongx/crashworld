"""
3D compass overlay that reflects world axes relative to camera view.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    NodePath,
    Camera,
    PerspectiveLens,
    TransparencyAttrib,
    LineSegs,
    LVector3f,
    CardMaker,
)


@dataclass
class CompassOverlay:
    """
    Renders a small 3D axes widget in the top-left. Semi-transparent background.
    """
    base: ShowBase
    region_bounds: Tuple[float, float, float, float] = (0.0, 0.18, 0.82, 1.0)
    axis_length: float = 0.9
    axis_thickness: float = 1.0  # 1.0 for reduced thicknes on slow systems, 2.0 for better viz
    bg_alpha: float = 0.35

    def __post_init__(self) -> None:
        self._build_scene()
        self._build_display_region()

    # public API
    def update_from_camera(self, camera_np: NodePath) -> None:
        q = camera_np.getQuat(self.base.render)
        q.invertInPlace()
        self._model.setQuat(q)

    # internals
    def _build_scene(self) -> None:
        self._scene = NodePath("compass_scene")
        self._model = self._scene.attachNewNode("compass_model")

        # axes
        axes = self._make_axes(self.axis_length, self.axis_thickness)
        axes.reparentTo(self._model)

        # overlay render state
        self._scene.setDepthTest(False)
        self._scene.setDepthWrite(False)
        axes.setBin("fixed", 0)

    def _build_display_region(self) -> None:
        l, r, b, t = self.region_bounds
        dr = self.base.win.makeDisplayRegion(l, r, b, t)
        dr.setSort(200)
        dr.setClearDepthActive(True)
        dr.setClearColorActive(False)
        
        self._scene.setDepthTest(False)
        self._scene.setDepthWrite(False)

        lens = PerspectiveLens()
        lens.setFov(30)
        lens.setNearFar(0.01, 10)

        self._cam_np = self._scene.attachNewNode(Camera("compass_cam"))
        self._cam_np.node().setLens(lens)
        self._cam_np.node().setScene(self._scene)
        dr.setCamera(self._cam_np)

        # fixed view
        self._cam_np.setPos(2.2, -2.2, 1.6)
        self._cam_np.lookAt(0, 0, 0)

        # background card attached to camera for viewport-aligned backdrop
        cm = CardMaker("compass_bg")
        cm.setFrame(-1.0, 1.0, -1.0, 1.0)
        bg = self._cam_np.attachNewNode(cm.generate())
        bg.setAttrib(TransparencyAttrib.make(TransparencyAttrib.M_alpha))
        bg.setPos(0, 0.02, 0)
        bg.setScale(1.05)
        bg.setColor(0, 0, 0, self.bg_alpha)
        bg.setTransparency(TransparencyAttrib.M_alpha)
        bg.setBin("fixed", -10)

    @staticmethod
    def _make_axes(length: float, thickness: float) -> NodePath:
        def axis(color, a, b) -> NodePath:
            ls = LineSegs()
            ls.setThickness(thickness)
            ls.setColor(*color)
            ls.moveTo(*a)
            ls.drawTo(*b)
            return NodePath(ls.create())

        root = NodePath("axes")
        # semi-transparent RGB axes
        axis((1, 0, 0, 0.5), (0, 0, 0), (length, 0, 0)).reparentTo(root)  # X
        axis((0, 1, 0, 0.5), (0, 0, 0), (0, length, 0)).reparentTo(root)  # Y
        axis((0, 0, 1, 0.5), (0, 0, 0), (0, 0, length)).reparentTo(root)  # Z
        root.setTransparency(TransparencyAttrib.M_alpha)
        return root

