from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd

from src.market.forward_curve import year_fraction_act365, ForwardCurve
from src.models.implied_vol import implied_vol_black76


@dataclass(frozen=True)
class OptionChain:
    expiry: date
    as_of: date
    F: float
    df: float
    data: pd.DataFrame

    @staticmethod
    def from_csv(
        path: str | Path,
        forward_curve: ForwardCurve,
        as_of: Optional[date] = None,
        df: float = 1.0,
        forward_mapping_rule: str = "next",
        drop_bad: bool = True,
    ) -> "OptionChain":
        path = Path(path)
        expiry = pd.to_datetime(path.stem).date()
        if as_of is None:
            as_of = forward_curve.as_of

        F = forward_curve.forward_on(expiry, rule=forward_mapping_rule)
        T = year_fraction_act365(as_of, expiry)

        raw = pd.read_csv(path)
        if not {"strike", "type", "premium"}.issubset(set(raw.columns)):
            raise ValueError("Options CSV must contain columns: strike, type, premium")

        df_out = raw.copy()
        df_out["strike"] = df_out["strike"].astype(float)
        df_out["type"] = df_out["type"].astype(str).str.upper().str.strip()
        df_out["premium"] = df_out["premium"].astype(float)

        df_out["cp"] = np.where(df_out["type"] == "C", 1, -1)
        df_out["T"] = T
        df_out["F"] = F
        df_out["df"] = float(df)

        vols = []
        oks = []
        for _, r in df_out.iterrows():
            res = implied_vol_black76(
                premium=float(r["premium"]),
                F=F,
                K=float(r["strike"]),
                T=T,
                cp=int(r["cp"]),
                df=float(df),
            )
            vols.append(res.vol)
            oks.append(bool(res.converged) and np.isfinite(res.vol))

        df_out["iv"] = vols
        df_out["ok"] = oks

        if drop_bad:
            df_out = df_out[df_out["ok"]].copy()

        df_out = df_out.sort_values("strike").reset_index(drop=True)

        return OptionChain(expiry=expiry, as_of=as_of, F=F, df=float(df), data=df_out)

    def smile(self) -> Tuple[np.ndarray, np.ndarray]:
        K = self.data["strike"].to_numpy(dtype=float)
        iv = self.data["iv"].to_numpy(dtype=float)
        return K, iv
