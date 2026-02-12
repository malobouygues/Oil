from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from src.models.black76 import price as black76_price


@dataclass(frozen=True)
class ImpliedVolResult:
    vol: float
    iterations: int
    converged: bool


def _intrinsic_forward(F: float, K: float, df: float, cp: int) -> float:
    return df * max(cp * (F - K), 0.0)


def implied_vol_black76(
    premium: float,
    F: float,
    K: float,
    T: float,
    cp: int,
    df: float = 1.0,
    vol_low: float = 1e-8,
    vol_high: float = 5.0,
    tol: float = 1e-8,
    max_iter: int = 200,
) -> ImpliedVolResult:
    premium = float(premium)
    F = float(F)
    K = float(K)
    T = float(T)
    df = float(df)
    cp = int(cp)

    if T <= 0:
        iv = 0.0
        return ImpliedVolResult(vol=iv, iterations=0, converged=True)

    if premium < 0:
        return ImpliedVolResult(vol=np.nan, iterations=0, converged=False)

    intrinsic = _intrinsic_forward(F, K, df, cp)

    if premium + 1e-10 < intrinsic:
        return ImpliedVolResult(vol=np.nan, iterations=0, converged=False)

    if abs(premium - intrinsic) <= 1e-10:
        return ImpliedVolResult(vol=0.0, iterations=0, converged=True)

    def f(sig: float) -> float:
        return black76_price(F=F, K=K, T=T, vol=sig, df=df, cp=cp) - premium

    lo, hi = vol_low, vol_high
    f_lo = f(lo)
    f_hi = f(hi)

    if f_lo > 0:
        return ImpliedVolResult(vol=np.nan, iterations=0, converged=False)

    expand = 0
    while f_hi < 0 and expand < 30:
        hi *= 1.5
        f_hi = f(hi)
        expand += 1

    if f_hi < 0:
        return ImpliedVolResult(vol=np.nan, iterations=expand, converged=False)

    it = 0
    while it < max_iter:
        mid = 0.5 * (lo + hi)
        f_mid = f(mid)

        if abs(f_mid) < tol or (hi - lo) < 1e-10:
            return ImpliedVolResult(vol=float(mid), iterations=it + 1, converged=True)

        if f_mid > 0:
            hi = mid
        else:
            lo = mid

        it += 1

    return ImpliedVolResult(vol=float(0.5 * (lo + hi)), iterations=it, converged=False)
