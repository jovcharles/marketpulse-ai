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

    data = yf.download(
        tickers=symbols,
        period=period,
        interval=interval,
        auto_adjust=False,
        group_by="ticker",
        progress=False,
        threads=True,
    )
    if data.empty:
        print("No market data returned.")
        return pd.DataFrame()

    return data
