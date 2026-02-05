# WTI Futures Term Structure Analysis

**Objective:** To quantify the economic incentive for storage (contango) or depletion (backwardation), by analyzing the WTI Term Structure.

## 1. Context & Rationale

The spot price is often noise driven by geopolitical headlines, while the real fundamental signal lies in the shape of the curve.

**The Objective** I wanted to isolate the noise of daily price fluctuation to focus on the structure; to see what narriative the market is pricing today.

- **Contango:** The market pays you to store oil.
- **Backwardation:** The market charges you a premium to hold oil (or pays you to sell it now).

**** Initially, I looked at the curve visually. I realized this was insufficient. A visual "steepness" is subjective. I needed to quantify the Roll Yield—the theoretical P&L of holding a position as contracts roll closer to expiry.

## 2. Building the Model (How My Thinking Evolved)

My focus shifted from simple price plotting to calculating the implied yield of the curve. This required handling the specific mathematical and operational nuances of energy futures.

## 3. Instrument Specifications

The model isolates the "Cash & Carry" signal by tracking the spread between the two most liquid maturities on the curve.

- **Leg 1: The Spot Proxy (M1)**
  
  Represents the immediate physical tightness of the market.
  
  **Benchmark:** West Texas Intermediate (WTI) Light Sweet Crude Oil.
  **Delivery:** FOB at Cushing, Oklahoma (Pipeline & Storage Hub).
  **Sulfur:** < 0.42% by weight (Sweet).
  **Instrument:** CME Group (NYMEX) WTI Crude Oil Futures (CL).
  
- **Leg 2: The Storage Proxy (M2)**
  
  Represents the future value of the barrel. Used to calculate the market's implied cost of carry.
  
  **Logic:** If M2 > M1 (Contango), the market pays for storage.
  **Data Logic:** Dynamic rolling ticker (e.g., if M1 is `CLZ25`, M2 is automatically `CLF26`).
  **Exchange:** NYMEX (New York Mercantile Exchange).

**Source:** CME Group (Physical Contract Specs)

https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.contractSpecs.html

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
