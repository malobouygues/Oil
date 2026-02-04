# Oil Folder

A portfolio of tools designed to analyze the WTI/Brent complex through the lens of a physical operator, focusing on Structure, Scarcity, and Logistics.

## 📂 Term Structure & Roll Yield

**The Question**: Is the market structure incentivizing storage (Contango) or demanding immediate inventory release (Backwardation)?

**Objective**: To visualize the WTI Forward Curve dynamics. This tool moves beyond "Flat Price" to calculate the Implied Roll Yield, identifying the inventory incentives that drive physical flows at the Cushing hub.

## 📂 M1/M2 Time Spread & Scarcity

**The Question**: Is the current physical tightness historically extreme (a 2-sigma event) or just nominal noise?

**Objective**: To model the WTI Prompt Spread (M1-M2) using a volume-based rolling algorithm. It applies Z-Score normalization to filter out volatility regimes and statistically confirm "Black Swan" scarcity signals (e.g., War, Pipeline outages).

## 📂 Transatlantic Arbitrage (Brent/WTI)

**The Question**: Is the Arb Window open to ship US Crude to Europe after accounting for Freight volatility?

**Objective**: To calculate the theoretical Netback for US exports. This tool adjusts the raw Brent-WTI spread by real-time Freight Costs to visualize the true economic incentive for moving barrels from the US Gulf Coast to Rotterdam.
