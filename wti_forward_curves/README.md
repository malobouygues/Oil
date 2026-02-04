# WTI Term Structure and Roll Yield Analysis

This project monitors the WTI Crude Oil (NYMEX) Forward Curve to extract fundamental supply/demand signals.

**Objective:** To answer the critical question for physical inventory management: Is the market incentivizing storage (Contango) or demanding immediate release of barrels (Backwardation)?

## 1. Context & Rationale

Retail traders often obsess over "Flat Price" (e.g., "$75/bbl"). However, for a physical operator or a refinery, the spot price is often noise driven by geopolitical headlines. The real fundamental signal lies in the shape of the curve.

**The Objective** I wanted to build a dashboard that ignores the noise of daily price fluctuation to focus on the structure.

- **Contango:** The market pays you to store oil.
- **Backwardation:** The market charges you a premium to hold oil (or pays you to sell it now).

**The Pivot** Initially, I looked at the curve visually. I realized this was insufficient. A visual "steepness" is subjective. I needed to quantify the Roll Yield—the theoretical P&L of holding a position as contracts roll closer to expiry.

## 2. Adapting the Code to Market Realities (Evolution of Logic)

My focus shifted from simple price plotting to calculating the implied yield of the curve. This required handling the specific mathematical and operational nuances of energy futures.

### A. The "Dollar Bias" (Normalization)

My first iteration calculated the spread in absolute dollars (Month 1 - Month 2).

**The Problem:** A $0.50 spread is structurally significant when Oil is at $40/bbl (1.25%), but negligible when Oil is at $100/bbl (0.5%). High-price environments were distorting the signal.

**The Fix:** I refactored the logic to calculate Percentage Roll Yield.

```
Yield = (Price_Front - Price_Next) / Price_Front
```

**Result:** This standardizes the signal across different price regimes, allowing for a fair historical comparison of market tightness.

### B. Interpreting the Signal (Merchant Logic)

The code distinguishes two market states based on the calculated yield:

- **Positive Yield (Backwardation):** Front > Next. This is a scarcity signal. The market is "tight" and penalizes anyone holding inventory. It signals immediate physical demand.

- **Negative Yield (Contango):** Front < Next. This is an oversupply signal. The negative yield represents the "Cost of Carry" (Storage + Finance + Insurance). If the Contango is deep enough, it opens the "Cash & Carry" arbitrage window.

### C. Operational Safety: Dynamic "Front Month" Logic

Unlike stocks, oil contracts expire monthly. Hardcoding tickers (e.g., CLZ2025) guarantees the code will break or analyze expired data.

**The Risk:** Analyzing a contract that has entered the delivery period or has zero liquidity.

**The Solution:** The script (CL_futures_dwnld.py) implements a Rolling Window. It dynamically generates the ticker symbols for the next 12 months based on the current system date.

**Impact:** This ensures the "Front Month" (M1) is always the liquid, active contract, mirroring the execution reality of a trader rolling positions.

## 3. Technical Implementation

This tool focuses on efficient data serialization and clear visualization of the term structure.

- **Language:** Python 3.9+

- **Data Acquisition:** tvDatafeed (TradingView API).

  **Reasoning:** NYMEX data is expensive. This wrapper allows access to delayed futures data sufficient for End-of-Day curve construction without scraping errors.

- **Core Libraries:**

  - **Pandas:** Used for time-series alignment and vectorizing the yield calculation across the curve.

  - **Matplotlib:** Dual-plot visualization (Curve Shape vs. Bar Chart Yields) to correlate price levels with structural incentives.

- **Architecture:** Modular design separating the data fetcher (dwnld), the calculation engine (curves.py), and the visualization (main.py).
