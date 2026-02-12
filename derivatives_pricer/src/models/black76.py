from __future__ import annotations

import math
from dataclasses import dataclass


SQRT_2PI = math.sqrt(2.0 * math.pi)


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / SQRT_2PI


def d1_d2(F: float, K: float, T: float, vol: float) -> tuple[float, float]:
    if F <= 0.0 or K <= 0.0:
        raise ValueError("F and K must be > 0.")
    if T < 0.0:
        raise ValueError("T must be >= 0.")
    if vol < 0.0:
        raise ValueError("vol must be >= 0.")

    if T == 0.0 or vol == 0.0:
        if F > K:
            return float("inf"), float("inf")
        if F < K:
            return float("-inf"), float("-inf")
        return 0.0, 0.0

    sqrtT = math.sqrt(T)
    vsqrtT = vol * sqrtT
    lnFK = math.log(F / K)
    d1 = (lnFK + 0.5 * vol * vol * T) / vsqrtT
    d2 = d1 - vsqrtT
    return d1, d2


def price(F: float, K: float, T: float, vol: float, df: float = 1.0, cp: int = 1) -> float:
    if cp not in (1, -1):
        raise ValueError("cp must be +1 (call) or -1 (put).")
    if df < 0.0:
        raise ValueError("df must be >= 0.")
    if F <= 0.0 or K <= 0.0:
        raise ValueError("F and K must be > 0.")
    if T < 0.0:
        raise ValueError("T must be >= 0.")
    if vol < 0.0:
        raise ValueError("vol must be >= 0.")

    if T == 0.0 or vol == 0.0:
        return df * max(cp * (F - K), 0.0)

    d1, d2 = d1_d2(F, K, T, vol)
    return df * cp * (F * _norm_cdf(cp * d1) - K * _norm_cdf(cp * d2))


def put_call_parity_residual(F: float, K: float, T: float, vol: float, df: float = 1.0) -> float:
    c = price(F, K, T, vol, df=df, cp=1)
    p = price(F, K, T, vol, df=df, cp=-1)
    return (c - p) - df * (F - K)
