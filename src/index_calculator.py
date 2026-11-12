
import pandas as pd
from pathlib import Path

# Project directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Initial research constituents
SYMBOLS = [
    "aluminium",
    "copper",
    "nickel",
    "lead"
]

WEIGHTS = {
    "aluminium": 0.25,
    "copper": 0.25,
    "nickel": 0.25,
    "lead": 0.25
}

BASE_VALUE = 1000


def load_data():

    datasets = []

    for symbol in SYMBOLS:

        file_path = RAW_DATA_DIR / f"{symbol}.csv"

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        df = pd.read_csv(file_path)

        df["date"] = pd.to_datetime(
            df["date"], utc=True
        )

        df = df[["date", "close"]].copy()

        df = df.rename(columns={
            "close": symbol
        })

        datasets.append(df)

    return datasets


def calculate_index():

    datasets = load_data()

    # Merge all four price series by date
    prices = datasets[0]

    for dataset in datasets[1:]:
        prices = prices.merge(
            dataset,
            on="date",
            how="inner",
            validate="one_to_one"
        )

    prices = prices.sort_values("date").reset_index(drop=True)

    if prices.empty:
        raise ValueError("No common dates found.")

    # Check for invalid closing prices
    if prices[SYMBOLS].isna().any().any():
        raise ValueError("Missing closing prices detected.")

    if (prices[SYMBOLS] <= 0).any().any():
        raise ValueError("Non-positive closing prices detected.")

    # First common date becomes the base date
    base_prices = prices.iloc[0][SYMBOLS]

    # Calculate each metal's price relative
    for symbol in SYMBOLS:

        prices[f"{symbol}_relative"] = (
            prices[symbol] / base_prices[symbol]
        )

    # Calculate weighted index
    prices["whiterock_index"] = sum(
        prices[f"{symbol}_relative"] * WEIGHTS[symbol]
        for symbol in SYMBOLS
    ) * BASE_VALUE

    # Calculate daily index returns
    prices["daily_return_pct"] = (
        prices["whiterock_index"].pct_change() * 100
    )

    # Export results
    output_file = PROCESSED_DIR / "whiterock_index.csv"

    prices.to_csv(output_file, index=False)

    # Summary
    first_value = prices["whiterock_index"].iloc[0]
    last_value = prices["whiterock_index"].iloc[-1]

    total_return = (
        (last_value / first_value) - 1
    ) * 100

    print("\n" + "=" * 50)
    print("WHITEROCK RESEARCH INDEX")
    print("=" * 50)

    print("Constituents:", len(SYMBOLS))
    print("Observations:", len(prices))
    print("Base date:", prices["date"].iloc[0])
    print("Latest date:", prices["date"].iloc[-1])

    print(f"Base index: {first_value:.2f}")
    print(f"Latest index: {last_value:.2f}")
    print(f"Total price return: {total_return:.2f}%")

    print("\nConstituent weights:")

    for symbol, weight in WEIGHTS.items():
        print(f"{symbol.title()}: {weight:.0%}")

    print("\nSaved:", output_file)

    print("\nLatest index observations:")
    print(
        prices[
            ["date", "whiterock_index", "daily_return_pct"]
        ].tail().to_string(index=False)
    )


if __name__ == "__main__":
    calculate_index()
