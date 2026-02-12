from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

from src.sabr.params import SABRParams
from src.sabr.sabr import hagan_lognormal_iv

try:
    from scipy.optimize import least_squares
    _HAS_SCIPY = True
except Exception:
    _HAS_SCIPY = False


@dataclass(frozen=True)
class SABRCalibrationResult:
    params: SABRParams
    rmse: float
    converged: bool


def calibrate_sabr_smile(
    F: float,
    T: float,
    strikes: np.ndarray,
    vols_mkt: np.ndarray,
    beta: float = 1.0,
    shift: float = 0.0,
    weights: Optional[np.ndarray] = None,
) -> SABRCalibrationResult:
    strikes = np.asarray(strikes, dtype=float)
    vols_mkt = np.asarray(vols_mkt, dtype=float)

    mask = np.isfinite(strikes) & np.isfinite(vols_mkt) & (strikes > 0) & (vols_mkt > 0) & (vols_mkt < 5.0)
    strikes = strikes[mask]
    vols_mkt = vols_mkt[mask]

    if len(strikes) < 5:
        atm_vol = float(np.median(vols_mkt)) if len(vols_mkt) > 0 else 0.3
        alpha0 = atm_vol * (F ** (1.0 - beta))
        p0 = SABRParams(alpha=alpha0, beta=beta, rho=0.0, nu=0.5, shift=shift)
        return SABRCalibrationResult(params=p0, rmse=float("nan"), converged=False)

    if weights is None:
        w = np.ones_like(vols_mkt)
    else:
        w = np.asarray(weights, dtype=float)[mask]
        w = np.where(np.isfinite(w) & (w > 0), w, 1.0)

    atm_idx = int(np.argmin(np.abs(strikes - F)))
    atm_vol = float(vols_mkt[atm_idx])
    alpha0 = max(atm_vol * (F ** (1.0 - beta)), 1e-6)
    x0 = np.array([alpha0, 0.0, 0.5], dtype=float)

    def model_vols(alpha: float, rho: float, nu: float) -> np.ndarray:
        p = SABRParams(alpha=float(alpha), beta=float(beta), rho=float(rho), nu=float(nu), shift=float(shift))
        out = np.array([hagan_lognormal_iv(F, k, T, p) for k in strikes], dtype=float)
        return out

    def residuals(x: np.ndarray) -> np.ndarray:
        alpha, rho, nu = x
        vols = model_vols(alpha, rho, nu)
        return np.sqrt(w) * (vols - vols_mkt)

    lb = np.array([1e-8, -0.999, 1e-8], dtype=float)
    ub = np.array([10.0, 0.999, 5.0], dtype=float)

    if _HAS_SCIPY:
        res = least_squares(residuals, x0=x0, bounds=(lb, ub), xtol=1e-12, ftol=1e-12, gtol=1e-12, max_nfev=5000)
        alpha, rho, nu = res.x
        p = SABRParams(alpha=float(alpha), beta=float(beta), rho=float(rho), nu=float(nu), shift=float(shift))
        rmse = float(np.sqrt(np.mean((model_vols(alpha, rho, nu) - vols_mkt) ** 2)))
        return SABRCalibrationResult(params=p, rmse=rmse, converged=bool(res.success))
    else:
        best = None
        best_rmse = float("inf")
        rng = np.random.default_rng(0)
        for _ in range(2000):
            a = float(rng.uniform(lb[0], ub[0]))
            r = float(rng.uniform(lb[1], ub[1]))
            n = float(rng.uniform(lb[2], ub[2]))
            vols = model_vols(a, r, n)
            rmse = float(np.sqrt(np.mean((vols - vols_mkt) ** 2)))
            if rmse < best_rmse:
                best_rmse = rmse
                best = (a, r, n)
        a, r, n = best
        p = SABRParams(alpha=float(a), beta=float(beta), rho=float(r), nu=float(n), shift=float(shift))
        return SABRCalibrationResult(params=p, rmse=float(best_rmse), converged=False)
