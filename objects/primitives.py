"""
Simple primitive actors: ground plane visual, dynamic box.
"""
from __future__ import annotations

from dataclasses import dataclass

from panda3d.core import (
    NodePath,
    LVector3,
    GeomVertexFormat,
    GeomVertexData,
    Geom,
    GeomTriangles,
    GeomVertexWriter,
    GeomNode,
    CardMaker,
    LineSegs,
    Material,
    LightAttrib,
)
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode

from util.geom import make_grid


@dataclass
class BoxActor:
    """
    Dynamic cube with flat-shaded visual.
    """
    size: float = 1.0
    mass: float = 1.0
    color: tuple[float, float, float, float] = (0.9, 0.3, 0.2, 1.0)
    
    def make_node(self) -> BulletRigidBodyNode:
        s = self.size * 0.5
        shape = BulletBoxShape(LVector3(s, s, s))
        node = BulletRigidBodyNode("box")
        node.addShape(shape)
        node.setMass(self.mass)
        return node

    def attach_visual(self, parent: NodePath) -> None:
        fmt = GeomVertexFormat.getV3n3()
        vdata = GeomVertexData("box", fmt, Geom.UHStatic)
        vdata.setNumRows(24)
        vw = GeomVertexWriter(vdata, "vertex")
        nw = GeomVertexWriter(vdata, "normal")

        def face(nx, ny, nz, verts):
            for v in verts:
                vw.addData3f(*v)
                nw.addData3f(nx, ny, nz)

        s = self.size * 0.5
        face(0, 0, 1, [(-s, -s, s), (s, -s, s), (s, s, s), (-s, s, s)])
        face(0, 0, -1, [(-s, s, -s), (s, s, -s), (s, -s, -s), (-s, -s, -s)])
        face(0, 1, 0, [(-s, s, s), (s, s, s), (s, s, -s), (-s, s, -s)])
        face(0, -1, 0, [(-s, -s, -s), (s, -s, -s), (s, -s, s), (-s, -s, s)])
        face(1, 0, 0, [(s, -s, s), (s, -s, -s), (s, s, -s), (s, s, s)])
        face(-1, 0, 0, [(-s, s, s), (-s, s, -s), (-s, -s, -s), (-s, -s, s)])

        tris = GeomTriangles(Geom.UHStatic)
        for i in range(0, 24, 4):
            tris.addVertices(i, i + 1, i + 2)
            tris.addVertices(i, i + 2, i + 3)

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        node = GeomNode("box_geom")
        node.addGeom(geom)
        vis = parent.attachNewNode(node)
        vis.setColor(*self.color)

        # simple material for specular highlights
        mat = Material()
        mat.setDiffuse((self.color[0], self.color[1], self.color[2], 1.0))
        mat.setSpecular((0.2, 0.2, 0.2, 1.0))
        mat.setShininess(16.0)
        vis.setMaterial(mat, 1)


class GroundPlane:
    """
    Visual ground helper.
    """

    @staticmethod
    def attach_visual_floor(parent: NodePath, size: float = 200.0, step: float = 5.0) -> None:
        cm = CardMaker("floor")
        cm.setFrame(-size, size, -size, size)
        floor = parent.attachNewNode(cm.generate())
        floor.setP(-90)
        floor.setZ(0)
        floor.setColor(0.85, 0.85, 0.85, 1.0)
        floor.setLightOff()

        grid_np = make_grid(size=size, step=step, z=0.01, color=(0.75, 0.75, 0.75, 1.0))
        grid_np.reparentTo(parent)

