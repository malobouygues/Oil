from __future__ import annotations

import math

import numpy as np

from src.sabr.params import SABRParams


def _safe_log(x: float) -> float:
    return math.log(max(x, 1e-300))


def hagan_lognormal_iv(F: float, K: float, T: float, p: SABRParams) -> float:
    F = float(F) + float(p.shift)
    K = float(K) + float(p.shift)
    T = float(T)

    if T <= 0:
        return 0.0

    alpha = float(p.alpha)
    beta = float(p.beta)
    rho = float(p.rho)
    nu = float(p.nu)

    if F <= 0 or K <= 0:
        return float("nan")

    if abs(F - K) < 1e-12:
        FK = F
        one_minus_beta = 1.0 - beta
        fk_pow = FK ** one_minus_beta

        term1 = alpha / fk_pow
        term2 = (
            (one_minus_beta ** 2 / 24.0) * (alpha ** 2) / (FK ** (2 * one_minus_beta))
            + (rho * beta * nu * alpha) / (4.0 * (FK ** one_minus_beta))
            + ((2.0 - 3.0 * rho ** 2) / 24.0) * (nu ** 2)
        ) * T
        return term1 * (1.0 + term2)

    lnFK = _safe_log(F / K)
    one_minus_beta = 1.0 - beta
    FK = math.sqrt(F * K)

    z = (nu / alpha) * (FK ** one_minus_beta) * lnFK
    sqrt_term = math.sqrt(max(1.0 - 2.0 * rho * z + z * z, 1e-16))
    xz = _safe_log((sqrt_term + z - rho) / (1.0 - rho))

    denom = (FK ** one_minus_beta) * (
        1.0
        + (one_minus_beta ** 2 / 24.0) * (lnFK ** 2)
        + (one_minus_beta ** 4 / 1920.0) * (lnFK ** 4)
    )

    A = alpha / denom
    B = z / xz

    term2 = (
        (one_minus_beta ** 2 / 24.0) * (alpha ** 2) / (FK ** (2 * one_minus_beta))
        + (rho * beta * nu * alpha) / (4.0 * (FK ** one_minus_beta))
        + ((2.0 - 3.0 * rho ** 2) / 24.0) * (nu ** 2)
    ) * T

    return A * B * (1.0 + term2)
