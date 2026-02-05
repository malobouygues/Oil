# WTI Futures Term Structure Analysis

**Question:** Does the forward curve implied yield incentivize storage (contango) or destocking (backwardation)?

## 1. Context & Rationale

The spot price is often noise driven by geopolitical headlines, while the real fundamental signal lies in the shape of the curve.

**The Objective** I wanted to isolate the noise of daily price fluctuation to focus on the structure; to see what narriative the market is pricing today.

- **Contango:** The market pays you to store oil.
- **Backwardation:** The market charges you a premium to hold oil (or pays you to sell it now).

**** Initially, I looked at the curve visually. I realized this was insufficient. A visual "steepness" is subjective. I needed to quantify the Roll Yield—the theoretical P&L of holding a position as contracts roll closer to expiry.

## 2. Building the Model (How My Thinking Evolved)

My focus shifted from simple price plotting to calculating the implied yield of the curve. This required handling the specific mathematical and operational nuances of energy futures.

### A. Physical Futures Specs

I used the CME Group Light Sweet Crude Oil contract:

- West Texas Intermediate (WTI), FOB Cushing, Oklahoma
- Ticker: CL
- Exchange: NYMEX (New York Mercantile Exchange)

https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.contractSpecs.html

**Logic:** Dynamic rolling ticker (if M1 is `CLZ2025`, M2 is automatically `CLF2026` the last quoted date)

### B. The Dollar Normalization

My first version calculated the spread in absolute dollars (Month 1 - Month 2).

**Problem:** $0.50 spread is structurally significant when Oil is at $40/bbl (1.25%), but negligible when Oil is at $100/bbl (0.5%) -> ie. high price environments distort the signal

**Solution:** I refactored the logic to calculate Roll Yield in percentage

```
Yield = (Price_Front - Price_Next) / Price_Front
```

**Result:** It gives fair historical comparison of market tightness.

### C. Interpretation

- **Positive yield (backwardation):** front > next, ie. the market is tight and signals immediate physical demand

- **Negative yield (contango):** front < next, the negative yield represents the cost of carry (case of contango deep enough, it opens a cash & carry arbitrage window appears)

### D. Delivery Risk (Front Month Logic)

Hardcoding tickers (ie. fixed CLZ2025) guarantees the code will break or analyze expired data

**Risk:** To analyze a contract that has entered the delivery period or has zero liquidity

**Solution:** I coded a rolling window algorithm: it dynamically generates the ticker symbols for the next 12 months based on the current date

Front month (M1) is always the liquid, active contract, mirroring the execution reality of a rolling position.

## 3. Technical Stack

- **Language**: Python 3.9+
- **Data**: tvDatafeed (TradingView API)
- **Core Libraries**:
  - **Pandas**: Used for time-series alignment and vectorizing the yield calculation across the curve
  - **Matplotlib:** Dual-plot visualization (curve and bar chart)
- **Data**: Local CSV serialization with ISO dates