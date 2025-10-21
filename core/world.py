"""
World and physics orchestration.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from panda3d.core import NodePath, LVector3
from panda3d.bullet import BulletWorld, BulletRigidBodyNode


class Actor(Protocol):
    """
    Protocol for physical actors that can be attached to the world.
    """

    def make_node(self) -> BulletRigidBodyNode: ...
    def attach_visual(self, parent: NodePath) -> None: ...


@dataclass
class World:
    """
    Contains the Bullet world and the scene root to attach actors.
    """
    scene_root: NodePath
    gravity: LVector3

    def __post_init__(self) -> None:
        self._world = BulletWorld()
        self._world.setGravity(self.gravity)

        # Add a static plane at Z=0 as ground collider
        from panda3d.bullet import BulletPlaneShape

        plane = BulletPlaneShape(LVector3(0, 0, 1), 0)
        ground = BulletRigidBodyNode("ground")
        ground.addShape(plane)
        ground.setMass(0.0)
        self._ground_np = self.scene_root.attachNewNode(ground)
        self._world.attachRigidBody(ground)

    def attach_actor(self, actor: Actor) -> NodePath:
        node = actor.make_node()
        np = self.scene_root.attachNewNode(node)
        self._world.attachRigidBody(node)
        actor.attach_visual(np)
        return np

    def step_physics(self, dt: float, max_substeps: int, substep_dt: float) -> None:
        self._world.doPhysics(dt, max_substeps, substep_dt)

    @property
    def bullet_world(self) -> BulletWorld:
        return self._world

