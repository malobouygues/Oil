from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from src.surfaces.vol_interface import VolSurface


@dataclass(frozen=True)
class FlatVol(VolSurface):
    sigma: float

    def vol(self, T: float, K: float) -> float:
        return float(self.sigma)


@dataclass(frozen=True)
class TermVol(VolSurface):
    vols: Dict[float, float]

    def vol(self, T: float, K: float) -> float:
        T = float(T)
        keys = np.array(sorted(self.vols.keys()), dtype=float)
        idx = int(np.argmin(np.abs(keys - T)))
        return float(self.vols[float(keys[idx])])


@dataclass(frozen=True)
class SmileSlice:
    T: float
    vols: Dict[float, float]

    def vol_at_strike(self, K: float) -> float:
        K = float(K)
        keys = np.array(sorted(self.vols.keys()), dtype=float)
        idx = int(np.argmin(np.abs(keys - K)))
        return float(self.vols[float(keys[idx])])


@dataclass(frozen=True)
class SmileSurface(VolSurface):
    slices: Dict[float, SmileSlice]

    def vol(self, T: float, K: float) -> float:
        T = float(T)
        mats = np.array(sorted(self.slices.keys()), dtype=float)
        idx = int(np.argmin(np.abs(mats - T)))
        sl = self.slices[float(mats[idx])]
        return sl.vol_at_strike(K)
