
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

SYMBOLS = [
    "aluminium",
    "copper",
    "nickel",
    "lead"
]

REQUIRED_COLUMNS = [
    "date",
    "open",
    "high",
    "low",
    "close"
]


def validate_file(symbol):

    file_path = RAW_DATA_DIR / f"{symbol}.csv"

    print("\n" + "=" * 55)
    print(f"VALIDATING: {symbol.upper()}")

    if not file_path.exists():
        print("ERROR: File not found")
        return None

    df = pd.read_csv(file_path)

    # Check required columns
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        print("Missing columns:", missing_columns)
        return None

    # Convert data types
    df["date"] = pd.to_datetime(
        df["date"], utc=True, errors="coerce"
    )

    price_columns = ["open", "high", "low", "close"]

    for col in price_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    issues = []

    # Missing values
    missing_values = df[REQUIRED_COLUMNS].isna().sum()

    if missing_values.sum() > 0:
        issues.append("Missing values detected")

    # Duplicate dates
    duplicate_dates = df["date"].duplicated().sum()

    if duplicate_dates > 0:
        issues.append("Duplicate dates detected")

    # Invalid prices
    invalid_prices = (df[price_columns] <= 0).any(axis=1).sum()

    if invalid_prices > 0:
        issues.append("Zero or negative prices detected")

    # OHLC consistency
    valid_rows = df[REQUIRED_COLUMNS].notna().all(axis=1)

    bad_high = (
        df["high"] < df[["open", "close"]].max(axis=1)
    ) & valid_rows

    bad_low = (
        df["low"] > df[["open", "close"]].min(axis=1)
    ) & valid_rows

    bad_range = (df["high"] < df["low"]) & valid_rows

    invalid_ohlc = (
        bad_high | bad_low | bad_range
    ).sum()

    if invalid_ohlc > 0:
        issues.append("Invalid OHLC relationships detected")

    # Report
    print("Records:", len(df))
    print("Date range:", df["date"].min(), "to", df["date"].max())
    print("Duplicate dates:", duplicate_dates)
    print("Missing values:", missing_values.sum())
    print("Invalid prices:", invalid_prices)
    print("Invalid OHLC rows:", invalid_ohlc)

    if issues:
        print("\nRESULT: REVIEW REQUIRED")
        for issue in issues:
            print("-", issue)
    else:
        print("\nRESULT: PASSED BASIC CHECKS")

    return df


def main():

    datasets = {}

    for symbol in SYMBOLS:
        df = validate_file(symbol)

        if df is not None:
            datasets[symbol] = df

    print("\n" + "=" * 55)
    print("CROSS-INSTRUMENT DATE VALIDATION")

    if len(datasets) != len(SYMBOLS):
        print("Cannot compare dates: one or more datasets are unavailable.")
        return

    date_sets = {
        name: set(df["date"].dropna())
        for name, df in datasets.items()
    }

    common_dates = set.intersection(*date_sets.values())
    all_dates = set.union(*date_sets.values())

    print("Total unique dates across instruments:", len(all_dates))
    print("Dates common to all four instruments:", len(common_dates))
    print("Dates not shared by every instrument:", len(all_dates - common_dates))

    print("\nVALIDATION FINISHED")


if __name__ == "__main__":
    main()
