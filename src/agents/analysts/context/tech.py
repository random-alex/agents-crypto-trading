import pandas as pd
import mplfinance as mpf
from ta import trend, momentum, volatility, volume
from io import BytesIO
from pydantic_ai import BinaryContent
from matplotlib.lines import Line2D

from src.agents.utils.exchange_utils import get_coin_prices
from src.config import Config

CONFIG = [
    {"sampling_freq": 15, "days_delay": 1, "type": "high_detail"},
    {"sampling_freq": 60, "days_delay": 7, "type": "mid_detail"},
    {"sampling_freq": "D", "days_delay": 120, "type": "low_detail"},
]


def plot_high_detail_chart(
    df: pd.DataFrame,
    symbol: str = Config.COIN,
    timeinterval: str = Config.SAMPLING_FREQ,
    reference_values: dict | None = None,
    save_path: str | None = None,
    return_bytes: bool = True,
):
    """
    Plot most detailed timeframe chart with all indicators using mplfinance.
    """
    df = df.copy()

    # Ensure datetime index
    if "datetime" in df.columns:
        df.set_index("datetime", inplace=True)
    df.index = pd.to_datetime(df.index)

    # Scale stochastic to 0-100 if needed
    if df["stoch_k"].max() <= 1:
        df["stoch_k"] = df["stoch_k"] * 100
        df["stoch_d"] = df["stoch_d"] * 100

    # MACD histogram colors
    macd_hist_colors = [
        "#26A69A" if v >= 0 else "#EF5350" for v in df["macd_histogram"].fillna(0)
    ]

    # Build addplots
    addplots = [
        # EMAs
        mpf.make_addplot(df["ema7"], color="#2196F3", width=1.2),
        mpf.make_addplot(df["ema14"], color="#FF9800", width=1.2),
        # Bollinger Bands
        mpf.make_addplot(df["bb_upper"], color="#78909C", width=0.8, linestyle="--"),
        mpf.make_addplot(df["bb_middle"], color="#78909C", width=0.8),
        mpf.make_addplot(df["bb_lower"], color="#78909C", width=0.8, linestyle="--"),
        # VWAP
        mpf.make_addplot(df["vwap"], color="#9C27B0", width=1.2, linestyle="--"),
        # RSI (panel 2)
        mpf.make_addplot(
            df["rsi14"], panel=2, color="#E91E63", width=1.2, ylabel="RSI"
        ),
        # MACD (panel 3)
        mpf.make_addplot(
            df["macd_line"], panel=3, color="#2196F3", width=1.2, ylabel="MACD"
        ),
        mpf.make_addplot(df["macd_signal"], panel=3, color="#FF9800", width=1.2),
        mpf.make_addplot(
            df["macd_histogram"], panel=3, type="bar", color=macd_hist_colors, width=0.7
        ),
        # Stochastic (panel 4)
        mpf.make_addplot(
            df["stoch_k"],
            panel=4,
            color="#2196F3",
            width=1.2,
            ylabel="Stoch",
            ylim=(0, 100),
        ),
        mpf.make_addplot(
            df["stoch_d"], panel=4, color="#FF9800", width=1.2, ylim=(0, 100)
        ),
    ]

    # Title
    title = f"{symbol} {timeinterval}m Chart"

    # Plot
    fig, axes = mpf.plot(
        df,
        type="candle",
        style="charles",
        addplot=addplots,
        volume=True,
        volume_panel=1,
        panel_ratios=(4, 1.5, 1, 1, 1),
        figsize=(18, 13),
        title=title,
        returnfig=True,
    )

    # RSI reference lines
    axes[4].axhline(70, color="#EF5350", linestyle="--", linewidth=0.7, alpha=0.7)
    axes[4].axhline(50, color="gray", linestyle="-", linewidth=0.5, alpha=0.5)
    axes[4].axhline(30, color="#26A69A", linestyle="--", linewidth=0.7, alpha=0.7)
    axes[4].set_ylim(20, 80)

    # MACD zero line
    axes[6].axhline(0, color="gray", linestyle="-", linewidth=0.5, alpha=0.5)

    # Stochastic reference lines
    axes[8].axhline(80, color="#EF5350", linestyle="--", linewidth=0.7, alpha=0.7)
    axes[8].axhline(50, color="gray", linestyle="-", linewidth=0.5, alpha=0.5)
    axes[8].axhline(20, color="#26A69A", linestyle="--", linewidth=0.7, alpha=0.7)
    axes[8].set_ylim(0, 100)

    # Add pivot points if provided
    if reference_values:
        ax = axes[0]
        current_price = df["close"].iloc[-1]
        price_range = df["high"].max() - df["low"].min()
        threshold = price_range * 1.5

        ax.axhline(reference_values["pivot"], color="black", linewidth=1, alpha=0.8)
        ax.axhline(reference_values["prev_day_high"], color="#00BCD4", linewidth=1)
        ax.axhline(reference_values["prev_day_low"], color="#FF5722", linewidth=1)

        for level in ["r1", "r2", "r3"]:
            if abs(reference_values[level] - current_price) < threshold:
                ax.axhline(
                    reference_values[level],
                    color="#4CAF50",
                    linestyle="--",
                    linewidth=0.7,
                    alpha=0.7,
                )

        for level in ["s1", "s2", "s3"]:
            if abs(reference_values[level] - current_price) < threshold:
                ax.axhline(
                    reference_values[level],
                    color="#F44336",
                    linestyle="--",
                    linewidth=0.7,
                    alpha=0.7,
                )

    # Custom legend with proper colors
    legend_elements = [
        Line2D([0], [0], color="#2196F3", linewidth=1.5, label="EMA7"),
        Line2D([0], [0], color="#FF9800", linewidth=1.5, label="EMA14"),
        Line2D([0], [0], color="#78909C", linewidth=1.5, linestyle="--", label="BB"),
        Line2D([0], [0], color="#9C27B0", linewidth=1.5, linestyle="--", label="VWAP"),
        Line2D([0], [0], color="#00BCD4", linewidth=1.5, label="Prev H"),
        Line2D([0], [0], color="#FF5722", linewidth=1.5, label="Prev L"),
        Line2D([0], [0], color="black", linewidth=1.5, label="Pivot"),
    ]
    axes[0].legend(
        handles=legend_elements, loc="upper left", fontsize=8, framealpha=0.9
    )

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    if return_bytes:
        with BytesIO() as buf:
            fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
            image_bytes = buf.getvalue()
        return image_bytes

    return fig, axes


