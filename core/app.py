"""
High-level application bootstrap.
"""
from __future__ import annotations

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import LVector3

from core.settings import WINDOW, CAMERA, PHYSICS
from core.world import World
from core.camera import CameraRig
from core.controls import ControlSystem
from ui.compass import CompassOverlay
from objects.primitives import GroundPlane, BoxActor

from core.lights import LightingRig

# deaxtivate sound
from panda3d.core import loadPrcFileData
loadPrcFileData("", "audio-library-name null")



class CrashWorldApp(ShowBase):
    """
    Main app that wires world, camera, UI, and controls.
    """

    def __init__(self) -> None:
        super().__init__()
        
        dr0 = self.win.getDisplayRegion(0)
        dr0.setClearColorActive(True)
        dr0.setClearColor(WINDOW.clear_color)

        # Window
        self.win.setClearColor(WINDOW.clear_color)
        self.render.setShaderAuto()

        # World + physics
        self.world = World(self.render, gravity=LVector3(*PHYSICS.gravity))

        # Visual base plane and grid
        GroundPlane.attach_visual_floor(self.render, size=200.0, step=5.0)

        # Example dynamic cube
        box = BoxActor(size=1.0, mass=1.0)
        box_np = self.world.attach_actor(box)
        box_np.setPos(0, 0, 8)

        # Camera rig + controls
        self.disableMouse()
        self.camera_rig = CameraRig(
            camera_np=self.camera,
            start_pos=CAMERA.start_pos,
            start_hpr=CAMERA.start_hpr,
            pitch_limits=CAMERA.pitch_min_max,
        )
        self.controls = ControlSystem(
            base=self,
            camera_rig=self.camera_rig,
            move_speed=CAMERA.move_speed,
            mouse_sens=CAMERA.mouse_sensitivity,
        )

        # UI
        self.compass = CompassOverlay(base=self)
        
        # Lighting
        LightingRig(self.render)

        # Input bindings
        self.accept("alt-0", self.camera_rig.reset_pose)
        self.controls.bind_mouse_right_drag()
        self.controls.bind_keyboard_defaults()

        # Tasks
        self.taskMgr.add(self._update, "app_update")

    # --- main loop ---
    def _update(self, task: Task) -> Task:
        dt = globalClock.getDt()

        # input
        self.controls.update(dt)

        # physics
        self.world.step_physics(
            dt=dt, max_substeps=PHYSICS.substeps, substep_dt=PHYSICS.dt_substep
        )

        # UI sync
        self.compass.update_from_camera(self.camera)

        return Task.cont

