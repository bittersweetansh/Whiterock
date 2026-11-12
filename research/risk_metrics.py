
import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INDEX_FILE = PROJECT_ROOT / "data" / "processed" / "whiterock_index.csv"

TRADING_DAYS = 252
RISK_FREE_RATE = 0.0


def calculate_metrics(df, price_column):

    prices = df[price_column].dropna()

    daily_returns = prices.pct_change().dropna()

    # Total return
    total_return = (prices.iloc[-1] / prices.iloc[0]) - 1

    # CAGR using actual calendar duration
    years = (
        df["date"].iloc[-1] - df["date"].iloc[0]
    ).total_seconds() / (365.25 * 24 * 60 * 60)

    cagr = (prices.iloc[-1] / prices.iloc[0]) ** (1 / years) - 1

    # Annualised volatility
    volatility = daily_returns.std() * np.sqrt(TRADING_DAYS)

    # Maximum drawdown
    running_peak = prices.cummax()
    drawdowns = (prices / running_peak) - 1
    max_drawdown = drawdowns.min()

    # Sharpe ratio
    annual_risk_free_daily = (
        (1 + RISK_FREE_RATE) ** (1 / TRADING_DAYS) - 1
    )

    excess_returns = daily_returns - annual_risk_free_daily

    if daily_returns.std() == 0:
        sharpe = np.nan
    else:
        sharpe = (
            excess_returns.mean() / daily_returns.std()
        ) * np.sqrt(TRADING_DAYS)

    # Best and worst daily returns
    best_day = daily_returns.max()
    worst_day = daily_returns.min()

    return {
        "Total Return": total_return,
        "CAGR": cagr,
        "Annualised Volatility": volatility,
        "Maximum Drawdown": max_drawdown,
        "Sharpe Ratio": sharpe,
        "Best Day": best_day,
        "Worst Day": worst_day
    }


def main():

    df = pd.read_csv(INDEX_FILE)

    df["date"] = pd.to_datetime(
        df["date"], utc=True
    )

    df = df.sort_values("date").reset_index(drop=True)

    metrics = calculate_metrics(df, "whiterock_index")

    print("\n" + "=" * 55)
    print("WHITEROCK RISK AND PERFORMANCE ANALYSIS")
    print("=" * 55)

    print("\nINDEX PERFORMANCE")

    for metric, value in metrics.items():

        if metric == "Sharpe Ratio":
            print(f"{metric}: {value:.3f}")
        else:
            print(f"{metric}: {value:.2%}")

    # Save index drawdown history
    df["running_peak"] = df["whiterock_index"].cummax()

    df["drawdown"] = (
        df["whiterock_index"] / df["running_peak"]
    ) - 1

    output_file = (
        PROJECT_ROOT / "data" / "processed" /
        "whiterock_risk_analysis.csv"
    )

    df.to_csv(output_file, index=False)

    print("\nSaved risk history:", output_file)


if __name__ == "__main__":
    main()
