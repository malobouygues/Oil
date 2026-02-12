from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


def _to_date(x) -> date:
    if isinstance(x, date):
        return x
    return pd.to_datetime(x).date()


def year_fraction_act365(as_of: date, expiry: date) -> float:
    return max((expiry - as_of).days / 365.0, 0.0)


@dataclass(frozen=True)
class ForwardCurve:
    as_of: date
    expiries: np.ndarray
    forwards: np.ndarray

    @staticmethod
    def from_csv(path: str | Path, as_of: Optional[date] = None) -> "ForwardCurve":
        path = Path(path)
        df = pd.read_csv(path)

        if "expiry_date" not in df.columns or "future_price" not in df.columns:
            raise ValueError("CSV must contain columns: expiry_date, future_price")

        df["expiry_date"] = pd.to_datetime(df["expiry_date"]).dt.date
        df = df.sort_values("expiry_date")

        if as_of is None:
            as_of = df["expiry_date"].iloc[0]

        expiries = df["expiry_date"].to_numpy(dtype=object)
        forwards = df["future_price"].astype(float).to_numpy()

        return ForwardCurve(as_of=as_of, expiries=expiries, forwards=forwards)

    def forward_on(self, expiry: date, rule: str = "next") -> float:
        expiry = _to_date(expiry)
        idx = None

        if rule == "next":
            candidates = np.where(self.expiries >= expiry)[0]
            if len(candidates) == 0:
                idx = len(self.expiries) - 1
            else:
                idx = int(candidates[0])
        elif rule == "closest":
            deltas = np.array([abs((d - expiry).days) for d in self.expiries], dtype=float)
            idx = int(np.argmin(deltas))
        else:
            raise ValueError("rule must be 'next' or 'closest'")

        return float(self.forwards[idx])

    def forward_T(self, T: float) -> float:
        T = float(T)
        if T <= 0:
            return float(self.forwards[0])

        times = np.array([year_fraction_act365(self.as_of, d) for d in self.expiries], dtype=float)

        if np.all(times == 0):
            return float(self.forwards[0])

        if T <= times.min():
            return float(self.forwards[np.argmin(times)])
        if T >= times.max():
            return float(self.forwards[np.argmax(times)])

        return float(np.interp(T, times, self.forwards))
