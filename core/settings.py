"""
Centralized configuration.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WindowConfig:
    clear_color: tuple[float, float, float, float] = (0.53, 0.70, 0.92, 1.0)


@dataclass(frozen=True)
class CameraConfig:
    start_pos: tuple[float, float, float] = (12.0, -18.0, 10.0)
    start_hpr: tuple[float, float, float] = (20.0, -15.0, 0.0)
    mouse_sensitivity: float = 0.15
    move_speed: float = 10.0
    pitch_min_max: tuple[float, float] = (-89.9, 89.9)


@dataclass(frozen=True)
class PhysicsConfig:
    gravity: tuple[float, float, float] = (0.0, 0.0, -9.81)
    substeps: int = 5
    dt_substep: float = 1.0 / 240.0


WINDOW = WindowConfig()
CAMERA = CameraConfig()
PHYSICS = PhysicsConfig()

