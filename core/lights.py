from __future__ import annotations

from dataclasses import dataclass
from panda3d.core import AmbientLight, DirectionalLight, OrthographicLens, NodePath

from core.settings import QUALITY


@dataclass
class LightingRig:
    """Sun + skylight + ambient, with shadow maps."""
    render_np: NodePath
    shadow_map_size: int = 2048
    sun_hpr: tuple[float, float, float] = (45.0, -60.0, 0.0)
    sun_color: tuple[float, float, float, float] = (1.0, 0.98, 0.92, 1.0)   # warm
    sky_color: tuple[float, float, float, float] = (0.55, 0.65, 0.85, 1.0)  # cool
    ambient_color: tuple[float, float, float, float] = (0.18, 0.18, 0.20, 1.0)
    ortho_film_size: float = 80.0
    ortho_near_far: tuple[float, float] = (1.0, 150.0)

    def __post_init__(self) -> None:
        if self.render_np.getPythonTag("lighting_rig") is True:
            return
        self.render_np.setPythonTag("lighting_rig", True)

        # Ambient
        al = AmbientLight("al")
        al.setColor(self.ambient_color)
        al_np = self.render_np.attachNewNode(al)
        self.render_np.setLight(al_np)

        # Sun with shadows
        sun = DirectionalLight("sun")
        sun.setColor(self.sun_color)
        if QUALITY.shadows:
            sun.setShadowCaster(True, QUALITY.shadow_map_size, QUALITY.shadow_map_size)
        else:
            sun.setShadowCaster(True, self.shadow_map_size, self.shadow_map_size)
        lens = OrthographicLens()
        lens.setFilmSize(120.0)
        lens.setNearFar(5.0,120.0)
        sun.setLens(lens)
        sun_np = self.render_np.attachNewNode(sun)
        sun_np.setHpr(*self.sun_hpr)
        self.render_np.setLight(sun_np)

        # Skylight fill (no shadows)
        sky = DirectionalLight("sky_fill")
        sky.setColor(tuple(c * 0.25 for c in self.sky_color[:3]) + (1.0,))
        sky_np = self.render_np.attachNewNode(sky)
        sky_np.setHpr(self.sun_hpr[0] + 180.0, 60.0, 0.0)
        self.render_np.setLight(sky_np)
