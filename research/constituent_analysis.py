
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = ROOT / "data" / "processed"

METALS = ["aluminium", "copper", "nickel", "lead"]

TRADING_DAYS = 252


def load_prices():

    datasets = []

    for metal in METALS:

        df = pd.read_csv(RAW_DIR / f"{metal}.csv")

        df["date"] = pd.to_datetime(df["date"], utc=True)

        df = df[["date", "close"]].rename(
            columns={"close": metal}
        )

        datasets.append(df)

    prices = datasets[0]

    for df in datasets[1:]:
        prices = prices.merge(
            df,
            on="date",
            how="inner",
            validate="one_to_one"
        )

    return prices.sort_values("date").reset_index(drop=True)


def analyse_metal(prices, metal):

    series = prices[metal]
    returns = series.pct_change().dropna()

    years = (
        prices["date"].iloc[-1] -
        prices["date"].iloc[0]
    ).total_seconds() / (365.25 * 24 * 60 * 60)

    total_return = series.iloc[-1] / series.iloc[0] - 1

    cagr = (
        (series.iloc[-1] / series.iloc[0]) ** (1 / years)
    ) - 1

    volatility = returns.std() * np.sqrt(TRADING_DAYS)

    drawdown = series / series.cummax() - 1

    return {
        "Metal": metal.title(),
        "Total Return": total_return,
        "CAGR": cagr,
        "Annualised Volatility": volatility,
        "Maximum Drawdown": drawdown.min(),
        "Best Day": returns.max(),
        "Worst Day": returns.min()
    }


def main():

    prices = load_prices()

    results = []

    for metal in METALS:
        results.append(analyse_metal(prices, metal))

    summary = pd.DataFrame(results)

    returns = prices[METALS].pct_change(fill_method=None)

    correlation = returns.corr()

    summary.to_csv(
        OUTPUT_DIR / "constituent_metrics.csv",
        index=False
    )

    correlation.to_csv(
        OUTPUT_DIR / "metal_correlations.csv"
    )

    print("\nINDIVIDUAL METAL PERFORMANCE")
    print(
        summary.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}"
        )
    )

    print("\nMETAL CORRELATION MATRIX")
    print(correlation.round(3))

    print("\nAnalysis saved successfully.")


if __name__ == "__main__":
    main()
