from __future__ import annotations

import math

from src.models.black76 import d1_d2, _norm_cdf, _norm_pdf, price as black_price


def delta(F: float, K: float, T: float, vol: float, df: float = 1.0, cp: int = 1) -> float:
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
        if cp * (F - K) > 0.0:
            return df * cp
        return 0.0

    d1, _ = d1_d2(F, K, T, vol)
    return df * cp * _norm_cdf(cp * d1)


def gamma(F: float, K: float, T: float, vol: float, df: float = 1.0) -> float:
    if df < 0.0:
        raise ValueError("df must be >= 0.")
    if F <= 0.0 or K <= 0.0:
        raise ValueError("F and K must be > 0.")
    if T < 0.0:
        raise ValueError("T must be >= 0.")
    if vol < 0.0:
        raise ValueError("vol must be >= 0.")

    if T == 0.0 or vol == 0.0:
        return 0.0

    d1, _ = d1_d2(F, K, T, vol)
    return df * _norm_pdf(d1) / (F * vol * math.sqrt(T))


def vega(F: float, K: float, T: float, vol: float, df: float = 1.0) -> float:
    if df < 0.0:
        raise ValueError("df must be >= 0.")
    if F <= 0.0 or K <= 0.0:
        raise ValueError("F and K must be > 0.")
    if T < 0.0:
        raise ValueError("T must be >= 0.")
    if vol < 0.0:
        raise ValueError("vol must be >= 0.")

    if T == 0.0 or vol == 0.0:
        return 0.0

    d1, _ = d1_d2(F, K, T, vol)
    return df * F * _norm_pdf(d1) * math.sqrt(T)


def delta_fd(F: float, K: float, T: float, vol: float, df: float = 1.0, cp: int = 1, h: float = 1e-4) -> float:
    p_up = black_price(F + h, K, T, vol, df=df, cp=cp)
    p_dn = black_price(F - h, K, T, vol, df=df, cp=cp)
    return (p_up - p_dn) / (2.0 * h)


def gamma_fd(F: float, K: float, T: float, vol: float, df: float = 1.0, cp: int = 1, h: float = 1e-3) -> float:
    p_up = black_price(F + h, K, T, vol, df=df, cp=cp)
    p_0 = black_price(F, K, T, vol, df=df, cp=cp)
    p_dn = black_price(F - h, K, T, vol, df=df, cp=cp)
    return (p_up - 2.0 * p_0 + p_dn) / (h * h)


def vega_fd(F: float, K: float, T: float, vol: float, df: float = 1.0, cp: int = 1, h: float = 1e-4) -> float:
    p_up = black_price(F, K, T, vol + h, df=df, cp=cp)
    p_dn = black_price(F, K, T, vol - h, df=df, cp=cp)
    return (p_up - p_dn) / (2.0 * h)
