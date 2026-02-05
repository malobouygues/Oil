# WTI M1/M2 Rolling Spread

This project builds a continuous, adjusted time-series of the WTI M1/M2 Spread to isolate short-term physical scarcity signals from expiration noise.

**Objective:** To put in perspective the magnitude of WTI M1/M2 spread current backwardation / contango events against historical prices

## 1. Context & Rationale

While the Forward Curve (Project n°1) gives a snapshot, I wanted to find out whether the M1-M2 oil spread is cycle. The M1/M2 Spread (front month vs second month) is crucial in the physical market

**Problem** Raw futures data is fragmented. You cannot simply download "Generic 1st Month Crude" without encountering massive price gaps when the contract expires and the data "rolls" to the next month.

**Pivot** Initially, I treated WTI like a stock index. I quickly found that looking at a non-adjusted continuous chart created false breakout signals every 20th of the month due to the expiry roll. **Rationale:** To get a clean signal, I needed to engineer a "Continuous Contract" that mimics the actual behavior of a trader rolling their position based on liquidity, not just the calendar.

## 2. Building the Model (How My Thinking Evolved)

The core value of this code lies in how it handles the transition between contracts to preserve data integrity.

### A. Rolling Contrat Challenge

My first version rolled contracts on the very last day of trading, but price action decouples from global fundamentals due to physical convergence

**Idea:** Historical data shows that Open Interest and Volume typically crossover from M1 to M2 between T-6/7 and T-3 days prior to expiration

**Solution:** I used a volume roll logic; when M2 volume > M1, it switches the active contract only when:

```
Volume(Next) > Volume(Front)
```

### B. Construction of the Continuous Series

The script does not rely on continuous tickers (like CL1! on TradingView) which often smooth data

**Methodology:** cl_futures.py script downloads individual monthly contracts (ie. CLN2020, CLQ2020)

spreads.py link them together using the rollout dates -> hence, a movement in price is not the consequence of low volatility and physical obligation

## 3. Technical Stack

- **Language**: Python 3.9+
- **Data**: tvDatafeed (TradingView API)
- **Core Libraries**:
  - Loop that iterates through contract volumes at expiration, look for M2 Volume > M1 Volume (T-5 to T-10 days pre expiry)
  - **Matplotlib:** bollinger bands (rolling mean ± 2 std dev) to visualize breakout zones
- **Data**: Local CSV serialization with ISO dates