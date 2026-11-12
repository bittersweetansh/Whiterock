import MetaTrader5 as mt5
import pandas as pd
from pathlib import Path

# Project directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Initial Whiterock research universe
SYMBOLS = [
    "ALUMINIUM",
    "COPPER",
    "NICKEL",
    "LEAD"
]

TIMEFRAME = mt5.TIMEFRAME_D1
NUMBER_OF_CANDLES = 1000


def connect_mt5():
    """Connect Python to the running MT5 terminal."""

    if not mt5.initialize():
        raise RuntimeError(
            f"MT5 initialization failed: {mt5.last_error()}"
        )

    print("Connected to MetaTrader 5")


def fetch_historical_data(symbol):
    """Retrieve historical daily price data for one metal."""

    if not mt5.symbol_select(symbol, True):
        print(f"Could not select {symbol}")
        return None

    rates = mt5.copy_rates_from_pos(
        symbol,
        TIMEFRAME,
        1,
        NUMBER_OF_CANDLES
    )

    if rates is None or len(rates) == 0:
        print(f"No historical data for {symbol}")
        print("MT5 error:", mt5.last_error())
        return None

    df = pd.DataFrame(rates)

    df["time"] = pd.to_datetime(
        df["time"],
        unit="s",
        utc=True
    )

    df = df.rename(columns={
        "time": "date",
        "tick_volume": "tick_volume"
    })

    columns = [
        "date",
        "open",
        "high",
        "low",
        "close",
        "tick_volume",
        "spread",
        "real_volume"
    ]

    df = df[columns]

    output_file = RAW_DATA_DIR / f"{symbol.lower()}.csv"

    df.to_csv(output_file, index=False)

    print(f"\n{symbol}")
    print("Records:", len(df))
    print("Start:", df["date"].min())
    print("End:", df["date"].max())
    print("Saved:", output_file)

    return df


def main():

    try:
        connect_mt5()

        for symbol in SYMBOLS:
            fetch_historical_data(symbol)

    finally:
        mt5.shutdown()
        print("\nMT5 connection closed")


if __name__ == "__main__":
    main()
