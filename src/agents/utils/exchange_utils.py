from dotenv import load_dotenv
from tiingo import TiingoClient
from datetime import datetime, timedelta
import pandas as pd
from src.config import Config
import mplfinance as mpf
import matplotlib.pyplot as plt
from pathlib import Path

load_dotenv()
tiingo_config = {}

# To reuse the same HTTP Session across API calls (and have better performance), include a session key.
tiingo_config["session"] = True
client = TiingoClient(tiingo_config)


def get_coin_prices(
    start_date: str | None = None,
    end_date: str | None = None,
    sampling_freq: str = Config.SAMPLING_FREQ,
):
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    res = client.get_crypto_price_history(
        tickers=Config.COINS,
        exchanges=Config.EXCHANGES,
        resampleFreq=sampling_freq,
        startDate=start_date,
        endDate=end_date,
    )
    df_ohlcv = pd.DataFrame(res[0]["priceData"])
    df_ohlcv["date"] = pd.to_datetime(df_ohlcv["date"])
    df_ohlcv.set_index(df_ohlcv["date"], inplace=True)
    return df_ohlcv


def get_plot_and_save_ohlc(
    filepath: Path,
    figsize=(16, 14),
    start_date: str | None = None,
    end_date: str | None = None,
    sampling_freq: str = Config.SAMPLING_FREQ,
):
    df = get_coin_prices(
        start_date=start_date, end_date=end_date, sampling_freq=sampling_freq
    )

    # Candlestick with volume
    fig, axes = mpf.plot(
        df,
        type="candle",
        style="charles",
        volume=True,
        figsize=figsize,
        returnfig=True,
        tight_layout=False,
        title=f"Candle plot for {Config.COINS[0]} for {sampling_freq} freq.",
    )
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    return df


if __name__ == "__main__":
    path = Path("logs/pics/btc_tmp.png")
    get_plot_and_save_ohlc(filepath=path)