def calculate_reference_values(df: pd.DataFrame) -> dict:
    """
    Calculate pivot points and previous session H/L/C from 1H candle data.

    Assumes: datetime index in UTC, columns include 'open', 'high', 'low', 'close'
    Session definition: 6 PM ET to 5 PM ET (CME electronic session)
    """
    # Convert to ET and assign session date
    # Adding 6 hours maps 6PM ET -> midnight, so .date gives correct session
    df = df.copy()
    et_index = df.index.tz_localize(  # pyright: ignore[reportAttributeAccessIssue]
        "UTC"
    ).tz_convert("US/Eastern")
    session_dates = (et_index + pd.Timedelta(hours=6)).date

    # Aggregate by session
    sessions = df.groupby(session_dates).agg(
        high=("high", "max"), low=("low", "min"), close=("close", "last")
    )

    # Previous completed session (second to last)
    prev = sessions.iloc[-2]
    h, low, c = prev["high"], prev["low"], prev["close"]

    # Pivot calculations
    p = (h + low + c) / 3

    return {
        "prev_day_high": h,
        "prev_day_low": low,
        "prev_day_close": c,
        "pivot": p,
        "r1": 2 * p - low,
        "r2": p + (h - low),
        "r3": h + 2 * (p - low),
        "s1": 2 * p - h,
        "s2": p - (h - low),
        "s3": low - 2 * (h - p),
    }


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    # Trend indicators
    df["ema7"] = trend.EMAIndicator(df["close"], window=7).ema_indicator()
    df["ema14"] = trend.EMAIndicator(df["close"], window=14).ema_indicator()
    df["ema20"] = trend.EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = trend.EMAIndicator(df["close"], window=50).ema_indicator()

    df["macd_line"] = trend.macd(
        df["close"],
    )
    df["macd_signal"] = trend.macd_signal(
        df["close"],
    )
    df["macd_histogram"] = trend.MACD(
        df["close"],
    ).macd_diff()

    # Momentum indicators
    df["rsi14"] = momentum.RSIIndicator(df["close"], window=14).rsi()
    df["stoch_k"] = momentum.stochrsi_k(df["close"], window=14)
    df["stoch_d"] = momentum.stochrsi_d(df["close"], window=14)

    # Volatility indicators
    df["bb_upper"] = volatility.bollinger_hband(df["close"])
    df["bb_lower"] = volatility.bollinger_lband(df["close"])
    df["bb_middle"] = volatility.bollinger_mavg(df["close"])
    df["atr_14"] = volatility.average_true_range(
        high=df["high"], low=df["low"], close=df["close"]
    )

    # Volume indicators
    df["vwap"] = volume.volume_weighted_average_price(
        high=df["high"], low=df["low"], close=df["close"], volume=df["volume"]
    )
    df["obv"] = volume.on_balance_volume(close=df["close"], volume=df["volume"])

    return df


