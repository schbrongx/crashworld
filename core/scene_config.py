"""
Scene config loader.

Loads a JSON file describing cubes (size, color, position) and validates it.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class CubeSpec:
    name: str
    size: float
    mass: float
    color: tuple[float, float, float, float]
    pos: tuple[float, float, float]


class SceneConfigError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise SceneConfigError(msg)


def _as_float_tuple(v: Any, n: int, field: str) -> tuple[float, ...]:
    _require(isinstance(v, (list, tuple)), f'"{field}" must be a list of {n} numbers')
    _require(len(v) == n, f'"{field}" must have exactly {n} elements')
    out = []
    for i, x in enumerate(v):
        _require(isinstance(x, (int, float)), f'"{field}[{i}]" must be a number')
        out.append(float(x))
    return tuple(out)


def _as_str(v: Any, field: str) -> str:
    _require(isinstance(v, str) and v.strip() != "", f'"{field}" must be a non-empty string')
    return v


def _as_pos(v: Any) -> tuple[float, float, float]:
    return _as_float_tuple(v, 3, "pos")  # type: ignore[return-value]


def _as_color(v: Any) -> tuple[float, float, float, float]:
    c = _as_float_tuple(v, 4, "color")  # type: ignore[assignment]
    for i, x in enumerate(c):
        _require(0.0 <= x <= 1.0, f'"color[{i}]" must be in range [0..1]')
    return c  # type: ignore[return-value]


def _as_positive_float(v: Any, field: str) -> float:
    _require(isinstance(v, (int, float)), f'"{field}" must be a number')
    f = float(v)
    _require(f > 0.0, f'"{field}" must be > 0')
    return f


def parse_scene_config(data: dict[str, Any]) -> list[CubeSpec]:
    _require(isinstance(data, dict), "Config root must be a JSON object")

    version = data.get("version", 1)
    _require(isinstance(version, int) and version >= 1, '"version" must be an integer >= 1')

    cubes = data.get("cubes")
    _require(isinstance(cubes, list), '"cubes" must be a list')

    specs: list[CubeSpec] = []
    for idx, raw in enumerate(cubes):
        _require(isinstance(raw, dict), f'cubes[{idx}] must be an object')

        name = _as_str(raw.get("name", f"cube_{idx}"), "name")
        size = _as_positive_float(raw.get("size"), "size")
        mass = float(raw.get("mass", 1.0))
        _require(mass >= 0.0, '"mass" must be >= 0')
        color = _as_color(raw.get("color", [0.9, 0.3, 0.2, 1.0]))
        pos = _as_pos(raw.get("pos"))

        specs.append(
            CubeSpec(
                name=name,
                size=size,
                mass=mass,
                color=color,
                pos=pos,
            )
        )

    return specs


def load_scene_config(path: str | Path) -> list[CubeSpec]:
    p = Path(path)
    _require(p.exists(), f"Config file not found: {p}")
    _require(p.is_file(), f"Config path is not a file: {p}")

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise SceneConfigError(f"Failed to read/parse JSON: {p} ({e})") from e

    return parse_scene_config(data)
