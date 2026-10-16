import yfinance as yf
import pandas as pd

""" 
Its responsibility is to:
1. Send a request to your chosen financial-data API.
2. Check whether the request succeeded.
3. Parse the response.
4. Return raw data to the next step.
"""


def fetch_prices(symbols: list[str], period, interval) -> pd.DataFrame:

    data = []
    for symbol in symbols:
        finance_data = yf.Ticker(symbol).history(
            period=period,
            interval=interval,
        )

        finance_data = finance_data.reset_index()

        finance_data["symbol"] = symbol
        data.append(finance_data)

    if not data:
        print("No market data returned")
        return pd.DataFrame()

    return pd.concat(data, ignore_index=True)