def plot_mid_details_chart(
    df: pd.DataFrame,
    symbol: str = Config.COIN,
    save_path: str | None = None,
    return_bytes: bool = True,
):
    """
    Plot medium details timeframe chart(most probably 1h) with indicators using mplfinance.
    """
    df = df.copy()

    # Ensure datetime index
    if "date" in df.columns:
        df.set_index("date", inplace=True)
    df.index = pd.to_datetime(df.index)

    # MACD histogram colors
    macd_hist_colors = [
        "#26A69A" if v >= 0 else "#EF5350" for v in df["macd_histogram"].fillna(0)
    ]

    # Build addplots
    addplots = [
        # EMAs
        mpf.make_addplot(df["ema14"], color="#2196F3", width=1.2),
        mpf.make_addplot(df["ema20"], color="#FF9800", width=1.2),
        # Bollinger Bands
        mpf.make_addplot(df["bb_upper"], color="#78909C", width=0.8, linestyle="--"),
        mpf.make_addplot(df["bb_middle"], color="#78909C", width=0.8),
        mpf.make_addplot(df["bb_lower"], color="#78909C", width=0.8, linestyle="--"),
        # RSI (panel 2)
        mpf.make_addplot(
            df["rsi14"], panel=2, color="#E91E63", width=1.2, ylabel="RSI"
        ),
        # MACD (panel 3)
        mpf.make_addplot(
            df["macd_line"], panel=3, color="#2196F3", width=1.2, ylabel="MACD"
        ),
        mpf.make_addplot(df["macd_signal"], panel=3, color="#FF9800", width=1.2),
        mpf.make_addplot(
            df["macd_histogram"], panel=3, type="bar", color=macd_hist_colors, width=0.7
        ),
    ]

    # Title
    title = f"{symbol} 1h Chart"

    # Plot
    fig, axes = mpf.plot(
        df,
        type="candle",
        style="charles",
        addplot=addplots,
        volume=True,
        volume_panel=1,
        panel_ratios=(4, 1.5, 1, 1),
        figsize=(16, 10),
        title=title,
        returnfig=True,
    )

    # RSI reference lines
    axes[4].axhline(70, color="#EF5350", linestyle="--", linewidth=0.7, alpha=0.7)
    axes[4].axhline(50, color="gray", linestyle="-", linewidth=0.5, alpha=0.5)
    axes[4].axhline(30, color="#26A69A", linestyle="--", linewidth=0.7, alpha=0.7)
    axes[4].set_ylim(20, 80)

    # MACD zero line
    axes[6].axhline(0, color="gray", linestyle="-", linewidth=0.5, alpha=0.5)

    # Legend
    legend_elements = [
        Line2D([0], [0], color="#2196F3", linewidth=1.5, label="EMA14"),
        Line2D([0], [0], color="#FF9800", linewidth=1.5, label="EMA20"),
        Line2D([0], [0], color="#78909C", linewidth=1.5, linestyle="--", label="BB"),
    ]
    axes[0].legend(
        handles=legend_elements, loc="upper left", fontsize=8, framealpha=0.9
    )

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    if return_bytes:
        with BytesIO() as buf:
            fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
            image_bytes = buf.getvalue()
        return image_bytes

    return fig, axes


