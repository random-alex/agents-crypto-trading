from dotenv import load_dotenv
from tiingo import TiingoClient
from datetime import datetime, timedelta
import pandas as pd
from config import Config
import mplfinance as mpf

load_dotenv()
tiingo_config = {}

# To reuse the same HTTP Session across API calls (and have better performance), include a session key.
tiingo_config["session"] = True
client = TiingoClient(tiingo_config)


def get_coin_prices(start_date: str | None = None):
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    res = client.get_crypto_price_history(
        tickers=Config.COINS,
        exchanges=Config.EXCHANGES,
        resampleFreq=Config.SAMPLING_FREQ,
        startDate=start_date,
    )
    df_ohlcv = pd.DataFrame(res[0]["priceData"])
    df_ohlcv["date"] = pd.to_datetime(df_ohlcv["date"])
    df_ohlcv.set_index(df_ohlcv["date"], inplace=True)
    return df_ohlcv


def get_plot_and_save_ohlc():
    df = get_coin_prices()
    # Candlestick with volume
    mpf.plot(df, type="candle", volume=True)


if __name__ == "__main__":
    get_plot_and_save_ohlc()
