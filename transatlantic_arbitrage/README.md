# Brent/WTI Transatlantic Arbitrage Model

This project models the "Arb Window" between the two global crude benchmarks: Brent (North Sea) and WTI (US). It moves beyond simple correlation analysis to calculate the Theoretical Netback, factoring in the cost of freight to determine the physical flow of barrels.

**Objective:** To visualize the economic incentive for US Crude exports to Europe. Is the spread wide enough to cover the shipping cost, or is the Transatlantic arbitrage closed?

## 1. Context & Rationale

Since the lifting of the US Crude Export Ban in December 2015, WTI has ceased to be a landlocked domestic asset and has become a global competitor to Brent. However, looking at the raw spread (e.g., "Brent is trading $4 premium to WTI") is misleading for a physical operator.

**The Question** Can I buy a barrel in Cushing, pipe it to the Gulf Coast, ship it to Rotterdam, and still make a margin against the local Brent price?

**The Pivot** Initially, I monitored the raw Brent - WTI spread. I realized this created false positive signals.

**Why?** A $4.00 spread looks lucrative, but if VLCC (Very Large Crude Carrier) freight rates skyrocket to $5.50/bbl (as seen during the 2022 energy crisis), the trade is actually a loss maker.

**Rationale:** The critical metric is not the spread, but the Arb Incentive (Spread minus Freight).

## 2. Adapting the Code to Market Realities (Evolution of Logic)

The logic of this tool is built around the "Cost to Deliver" concept.

### A. The Structural Relationship (The Benchmarks)

I selected Brent (UKOIL) and WTI (USOIL) as the inputs.

- **Brent:** The price setter for the Atlantic Basin (Europe/Africa).

- **WTI:** The source of marginal supply.

**The Logic:** When the Arb is Open (Green zone in the chart), US crude floods Europe, capping Brent upside. When the Arb is Closed (Red zone), US crude is trapped domestically, typically forcing WTI lower to clear the glut.

### B. Integrating the "Invisible" Cost (Freight)

My initial model ignored logistics.

**The Mistake:** Assuming the spread is pure profit.

**Realization:** Physical arbitrage is a function of shipping rates. A wide spread is often just a reflection of expensive freight (the market pricing in the transport cost).

**The Fix:** I introduced a FREIGHT_COST variable in config.py.

**Implementation:** Arb_Incentive = (Brent - WTI) - Freight.

**Value:** Currently set to $3.00/bbl, representing a standardized proxy for USGC (US Gulf Coast) to ARA (Amsterdam-Rotterdam-Antwerp) shipping costs on an Aframax/Suezmax vessel.

**Impact:** This creates a "Zero Line" hard threshold. Positive values indicate a physical "Go" signal; negative values indicate the trade is uneconomic.

### C. Visualizing the "Arb Window"

Instead of a simple line chart, the visualization (main.py) uses a fill_between logic to distinctively highlight market regimes:

- **Green Zone (Arb Open):** The spread > Freight. US exporters are active. Expect WTI to strengthen relative to Brent as inventory draws down.

- **Red Zone (Arb Closed):** The spread < Freight. The US is priced out of the export market. Expect WTI to weaken as domestic storage fills up.

## 3. Technical Implementation

This project separates configuration from logic to allow for scenario analysis.

- **Stack:** Python, Pandas, Matplotlib.

- **Architecture:**

  - **config.py:** Centralizes the FREIGHT_COST variable. This allows the user to stress-test the arb against rising shipping rates (e.g., simulating a spike to $6.00/bbl) without rewriting the core code.

  - **data_loader.py:** Fetches distinct time series for UKOIL and USOIL and merges them on a common datetime index to prevent misalignment.

  - **Vectorized Logic:** The arbitrage calculation is performed on the entire dataframe instantly, creating a dynamic boolean mask (Arb_Open) for visualization.
