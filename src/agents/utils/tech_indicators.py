from typing import Dict, Hashable, Any
import pandas as pd
import pandas_ta as ta
from pydantic_ai import RunContext
from src.agents.analysts.models import AgentsDeps


def get_dataframe(ctx: RunContext[AgentsDeps]) -> pd.DataFrame:
    """Load OHLC candlestick data with columns: open, high, low, close, volume"""
    df = pd.read_csv(ctx.deps.df_candle_path, parse_dates=True, index_col="timestamp")
    return df


# --- MOMENTUM INDICATORS ---


def calculate_rsi(ctx: RunContext[AgentsDeps], length: int = 14) -> dict[str, Hashable]:
    """
    Calculate RSI (Relative Strength Index) momentum oscillator.

    RSI measures speed and magnitude of price changes, oscillating between 0-100.
    Values above 70 indicate overbought, below 30 indicate oversold.

    Args:
        length: Lookback period for calculation. Default 14. Common values: 7, 14, 21

    Returns:
        Structured dictionary containing:
        - statistics: Statistical summary (min, max, mean, std, current_value)
        - raw_values: Complete list of RSI values
    """
    df = get_dataframe(ctx=ctx)
    result = ta.rsi(close=df["close"], length=length).dropna().round(2)
    rsi_values = result.tolist()
    valid_rsi = [v for v in rsi_values if not (isinstance(v, float) and v != v)]
    # Calculate statistics
    current_rsi = valid_rsi[-1]
    statistics = {
        "current": round(current_rsi, 2),
        "min": round(min(valid_rsi), 2),
        "max": round(max(valid_rsi), 2),
        "mean": round(sum(valid_rsi) / len(valid_rsi), 2),
        "std": round(
            (
                sum((x - sum(valid_rsi) / len(valid_rsi)) ** 2 for x in valid_rsi)
                / len(valid_rsi)
            )
            ** 0.5,
            2,
        ),
    }
    result.index = result.index.astype(str)
    output = {"overall_stats": statistics, "raw_values": result.to_dict()}
    return output


def calculate_stochastic(
    ctx: RunContext[AgentsDeps], k: int = 14, d: int = 3, smooth_k: int = 3
) -> Dict[Hashable, Any]:
    """
    Calculate Stochastic Oscillator momentum indicator.

    Compares closing price to price range over time. Values above 80 indicate
    overbought, below 20 indicate oversold.

    Args:
        k: %K period (fast line). Default 14
        d: %D period (slow line). Default 3
        smooth_k: Smoothing period for %K. Default 3

    Returns:
        Dict with STOCHk_{k}_{d}_{smooth_k} and STOCHd_{k}_{d}_{smooth_k} keys containing lists of Stochastic %K and %D values and corresponding datetimes
    """
    df = get_dataframe(ctx=ctx)
    result = (
        ta.stoch(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            k=k,
            d=d,
            smooth_k=smooth_k,
        )
        .dropna()
        .round(2)
    )
    result.index = result.index.astype(str)
    return result[
        [f"STOCHk_{k}_{d}_{smooth_k}", f"STOCHd_{k}_{d}_{smooth_k}"]
    ].to_dict()


# --- TREND INDICATORS ---


def calculate_macd(
    ctx: RunContext[AgentsDeps], fast: int = 12, slow: int = 26, signal: int = 9
) -> Dict[str, dict[Any, Any]]:
    """
    Calculate MACD (Moving Average Convergence Divergence) trend indicator.

    Shows relationship between two EMAs. MACD line crossing above signal line
    is bullish, crossing below is bearish.

    Args:
        fast: Fast EMA period. Default 12
        slow: Slow EMA period. Default 26
        signal: Signal line EMA period. Default 9

    Returns:
        Dict with 'macd', 'signal', and 'histogram' keys containing pairs of values and corresponding datetimes
    """
    df = get_dataframe(ctx=ctx)
    result = (
        ta.macd(close=df["close"], fast=fast, slow=slow, signal=signal)
        .dropna()
        .round(2)
    )
    result.index = result.index.astype(str)
    return {
        "macd": result[f"MACD_{fast}_{slow}_{signal}"].to_dict(),
        "signal": result[f"MACDs_{fast}_{slow}_{signal}"].to_dict(),
        "histogram": result[f"MACDh_{fast}_{slow}_{signal}"].to_dict(),
    }


def calculate_ema(ctx: RunContext[AgentsDeps], length: int = 20) -> dict[Hashable, Any]:
    """
    Calculate EMA (Exponential Moving Average).

    Weighted moving average giving more weight to recent prices.
    Used to identify trend direction and support/resistance levels.

    Args:
        length: EMA period. Default 20. Common values: 9, 20, 50, 200

    Returns:
        Dict with pairs of EMA values and corresponding datetime
    """
    df = get_dataframe(ctx=ctx)
    result = ta.ema(close=df["close"], length=length).dropna().round(2)
    result.index = result.index.astype(str)
    return result.to_dict()


