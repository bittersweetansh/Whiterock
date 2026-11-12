
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INDEX_FILE = PROJECT_ROOT / "data" / "processed" / "whiterock_index.csv"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
REPORT_DIR = PROJECT_ROOT / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

METALS = ["aluminium", "copper", "nickel", "lead"]


def plot_index():

    df = pd.read_csv(INDEX_FILE)
    df["date"] = pd.to_datetime(df["date"], utc=True)

    # Chart 1: Whiterock index
    plt.figure(figsize=(12, 6))

    plt.plot(
        df["date"],
        df["whiterock_index"],
        label="Whiterock Index"
    )

    plt.axhline(
        y=1000,
        linestyle="--",
        label="Base value (1000)"
    )

    plt.title("Whiterock Four-Metal Research Index")
    plt.xlabel("Date")
    plt.ylabel("Index Value")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        REPORT_DIR / "whiterock_index.png",
        dpi=300
    )

    plt.show()

    # Chart 2: Normalised constituent performance
    plt.figure(figsize=(12, 6))

    for metal in METALS:

        prices = pd.read_csv(
            RAW_DIR / f"{metal}.csv"
        )

        prices["date"] = pd.to_datetime(
            prices["date"], utc=True
        )

        prices = prices.sort_values("date")

        normalised = (
            prices["close"] / prices["close"].iloc[0]
        ) * 100

        plt.plot(
            prices["date"],
            normalised,
            label=metal.title()
        )

    plt.title("Normalised Performance of Constituents")
    plt.xlabel("Date")
    plt.ylabel("Price Index (Base = 100)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        REPORT_DIR / "constituent_performance.png",
        dpi=300
    )

    plt.show()

    print("Charts saved in:", REPORT_DIR)


if __name__ == "__main__":
    plot_index()
