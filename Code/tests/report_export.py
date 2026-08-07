import pandas as pd
from datetime import datetime


def save_report(data):

    if len(data) == 0:
        print("No report generated.")
        return


    df = pd.DataFrame(data)

    filename = (
        "BrainTrader_Report_"
        + datetime.now().strftime("%Y-%m-%d")
        + ".csv"
    )

    df.to_csv(filename, index=False)

    print("\nReport saved:", filename)