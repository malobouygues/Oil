from __future__ import annotations

from src.models.black76 import price as black_price
from src.models.greeks import delta, gamma, vega
from src.instrument.vanilla import VanillaOption


def _get_vol(vol_or_surface, T: float, K: float) -> float:
    if hasattr(vol_or_surface, "vol"):
        return vol_or_surface.vol(T, K)
    return float(vol_or_surface)


def pv(trade: VanillaOption, F: float, vol_or_surface, df: float = 1.0) -> float:
    vol = _get_vol(vol_or_surface, trade.T, trade.K)
    return trade.qty * black_price(F, trade.K, trade.T, vol, df=df, cp=trade.cp)


def greeks(trade: VanillaOption, F: float, vol_or_surface, df: float = 1.0) -> dict[str, float]:
    vol = _get_vol(vol_or_surface, trade.T, trade.K)
    d = trade.qty * delta(F, trade.K, trade.T, vol, df=df, cp=trade.cp)
    g = trade.qty * gamma(F, trade.K, trade.T, vol, df=df)
    v = trade.qty * vega(F, trade.K, trade.T, vol, df=df)
    return {"delta": d, "gamma": g, "vega": v}
