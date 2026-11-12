
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = ROOT / "data" / "processed"

METALS = ["aluminium", "copper", "nickel", "lead"]
TRADING_DAYS = 252


def load_returns():

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

    prices = prices.sort_values("date").reset_index(drop=True)

    returns = prices.set_index("date")[METALS].pct_change(
        fill_method=None
    ).dropna()

    return returns


def performance_stats(portfolio_returns):

    wealth = (1 + portfolio_returns).cumprod()

    years = len(portfolio_returns) / TRADING_DAYS

    cagr = wealth.iloc[-1] ** (1 / years) - 1

    volatility = (
        portfolio_returns.std() * np.sqrt(TRADING_DAYS)
    )

    drawdown = wealth / wealth.cummax() - 1

    sharpe = (
        portfolio_returns.mean() /
        portfolio_returns.std()
    ) * np.sqrt(TRADING_DAYS)

    return {
        "CAGR": cagr,
        "Volatility": volatility,
        "Sharpe": sharpe,
        "Max Drawdown": drawdown.min()
    }


def main():

    returns = load_returns()

    # Strategy 1: Equal weights
    equal_weights = pd.Series(
        1 / len(METALS),
        index=METALS
    )

    equal_returns = returns @ equal_weights

    # Strategy 2: Inverse volatility weights
    volatility = returns.std() * np.sqrt(TRADING_DAYS)

    inverse_vol = 1 / volatility

    inverse_weights = inverse_vol / inverse_vol.sum()

    inverse_returns = returns @ inverse_weights

    # Compare strategies
    results = {
        "Equal Weight": performance_stats(equal_returns),
        "Inverse Volatility": performance_stats(inverse_returns)
    }

    comparison = pd.DataFrame(results).T

    print("\nALLOCATION STRATEGY COMPARISON")
    print("=" * 60)

    print("\nWeights:")

    print(pd.DataFrame({
        "Equal Weight": equal_weights,
        "Inverse Volatility": inverse_weights
    }).round(4))

    print("\nPerformance:")

    print(comparison.round(4))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    comparison.to_csv(
        OUTPUT_DIR / "allocation_comparison.csv"
    )

    print("\nSaved allocation comparison.")


if __name__ == "__main__":
    main()
