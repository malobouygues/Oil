from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Tuple

import numpy as np

from src.market.forward_curve import ForwardCurve, year_fraction_act365
from src.sabr.params import SABRParams
from src.sabr.sabr import hagan_lognormal_iv


@dataclass(frozen=True)
class SABRVolSurface:
    as_of: date
    forward_curve: ForwardCurve
    params_by_expiry: Dict[date, SABRParams]

    def _times_and_params(self) -> Tuple[np.ndarray, List[SABRParams]]:
        expiries = sorted(self.params_by_expiry.keys())
        times = np.array([year_fraction_act365(self.as_of, d) for d in expiries], dtype=float)
        params = [self.params_by_expiry[d] for d in expiries]
        return times, params

    def _interp_params(self, T: float) -> SABRParams:
        T = float(T)
        times, params = self._times_and_params()

        if len(times) == 0:
            raise ValueError("No SABR params in surface")

        if T <= times.min():
            return params[int(np.argmin(times))]
        if T >= times.max():
            return params[int(np.argmax(times))]

        j = int(np.searchsorted(times, T))
        t0, t1 = times[j - 1], times[j]
        p0, p1 = params[j - 1], params[j]
        w = (T - t0) / (t1 - t0)

        alpha = (1 - w) * p0.alpha + w * p1.alpha
        rho = (1 - w) * p0.rho + w * p1.rho
        nu = (1 - w) * p0.nu + w * p1.nu
        return SABRParams(alpha=float(alpha), beta=float(p0.beta), rho=float(rho), nu=float(nu), shift=float(p0.shift))

    def vol(self, T: float, K: float) -> float:
        F = self.forward_curve.forward_T(T)
        p = self._interp_params(T)
        return float(hagan_lognormal_iv(F=F, K=float(K), T=float(T), p=p))
