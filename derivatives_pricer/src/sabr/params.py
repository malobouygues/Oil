from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SABRParams:
    alpha: float
    beta: float
    rho: float
    nu: float
    shift: float = 0.0