def plot_low_detail_chart(
    df: pd.DataFrame,
    symbol: str = Config.COIN,
    save_path: str | None = None,
    return_bytes: bool = True,
):
    """
    Plot low detail timeframe chart (daily/weekly) with indicators using mplfinance.
    """
    df = df.copy()

    # Ensure datetime index
    if "week_start" in df.columns:
        df.set_index("week_start", inplace=True)
    df.index = pd.to_datetime(df.index)

    # Build addplots
    addplots = [
        # EMAs
        mpf.make_addplot(df["ema14"], color="#2196F3", width=1.2),
        mpf.make_addplot(df["ema20"], color="#FF9800", width=1.2),
        # RSI (panel 2)
        mpf.make_addplot(
            df["rsi14"], panel=2, color="#E91E63", width=1.2, ylabel="RSI"
        ),
    ]

    # Title
    title = f"{symbol} 1d Chart"

    # Plot
    fig, axes = mpf.plot(
        df,
        type="candle",
        style="charles",
        addplot=addplots,
        volume=True,
        volume_panel=1,
        panel_ratios=(4, 1.5, 1),
        figsize=(14, 8),
        title=title,
        returnfig=True,
    )

    # RSI reference lines
    axes[4].axhline(70, color="#EF5350", linestyle="--", linewidth=0.7, alpha=0.7)
    axes[4].axhline(50, color="gray", linestyle="-", linewidth=0.5, alpha=0.5)
    axes[4].axhline(30, color="#26A69A", linestyle="--", linewidth=0.7, alpha=0.7)
    axes[4].set_ylim(20, 80)

    # Legend
    legend_elements = [
        Line2D([0], [0], color="#2196F3", linewidth=1.5, label="EMA20"),
        Line2D([0], [0], color="#FF9800", linewidth=1.5, label="EMA50"),
    ]
    axes[0].legend(
        handles=legend_elements, loc="upper left", fontsize=8, framealpha=0.9
    )

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    if return_bytes:
        with BytesIO() as buf:
            fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
            image_bytes = buf.getvalue()
        return image_bytes

    return fig, axes


def format_reference_values(ref: dict) -> str:
    """Format reference values inline."""
    return (
        f"Reference: Pivot={ref['pivot']:.4f} | "
        f"R1={ref['r1']:.4f} R2={ref['r2']:.4f} R3={ref['r3']:.4f} | "
        f"S1={ref['s1']:.4f} S2={ref['s2']:.4f} S3={ref['s3']:.4f} | "
        f"Prev H={ref['prev_day_high']:.4f} L={ref['prev_day_low']:.4f} C={ref['prev_day_close']:.4f}"
    )


def get_ta_context(text_context: str):
    all_messages = [text_context]

    for config in CONFIG:
        df = get_coin_prices(**config)
        df = calculate_indicators(df)

        if config["type"] == "high_detail":
            reference_values = calculate_reference_values(df=df)
            all_messages.append(format_reference_values(ref=reference_values))
            img_bytes = plot_high_detail_chart(
                df=df,
                reference_values=reference_values,
                # save_path="test_high_det.png",
                return_bytes=True,
            )

        elif config["type"] == "mid_detail":
            img_bytes = plot_mid_details_chart(
                df=df,
                # save_path="test_mid_det.png",
                return_bytes=True,
            )
        elif config["type"] == "low_detail":
            img_bytes = plot_low_detail_chart(
                df=df,
                # save_path="test_low_det.png",
                return_bytes=True,
            )
        else:
            raise ValueError(
                f"No plotting function define for this time: {config['type']}"
            )

        # all_messages.append(df.to_markdown())
        all_messages.append(
            BinaryContent(
                data=img_bytes,  # pyright: ignore[reportArgumentType]
                media_type="image/png",
            )
        )

    return all_messages


if __name__ == "__main__":
    context = get_ta_context(
        "analyze below images and give trading recommendation for a next 2-3 hours."
    )
