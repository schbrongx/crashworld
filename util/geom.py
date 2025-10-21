"""
Geometry utilities: grid lines and helpers.
"""
from __future__ import annotations

from panda3d.core import LineSegs, NodePath


def make_grid(
    size: float,
    step: float,
    z: float = 0.0,
    color: tuple[float, float, float, float] = (0.75, 0.75, 0.75, 1.0),
) -> NodePath:
    """
    Create a square grid on Z=z spanning [-size, size].
    """
    ls = LineSegs()
    ls.setThickness(1.0)
    ls.setColor(*color)

    s = int(size)
    st = int(step)
    for x in range(-s, s + 1, st):
        ls.moveTo(x, -size, z)
        ls.drawTo(x, size, z)
    for y in range(-s, s + 1, st):
        ls.moveTo(-size, y, z)
        ls.drawTo(size, y, z)

    return NodePath(ls.create())

