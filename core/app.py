"""
High-level application bootstrap.
"""
from __future__ import annotations

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import LVector3
from panda3d.core import CollisionNode, CollisionRay, CollisionTraverser, CollisionHandlerQueue
from panda3d.core import BitMask32, Vec3, Point3

from core.settings import WINDOW, CAMERA, PHYSICS
from core.world import World
from core.camera import CameraRig
from core.controls import ControlSystem
from ui.compass import CompassOverlay
from objects.primitives import GroundPlane, BoxActor

from core.lights import LightingRig
from core.scene_config import load_scene_config, SceneConfigError

# deaxtivate sound
from panda3d.core import loadPrcFileData
loadPrcFileData("", "audio-library-name null")


PICK_MASK = BitMask32.bit(1)
IMPULSE_RADIUS = 4.0
IMPULSE_STRENGTH = 35.0


class CrashWorldApp(ShowBase):
    """
    Main app that wires world, camera, UI, and controls.
    """

    def __init__(self, config_path: str | None = None) -> None:
        super().__init__()
        
        dr0 = self.win.getDisplayRegion(0)
        dr0.setClearColorActive(True)
        dr0.setClearColor(WINDOW.clear_color)

        # Window
        self.win.setClearColor(WINDOW.clear_color)
        self.render.setShaderAuto()

        # World + physics
        self.world = World(self.render, gravity=LVector3(*PHYSICS.gravity))
        
        # Used for mouse click
        self.actors: list = []

        # Visual base plane and grid
        GroundPlane.attach_visual_floor(self.render, size=200.0, step=5.0)

        # Spawn cubes from config (or fall back to a single demo cube)
        if config_path:
            self._spawn_from_config(config_path)
        else:
            box = BoxActor(size=1.0, mass=1.0)
            box_np = self.world.attach_actor(box)
            box_np.setPos(0, 0, 8)
            np.node().setIntoCollideMask(PICK_MASK)
            self.actors.append(box_np)

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
        
        # Mouse click picking
        self._setup_mouse_picking()
        self.accept("mouse1", self._on_mouse_click)

        # Tasks
        self.taskMgr.add(self._update, "app_update")

    def _spawn_from_config(self, config_path: str) -> None:
      try:
        specs = load_scene_config(config_path)
      except SceneConfigError as e:
        raise RuntimeError(f"Scene config error: {e}") from e

      # "Spawn at once": create all actors in one pass before the main loop runs.
      for spec in specs:
        actor = BoxActor(size=spec.size, mass=spec.mass, color=spec.color)
        np = self.world.attach_actor(actor)
        np.setName(spec.name)
        np.setPos(*spec.pos)
        np.node().setIntoCollideMask(PICK_MASK)
        
        self.actors.append(np)

    def _setup_mouse_picking(self) -> None:
        pass

    def _on_mouse_click(self) -> None:
        if not self.mouseWatcherNode.hasMouse():
            return
    
        mpos = self.mouseWatcherNode.getMouse()
    
        # Build a world-space ray from the camera through the mouse position.
        near = Point3()
        far = Point3()
        self.camLens.extrude(mpos, near, far)
    
        near_world = self.render.getRelativePoint(self.camera, near)
        far_world = self.render.getRelativePoint(self.camera, far)
    
        result = self.world.bullet_world.rayTestClosest(near_world, far_world)
    
        if not result.hasHit():
            return
    
        hit_node = result.getNode()  # BulletRigidBodyNode
        actor_np = self.render.find(f"**/+{hit_node.getName()}")
        if actor_np.isEmpty():
            # Fallback: use hit position directly
            center = result.getHitPos()
        else:
            center = actor_np.getPos(self.render)
    
        self._emit_radial_impulse(center)

    def _emit_radial_impulse(self, center: Vec3) -> None:
        for actor_np in self.actors:
            body = actor_np.node()
            if body.getMass() <= 0.0:
                continue  # static objects stay fixed
    
            pos = actor_np.getPos(self.render)
            delta = pos - center
            dist = delta.length()
    
            if dist <= 0.001 or dist > IMPULSE_RADIUS:
                continue
    
            direction = delta.normalized()
            falloff = 1.0 - (dist / IMPULSE_RADIUS)
            strength = IMPULSE_STRENGTH * falloff
    
            impulse = direction * strength
            body.applyCentralImpulse(impulse)


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

