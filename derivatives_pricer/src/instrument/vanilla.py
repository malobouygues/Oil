from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class VanillaOption:
    K: float
    T: float
    cp: int
    qty: float = 1.0
