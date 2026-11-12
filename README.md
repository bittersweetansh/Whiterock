# Whiterock — Industrial Metals Quantitative Research

**A quantitative research prototype for a diversified industrial metals index.**

Whiterock is an early-stage financial technology project exploring the construction and analysis of a diversified basket of industrial metals.

## Current Research Basket

The initial research basket consists of:

- Aluminium — 25%
- Copper — 25%
- Nickel — 25%
- Lead — 25%

Iron ore is reserved for a future expansion phase.

## Current Capabilities

- Historical commodity price extraction through MetaTrader 5.
- Daily OHLC data processing.
- Historical data validation.
- Equal-weighted four-metal index calculation.
- Index performance visualisation.
- Volatility and drawdown analysis.
- Constituent correlation analysis.
- Performance attribution.
- Rolling inverse-volatility allocation backtesting.

## Preliminary Research Results

Research period: May 2023 – November 2026.

| Metric                                  | Preliminary result |
| --------------------------------------- | -----------------: |
| Equal-weight index cumulative return    |             12.68% |
| Equal-weight index CAGR                 |              3.46% |
| Annualised volatility                   |             15.08% |
| Maximum drawdown                        |            -21.92% |
| Rolling inverse-volatility CAGR         |              4.41% |
| Rolling inverse-volatility Sharpe ratio |             0.3825 |

These figures are preliminary results from the current research implementation, not audited investment performance.

## Technology Stack

- Python
- MetaTrader 5 Python API
- Pandas
- NumPy
- Matplotlib

## Project Status

**Version 0.1.0 — Research Prototype**

The project is under active development. Benchmark verification, transaction-cost modelling, out-of-sample testing, and further index methodology research remain outstanding.

## Important Disclaimer

Whiterock is currently a quantitative research project, not an operational investment product, regulated fund, ETF or tokenised security.

Historical results are based on instruments available through a MetaTrader 5 demonstration environment. Their correspondence to exchange-traded commodity benchmarks has not yet been independently established.

Nothing in this repository constitutes investment advice or an offer to invest.
