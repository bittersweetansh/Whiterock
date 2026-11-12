
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = ROOT / "data" / "processed"

METALS = ["aluminium", "copper", "nickel", "lead"]

LOOKBACK = 60
TRADING_DAYS = 252
RISK_FREE_RATE = 0.0


def load_returns():

    datasets = []

    for metal in METALS:

        df = pd.read_csv(RAW_DIR / f"{metal}.csv")

        df["date"] = pd.to_datetime(
            df["date"], utc=True
        )

        df = df[["date", "close"]].rename(
            columns={"close": metal}
        )

        datasets.append(df)

    prices = datasets[0]

    for dataset in datasets[1:]:

        prices = prices.merge(
            dataset,
            on="date",
            how="inner",
            validate="one_to_one"
        )

    prices = prices.sort_values("date")
    prices = prices.set_index("date")

    returns = prices[METALS].pct_change(
        fill_method=None
    ).dropna()

    return returns


def calculate_metrics(returns):

    wealth = (1 + returns).cumprod()

    years = (
        (returns.index[-1] - returns.index[0]).total_seconds()
        / (365.25 * 24 * 60 * 60)
    )

    cagr = wealth.iloc[-1] ** (1 / years) - 1

    volatility = (
        returns.std() * np.sqrt(TRADING_DAYS)
    )

    drawdown = wealth / wealth.cummax() - 1

    excess_returns = returns - (
        (1 + RISK_FREE_RATE) ** (1 / TRADING_DAYS) - 1
    )

    sharpe = (
        excess_returns.mean() / returns.std()
    ) * np.sqrt(TRADING_DAYS)

    return {
        "Total Return": wealth.iloc[-1] - 1,
        "CAGR": cagr,
        "Volatility": volatility,
        "Sharpe": sharpe,
        "Max Drawdown": drawdown.min()
    }


def main():

    returns = load_returns()

    # Equal-weight strategy
    equal_weights = pd.DataFrame(
        1 / len(METALS),
        index=returns.index,
        columns=METALS
    )

    equal_portfolio_returns = (
        returns * equal_weights
    ).sum(axis=1)

    # Calculate historical rolling volatility.
    # Shift by one day to prevent look-ahead bias.
    rolling_volatility = (
        returns.rolling(
            window=LOOKBACK,
            min_periods=LOOKBACK
        ).std() * np.sqrt(TRADING_DAYS)
    ).shift(1)

    # Inverse-volatility allocation
    inverse_volatility = 1 / rolling_volatility

    inverse_weights = inverse_volatility.div(
        inverse_volatility.sum(axis=1),
        axis=0
    )

    # Apply weights to the following day's returns
    inverse_portfolio_returns = (
        returns * inverse_weights
    ).sum(axis=1)

    # Use identical evaluation dates
    valid_dates = inverse_portfolio_returns.dropna().index

    equal_portfolio_returns = (
        equal_portfolio_returns.loc[valid_dates]
    )

    inverse_portfolio_returns = (
        inverse_portfolio_returns.loc[valid_dates]
    )

    # Performance comparison
    results = pd.DataFrame({
        "Equal Weight": calculate_metrics(
            equal_portfolio_returns
        ),
        "Rolling Inverse Volatility": calculate_metrics(
            inverse_portfolio_returns
        )
    }).T

    print("\nROLLING ALLOCATION BACKTEST")
    print("=" * 60)

    print("Volatility lookback:", LOOKBACK, "trading days")
    print("Evaluation start:", valid_dates[0])
    print("Evaluation end:", valid_dates[-1])
    print("Observations:", len(valid_dates))

    print("\nPERFORMANCE")
    print(results.round(4))

    print("\nLATEST INVERSE-VOLATILITY WEIGHTS")

    print(
        inverse_weights.loc[valid_dates[-1]].round(4)
    )

    # Export results
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    comparison_file = (
        OUTPUT_DIR / "rolling_allocation_comparison.csv"
    )

    results.to_csv(comparison_file)

    weights_file = (
        OUTPUT_DIR / "rolling_inverse_volatility_weights.csv"
    )

    inverse_weights.loc[valid_dates].to_csv(weights_file)

    print("\nSaved performance:", comparison_file)
    print("Saved weights:", weights_file)


if __name__ == "__main__":
    main()
