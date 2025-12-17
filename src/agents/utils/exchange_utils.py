from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import pandas as pd
from src.config import Config
import mplfinance as mpf
import matplotlib.pyplot as plt
from pathlib import Path
from pybit.unified_trading import HTTP

load_dotenv()

bybit_client = HTTP(
    api_key=Config.BYBIT_DEMO_API_KEY,
    api_secret=Config.BYBIT_DEMO_API_SECRET,
    testnet=False,
)


def get_coin_prices(
    start_date: int | None = None,
    end_date: int | None = None,
    sampling_freq: str = Config.SAMPLING_FREQ,
    days_delay: int = 1,
    **kwargs,
):
    if not start_date:
        start_date = int(
            (datetime.now(timezone.utc) - timedelta(days=days_delay)).timestamp() * 1000
        )
    if not end_date:
        end_date = int(datetime.now(timezone.utc).timestamp() * 1000)

    res = bybit_client.get_kline(
        symbol=Config.COIN,
        interval=sampling_freq,
        category=Config.CATEGORY,
        limit=1000,
        start=start_date,
        end=end_date,
    )

    df = pd.DataFrame(
        res["result"]["list"],
        columns=["timestamp", "open", "high", "low", "close", "volume", "turnover"],
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"].astype(int), unit="ms")
    for col in ["open", "high", "low", "close", "volume", "turnover"]:
        df[col] = pd.to_numeric(df[col])
    df = df.sort_values("timestamp")
    df.set_index(df["timestamp"], inplace=True)
    df = df.drop(columns=["timestamp"])
    return df


def get_plot_and_save_ohlc(
    filepath: Path,
    figsize=(16, 14),
    start_date: int | None = None,
    end_date: int | None = None,
    sampling_freq: str = Config.SAMPLING_FREQ,
):
    df = get_coin_prices(
        start_date=start_date, end_date=end_date, sampling_freq=sampling_freq
    )
    df.to_csv(filepath.with_suffix(".csv"))
    # Candlestick with volume
    fig, axes = mpf.plot(
        df,
        type="candle",
        style="charles",
        volume=True,
        figsize=figsize,
        returnfig=True,
        tight_layout=False,
        title=f"Candle plot for {Config.COIN} for {sampling_freq} freq.",
    )
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    return df


if __name__ == "__main__":
    path = Path("logs/pics/btc_tmp.png")
    get_plot_and_save_ohlc(filepath=path)
