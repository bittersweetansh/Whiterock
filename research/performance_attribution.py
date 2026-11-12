
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = ROOT / "data" / "processed"

METALS = ["aluminium", "copper", "nickel", "lead"]
WEIGHT = 0.25


def main():

    results = []

    for metal in METALS:

        df = pd.read_csv(RAW_DIR / f"{metal}.csv")

        initial_price = df["close"].iloc[0]
        final_price = df["close"].iloc[-1]

        total_return = (
            final_price / initial_price
        ) - 1

        contribution = WEIGHT * total_return

        results.append({
            "Metal": metal.title(),
            "Initial Price": initial_price,
            "Final Price": final_price,
            "Total Return": total_return,
            "Weight": WEIGHT,
            "Index Contribution": contribution
        })

    attribution = pd.DataFrame(results)

    total_contribution = attribution[
        "Index Contribution"
    ].sum()

    attribution["Contribution (%)"] = (
        attribution["Index Contribution"] * 100
    )

    print("\nWHITEROCK PERFORMANCE ATTRIBUTION")
    print("=" * 65)

    print(
        attribution[
            ["Metal", "Total Return", "Weight", "Contribution (%)"]
        ].to_string(
            index=False,
            formatters={
                "Total Return": "{:.2%}".format,
                "Weight": "{:.0%}".format,
                "Contribution (%)": "{:.2f}".format
            }
        )
    )

    print("\nTotal index return:", f"{total_contribution:.2%}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    attribution.to_csv(
        OUTPUT_DIR / "performance_attribution.csv",
        index=False
    )

    print("\nSaved performance attribution.")


if __name__ == "__main__":
    main()
