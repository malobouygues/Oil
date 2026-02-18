# WTI M1/M2 Rolling Spread

## Project Overview

The project quantifies the economic viability of physical storage arbitrage (Cash-and-Carry) and to monitor the transition between backwardation (positive roll yield) and contango (storage cost incentives)

## Methodology

- Liquidity-adjusted roll: Dynamic transition from Front-Month (M<sub>1</sub>) to Second-Month (M<sub>2</sub>) triggered by Daily Volume Crossover (V<sub>M2</sub> > V<sub>M1</sub>)

- Physical convergence filter: Pre-empts Last Trading Day (LTD) volatility (typically rolling T−7 to T−3) to exclude price decoupling driven by Cushing logistical bottlenecks rather than global supply/demand

## Benchmarks

**WTI Light Sweet Crude Oil**

- Benchmark: West Texas Intermediate (WTI)
- Instrument: NYMEX/CME Light Sweet Crude Oil Futures (CL)
- Logic: Dynamic front month (M<sub>1</sub>) vs second month (M<sub>2</sub>) based on volume crossover (V<sub>M2</sub> > V<sub>M1</sub>)

source: https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.html

## Mathematical Model

The continuous spread series S<sub>t</sub> is derived from the term structure of futures prices P

### Variable Definitions

- t: Current time step (daily resolution)
- P<sub>t,n</sub>: Settlement price of the n-th nearby futures contract at time t
- V<sub>t,n</sub>: Daily trading volume of the n-th nearby futures contract at time t
- M<sub>1</sub>: Front-month contract index
- M<sub>2</sub>: Second-month contract index

### Roll Logic

The active contract pair transitions when liquidity shifts to the deferred expiry. The roll condition R<sub>t</sub> is defined as a boolean trigger:

```
R_t = { 1  if V_t,M2 > V_t,M1
      { 0  otherwise
```

### Spread Calculation

The calendar spread S<sub>t</sub> represents the cost of carry (or scarcity premium)

**S<sub>t</sub> = P<sub>t,M1</sub> − P<sub>t,M2</sub>**

Where P<sub>t,M1</sub> and P<sub>t,M2</sub> are the prices of the currently active pair determined by the roll logic state

### Statistical Bounds (Bollinger Bands)

To identify mean reversion or breakout signals in the spread term structure, volatility bands are calculated:

- BB<sub>upper,t</sub> = μ<sub>t</sub> + k·σ<sub>t</sub>
- BB<sub>lower,t</sub> = μ<sub>t</sub> − k·σ<sub>t</sub>

Where:

- μ<sub>t</sub>: Rolling Simple Moving Average (SMA) of S<sub>t</sub> over window w
- σ<sub>t</sub>: Rolling Standard Deviation of S<sub>t</sub> over window w
- k: Number of standard deviations (typically k=2)

## Technical Architecture

- Python 3.9+
- Data: tvDatafeed (TradingView API)
- Libraries: Pandas, Numpy, Matplotlib