def calculate_supertrend(
    ctx: RunContext[AgentsDeps], length: int = 10, multiplier: float = 3.0
) -> Dict[Hashable, Any]:
    """
    Calculate Supertrend indicator for trend following.

    Shows dynamic support/resistance levels. When price above Supertrend line
    it's bullish, below is bearish. Very popular for trending markets.

    Args:
        length: ATR period. Default 10. Common values: 7, 10, 14
        multiplier: ATR multiplier. Default 3.0. Common values: 2.0-4.0

    Returns:
        Dict with 'trend', 'direction', 'long', and 'short' keys containing corresponding pairs of datetimes and values
    """
    df = get_dataframe(ctx=ctx)
    result = (
        ta.supertrend(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            length=length,
            multiplier=multiplier,
        )
        .dropna()
        .round(2)
    )
    result.index = result.index.astype(str)
    return {
        "trend": result[f"SUPERT_{length}_{multiplier}"].to_dict(),
        "direction": result[f"SUPERTd_{length}_{multiplier}"].to_dict(),
        "long": result[f"SUPERTl_{length}_{multiplier}"].to_dict(),
        "short": result[f"SUPERTs_{length}_{multiplier}"].to_dict(),
    }


# --- VOLATILITY INDICATORS ---


def calculate_bollinger_bands(
    ctx: RunContext[AgentsDeps], length: int = 20
) -> Dict[Hashable, Any]:
    """
    Calculate Bollinger Bands volatility indicator.

    Consists of moving average with upper/lower bands at standard deviations.
    Price near upper band suggests overbought, near lower band suggests oversold.

    Args:
        length: Moving average period. Default 20

    Returns:
        Dict with 'upper', 'middle', 'lower', and 'bandwidth' keys containing corresponding pairs of datetimes and values
    """
    df = get_dataframe(ctx=ctx)
    result = ta.bbands(close=df["close"], length=length).dropna().round(2)
    result.index = result.index.astype(str)

    return {
        "upper": result[f"BBU_{length}_2.0_2.0"].to_dict(),
        "middle": result[f"BBM_{length}_2.0_2.0"].to_dict(),
        "lower": result[f"BBL_{length}_2.0_2.0"].to_dict(),
        "bandwidth": result[f"BBB_{length}_2.0_2.0"].to_dict(),
    }


def calculate_atr(ctx: RunContext[AgentsDeps], length: int = 14) -> dict[Hashable, Any]:
    """
    Calculate ATR (Average True Range) volatility indicator.

    Measures market volatility by decomposing the entire range of price movement.
    Higher ATR indicates higher volatility.

    Args:
        length: ATR period. Default 14

    Returns:
        Dict with ATR values and corresponding datetimes
    """
    df = get_dataframe(ctx=ctx)
    result = (
        ta.atr(high=df["high"], low=df["low"], close=df["close"], length=length)
        .dropna()
        .round(2)
    )
    result.index = result.index.astype(str)

    return result.to_dict()


# --- VOLUME INDICATORS ---


def calculate_obv(
    ctx: RunContext[AgentsDeps],
) -> dict[Any, Hashable]:
    """
    Calculate OBV (On-Balance Volume) momentum indicator.

    Cumulative volume indicator showing buying/selling pressure.
    Rising OBV suggests accumulation, falling OBV suggests distribution.

    Returns:
        Dict of OBV values and datetimes
    """
    df = get_dataframe(ctx=ctx)
    result = ta.obv(close=df["close"], volume=df["volume"]).dropna().round(2)
    result.index = result.index.astype(str)

    return result.to_dict()


def calculate_vwap(
    ctx: RunContext[AgentsDeps],
) -> dict[Hashable, Any]:
    """
    Calculate VWAP (Volume Weighted Average Price).

    Average price weighted by volume. Used to identify value areas and
    institutional trading levels. Price above VWAP is bullish, below is bearish.

    Returns:
        Dict of VWAP values with datetimes
    """
    df = get_dataframe(ctx=ctx)
    result = (
        ta.vwap(high=df["high"], low=df["low"], close=df["close"], volume=df["volume"])
        .dropna()
        .round(2)
    )
    result.index = result.index.astype(str)
    return result.to_dict()


# --- CANDLE PATTERN INDICATORS ---


def calculate_cdl_pattern(
    ctx: RunContext[AgentsDeps],
) -> str:
    """
    Detect candlestick patterns in the price data.

    Analyzes OHLC (Open, High, Low, Close) data to identify common
    candlestick patterns like doji, hammer, engulfing patterns, etc.
    Returns a formatted string describing detected patterns with their
    timestamps and signal direction (bullish- ↑/bearish - ↓).

    Returns:
        Formatted string describing detected candlestick patterns.
        Returns "No candlestick patterns detected." if none found.
    """
    df = get_dataframe(ctx=ctx)
    res = ta.cdl_pattern(
        open_=df["open"], high=df["high"], low=df["low"], close=df["close"]
    )
    res = res.loc[:, (res != 0).any()]
    patterns_df = res[(res != 0).any(axis=1)]
    # If no patterns detected
    if patterns_df.empty:
        return "No candlestick patterns detected in the analyzed period."
    result_lines = ["Candlestick Patterns Detected:\n"]

    for timestamp, row in patterns_df.iterrows():
        patterns_found = []
        for pattern_name, value in row.items():
            if value != 0:
                clean_name = pattern_name.replace("CDL_", "").replace("_", " ").title()  # pyright: ignore[reportAttributeAccessIssue]
                signal = "↑" if value > 0 else "↓"
                patterns_found.append(f"{clean_name} {signal}")

        if patterns_found:
            result_lines.append(f"{timestamp}: {', '.join(patterns_found)}")

    return "\n".join(result_lines)


if __name__ == "__main__":
    df = pd.read_csv("logs/pics/btc_tmp.csv", parse_dates=True, index_col="timestamp")
    result = ta.stoch(
        high=df["high"],
        low=df["low"],
        close=df["close"],
    )

    print(result)
