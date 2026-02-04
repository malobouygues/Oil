# WTI M1/M2 Time Spread & Rolling Structure

This project builds a continuous, adjusted time-series of the WTI M1/M2 Spread to isolate short-term physical scarcity signals from expiration noise.

**Objective:** To backtest the magnitude of current Backwardation/Contango events against historical standards using statistical normalization (Z-Scores), while solving the data engineering challenge of futures contract rollovers.

## 1. Context & Rationale

While the Forward Curve (Project 1) gives a snapshot, traders need to know if the current tightness is historically extreme. The M1/M2 Spread (Front Month vs. Second Month) is the heartbeat of the physical market. It dictates the incentive for managing inventory at the Cushing, OK delivery hub: should traders draw down stocks (Backwardation) or fill the tanks (Contango)?

**The Problem** Raw futures data is fragmented. You cannot simply download "Generic 1st Month Crude" without encountering massive price gaps when the contract expires and the data "rolls" to the next month.

**The Pivot** Initially, I treated WTI like a stock index. I quickly found that looking at a non-adjusted continuous chart created false breakout signals every 20th of the month due to the expiry roll. **Rationale:** To get a clean signal, I needed to engineer a "Continuous Contract" that mimics the actual behavior of a trader rolling their position based on liquidity, not just the calendar.

## 2. Adapting the Code to Market Realities (Evolution of Logic)

The core value of this code lies in how it handles the transition between contracts to preserve data integrity.

### A. The "Expiration Crush" & Liquidity Rolling

My first iteration rolled contracts on the very last day of trading.

**The Mistake:** In the last 3 days of a WTI contract, price action decouples from global fundamentals due to "Physical Convergence" (traders with no storage capacity scrambling to close positions).

**Realization:** Historical data shows that Open Interest and Volume typically crossover from M1 to M2 between T-5 and T-4 days prior to expiration.

**The Fix:** I implemented a Volume-Based Roll logic. The code monitors the volume of M1 vs M2. When M2 volume exceeds M1, the algorithm switches the active contract. This filters out the erratic volatility of the "delivery window."

### B. Signal Normalization (The Z-Score)

Looking at the spread in dollars (e.g., "$1.00 backwardation") is misleading over a 5-year period due to volatility regimes.

**Observation:** A $0.50 spread in a low-volatility year (like 2019, where spreads oscillated in a tight **±$0.30 range**) is a scream for barrels. The same $0.50 in a war year (like March 2022, where spreads exploded to >$3.00/bbl) is meaningless noise.

**Correction:** I integrated a Rolling Z-Score (Standard Deviation) calculation.

**The "Merchant" View:** Instead of trading the price, this tool flags "2-Sigma Events". If the Z-Score hits +2, it statistically confirms that the market is over-extended in tightness, regardless of the nominal price of oil.

### C. Construction of the Continuous Series

The script does not rely on pre-built "Continuous" tickers (like CL1! on TradingView) which often smooth data aggressively.

**Methodology:** The CL_futures_dwnld.py script downloads individual monthly contracts (e.g., CLN2020, CLQ2020) separately.

**Stitching:** The spreads.py module stitches them together using the rollout dates defined in step A. This grants total control over the "Splice" method, ensuring that a spike in backwardation is real and not an artifact of bad data stitching.

## 3. Technical Implementation

This project focuses on data engineering and time-series manipulation.

- **Stack:** Python, Pandas, Matplotlib.

- **Architecture:**

  - **Data Ingestion:** Downloads individual contract CSVs to avoid large memory loads.

  - **Splicing Engine:** A loop structure that iterates through contract expiry dates to build a seamless dataset.

- **Visualization:**

  - Plots the Raw Spread (Orange line).

  - Overlays Anomaly Bands (Red/Blue dots) triggered by Z-Score breakouts (> 2 or < -2), offering an instant visual backtest of extreme market conditions.
