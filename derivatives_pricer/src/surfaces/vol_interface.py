from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class VolSurface(Protocol):
    def vol(self, T: float, K: float) -> float:
        ...
