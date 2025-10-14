from typing import Dict, List
import pandas as pd
import pandas_ta as ta


def get_dataframe() -> pd.DataFrame:
    """Load OHLC candlestick data with columns: open, high, low, close, volume"""
    # TODO(@alex): make the path configurable
    df = pd.read_csv("logs/pics/btc_tmp.csv", parse_dates=True, index_col="timestamp")
    return df


# --- MOMENTUM INDICATORS ---


def calculate_rsi(length: int = 14) -> List[float]:
    """
    Calculate RSI (Relative Strength Index) momentum oscillator.

    RSI measures speed and magnitude of price changes, oscillating between 0-100.
    Values above 70 indicate overbought, below 30 indicate oversold.

    Args:
        length: Lookback period for calculation. Default 14. Common values: 7, 14, 21

    Returns:
        List of RSI values
    """
    df = get_dataframe()
    result = ta.rsi(close=df["close"], length=length)
    return result.tolist()


def calculate_williams_r(length: int = 14) -> List[float]:
    """
    Calculate Williams %R momentum indicator.

    Measures overbought/oversold levels. Values above -20 indicate overbought,
    below -80 indicate oversold. Similar to Stochastic but more sensitive.

    Args:
        length: Lookback period. Default 14. Common values: 14, 21

    Returns:
        List of Williams %R values (range: -100 to 0)
    """
    df = get_dataframe()
    result = ta.willr(high=df["high"], low=df["low"], close=df["close"], length=length)
    return result.tolist()


def calculate_cci(length: int = 20) -> List[float]:
    """
    Calculate CCI (Commodity Channel Index) momentum oscillator.

    Measures deviation from average price. Values above +100 indicate overbought,
    below -100 indicate oversold. Good for identifying cyclical trends.

    Args:
        length: Lookback period. Default 20

    Returns:
        List of CCI values
    """
    df = get_dataframe()
    result = ta.cci(high=df["high"], low=df["low"], close=df["close"], length=length)
    return result.tolist()


def calculate_roc(length: int = 12) -> List[float]:
    """
    Calculate ROC (Rate of Change) momentum indicator.

    Measures percentage price change over time. Positive values indicate upward
    momentum, negative values indicate downward momentum.

    Args:
        length: Lookback period. Default 12. Common values: 9, 12, 25

    Returns:
        List of ROC percentage values
    """
    df = get_dataframe()
    result = ta.roc(close=df["close"], length=length)
    return result.tolist()


def calculate_mfi(length: int = 14) -> List[float]:
    """
    Calculate MFI (Money Flow Index) volume-weighted momentum indicator.

    RSI that incorporates volume. Values above 80 indicate overbought,
    below 20 indicate oversold. Better than RSI for volume-driven markets.

    Args:
        length: Lookback period. Default 14

    Returns:
        List of MFI values (range: 0-100)
    """
    df = get_dataframe()
    result = ta.mfi(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        volume=df["volume"],
        length=length,
    )
    return result.tolist()


def calculate_stoch_rsi(
    length: int = 14, rsi_length: int = 14, k: int = 3, d: int = 3
) -> Dict[str, List[float]]:
    """
    Calculate Stochastic RSI oscillator.

    Applies Stochastic formula to RSI. More sensitive than regular Stochastic.
    Values above 0.8 indicate overbought, below 0.2 indicate oversold.

    Args:
        length: Stochastic period. Default 14
        rsi_length: RSI period. Default 14
        k: %K smoothing period. Default 3
        d: %D smoothing period. Default 3

    Returns:
        Dict with 'k' and 'd' keys containing lists of StochRSI %K and %D values
    """
    df = get_dataframe()
    result = ta.stochrsi(
        close=df["close"], length=length, rsi_length=rsi_length, k=k, d=d
    )

    # Convert DataFrame to dict of lists
    return {
        "k": result[f"STOCHRSIk_{rsi_length}_{length}_{k}_{d}"].tolist(),
        "d": result[f"STOCHRSId_{rsi_length}_{length}_{k}_{d}"].tolist(),
    }


def calculate_stochastic(
    k: int = 14, d: int = 3, smooth_k: int = 3
) -> Dict[str, List[float]]:
    """
    Calculate Stochastic Oscillator momentum indicator.

    Compares closing price to price range over time. Values above 80 indicate
    overbought, below 20 indicate oversold.

    Args:
        k: %K period (fast line). Default 14
        d: %D period (slow line). Default 3
        smooth_k: Smoothing period for %K. Default 3

    Returns:
        Dict with 'k' and 'd' keys containing lists of Stochastic %K and %D values
    """
    df = get_dataframe()
    result = ta.stoch(
        high=df["high"], low=df["low"], close=df["close"], k=k, d=d, smooth_k=smooth_k
    )

    return {
        "k": result[f"STOCHk_{k}_{d}_{smooth_k}"].tolist(),
        "d": result[f"STOCHd_{k}_{d}_{smooth_k}"].tolist(),
    }


# --- TREND INDICATORS ---


def calculate_macd(
    fast: int = 12, slow: int = 26, signal: int = 9
) -> Dict[str, List[float]]:
    """
    Calculate MACD (Moving Average Convergence Divergence) trend indicator.

    Shows relationship between two EMAs. MACD line crossing above signal line
    is bullish, crossing below is bearish.

    Args:
        fast: Fast EMA period. Default 12
        slow: Slow EMA period. Default 26
        signal: Signal line EMA period. Default 9

    Returns:
        Dict with 'macd', 'signal', and 'histogram' keys containing lists of values
    """
    df = get_dataframe()
    result = ta.macd(close=df["close"], fast=fast, slow=slow, signal=signal)

    return {
        "macd": result[f"MACD_{fast}_{slow}_{signal}"].tolist(),
        "signal": result[f"MACDs_{fast}_{slow}_{signal}"].tolist(),
        "histogram": result[f"MACDh_{fast}_{slow}_{signal}"].tolist(),
    }


def calculate_ema(length: int = 20) -> List[float]:
    """
    Calculate EMA (Exponential Moving Average).

    Weighted moving average giving more weight to recent prices.
    Used to identify trend direction and support/resistance levels.

    Args:
        length: EMA period. Default 20. Common values: 9, 20, 50, 200

    Returns:
        List of EMA values
    """
    df = get_dataframe()
    result = ta.ema(close=df["close"], length=length)
    return result.tolist()


def calculate_sma(length: int = 20) -> List[float]:
    """
    Calculate SMA (Simple Moving Average).

    Arithmetic mean of prices over specified period.
    Used to smooth price data and identify trend direction.

    Args:
        length: SMA period. Default 20. Common values: 10, 20, 50, 100, 200

    Returns:
        List of SMA values
    """
    df = get_dataframe()
    result = ta.sma(close=df["close"], length=length)
    return result.tolist()


def calculate_supertrend(
    length: int = 10, multiplier: float = 3.0
) -> Dict[str, List[float]]:
    """
    Calculate Supertrend indicator for trend following.

    Shows dynamic support/resistance levels. When price above Supertrend line
    it's bullish, below is bearish. Very popular for trending markets.

    Args:
        length: ATR period. Default 10. Common values: 7, 10, 14
        multiplier: ATR multiplier. Default 3.0. Common values: 2.0-4.0

    Returns:
        Dict with 'trend', 'direction', 'long', and 'short' keys
    """
    df = get_dataframe()
    result = ta.supertrend(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        length=length,
        multiplier=multiplier,
    )

    return {
        "trend": result[f"SUPERT_{length}_{multiplier}"].tolist(),
        "direction": result[f"SUPERTd_{length}_{multiplier}"].tolist(),
        "long": result[f"SUPERTl_{length}_{multiplier}"].tolist(),
        "short": result[f"SUPERTs_{length}_{multiplier}"].tolist(),
    }


def calculate_psar(af: float = 0.02, max_af: float = 0.2) -> Dict[str, List[float]]:
    """
    Calculate Parabolic SAR (Stop and Reverse) trend indicator.

    Provides entry/exit points. Dots below price suggest uptrend (buy),
    dots above price suggest downtrend (sell).

    Args:
        af: Acceleration factor. Default 0.02
        max_af: Maximum acceleration factor. Default 0.2

    Returns:
        Dict with 'psar', 'long', 'short', and 'af' (acceleration factor) keys
    """
    df = get_dataframe()
    result = ta.psar(
        high=df["high"], low=df["low"], close=df["close"], af0=af, af=af, max_af=max_af
    )

    return {
        "psar": result[f"PSARl_{af}_{max_af}"]
        .fillna(result[f"PSARs_{af}_{max_af}"])
        .tolist(),
        "long": result[f"PSARl_{af}_{max_af}"].tolist(),
        "short": result[f"PSARs_{af}_{max_af}"].tolist(),
        "af": result[f"PSARaf_{af}_{max_af}"].tolist(),
    }


def calculate_ichimoku(
    tenkan: int = 9, kijun: int = 26, senkou: int = 52
) -> Dict[str, List[float]]:
    """
    Calculate Ichimoku Cloud comprehensive trend indicator.

    Provides support/resistance, trend direction, and momentum. Price above
    cloud is bullish, below cloud is bearish. Cloud color indicates trend.

    Args:
        tenkan: Conversion line period. Default 9
        kijun: Base line period. Default 26
        senkou: Leading span B period. Default 52

    Returns:
        Dict with conversion line, base line, leading spans A/B, and lagging span
    """
    df = get_dataframe()
    result = ta.ichimoku(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        tenkan=tenkan,
        kijun=kijun,
        senkou=senkou,
    )

    return {
        "conversion_line": result[0][f"ITS_{tenkan}"].tolist(),
        "base_line": result[0][f"IKS_{kijun}"].tolist(),
        "leading_span_a": result[0][f"ISA_{tenkan}"].tolist(),
        "leading_span_b": result[0][f"ISB_{kijun}"].tolist(),
        "lagging_span": result[0][f"ICS_{kijun}"].tolist(),
    }


def calculate_adx(length: int = 14) -> Dict[str, List[float]]:
    """
    Calculate ADX (Average Directional Index) trend strength indicator.

    Measures strength of trend regardless of direction. Values above 25 indicate
    strong trend, below 20 indicate weak trend or ranging market.

    Args:
        length: ADX period. Default 14

    Returns:
        Dict with 'adx', 'dmp' (+DI), and 'dmn' (-DI) keys
    """
    df = get_dataframe()
    result = ta.adx(high=df["high"], low=df["low"], close=df["close"], length=length)

    return {
        "adx": result[f"ADX_{length}"].tolist(),
        "dmp": result[f"DMP_{length}"].tolist(),  # +DI
        "dmn": result[f"DMN_{length}"].tolist(),  # -DI
    }


def calculate_vortex(length: int = 14) -> Dict[str, List[float]]:
    """
    Calculate Vortex Indicator for trend direction and strength.

    Returns +VI and -VI lines. When +VI crosses above -VI it's bullish,
    when -VI crosses above +VI it's bearish. Good trend confirmation.

    Args:
        length: Lookback period. Default 14. Common values: 14, 21

    Returns:
        Dict with 'positive' (+VI) and 'negative' (-VI) keys
    """
    df = get_dataframe()
    result = ta.vortex(high=df["high"], low=df["low"], close=df["close"], length=length)

    return {
        "positive": result[f"VTXP_{length}"].tolist(),
        "negative": result[f"VTXM_{length}"].tolist(),
    }


# --- VOLATILITY INDICATORS ---


def calculate_bollinger_bands(length: int = 20) -> Dict[str, List[float]]:
    """
    Calculate Bollinger Bands volatility indicator.

    Consists of moving average with upper/lower bands at standard deviations.
    Price near upper band suggests overbought, near lower band suggests oversold.

    Args:
        length: Moving average period. Default 20

    Returns:
        Dict with 'upper', 'middle', 'lower', and 'bandwidth' keys
    """
    df = get_dataframe()
    result = ta.bbands(close=df["close"], length=length)

    return {
        "upper": result[f"BBU_{length}_2.0_2.0"].tolist(),
        "middle": result[f"BBM_{length}_2.0_2.0"].tolist(),
        "lower": result[f"BBL_{length}_2.0_2.0"].tolist(),
        "bandwidth": result[f"BBB_{length}_2.0_2.0"].tolist(),
    }


def calculate_atr(length: int = 14) -> List[float]:
    """
    Calculate ATR (Average True Range) volatility indicator.

    Measures market volatility by decomposing the entire range of price movement.
    Higher ATR indicates higher volatility.

    Args:
        length: ATR period. Default 14

    Returns:
        List of ATR values
    """
    df = get_dataframe()
    result = ta.atr(high=df["high"], low=df["low"], close=df["close"], length=length)
    return result.tolist()


def calculate_keltner_channel(
    length: int = 20, multiplier: float = 2.0
) -> Dict[str, List[float]]:
    """
    Calculate Keltner Channels volatility indicator.

    Similar to Bollinger Bands but uses ATR. Returns upper, middle (EMA),
    and lower channels. Good for breakout trading.

    Args:
        length: EMA period. Default 20
        multiplier: ATR multiplier. Default 2.0. Common values: 1.5-2.5

    Returns:
        Dict with 'upper', 'middle', and 'lower' channel keys
    """
    df = get_dataframe()
    result = ta.kc(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        length=length,
        scalar=multiplier,
    )

    return {
        "upper": result[f"KCUe_{length}_{multiplier}"].tolist(),
        "middle": result[f"KCBe_{length}_{multiplier}"].tolist(),
        "lower": result[f"KCLe_{length}_{multiplier}"].tolist(),
    }


def calculate_donchian_channel(length: int = 20) -> Dict[str, List[float]]:
    """
    Calculate Donchian Channels volatility/breakout indicator.

    Shows highest high and lowest low over period. Breakouts above upper
    channel are bullish, below lower channel are bearish.

    Args:
        length: Lookback period. Default 20. Common values: 20, 50, 100

    Returns:
        Dict with 'upper', 'middle', and 'lower' channel keys
    """
    df = get_dataframe()
    result = ta.donchian(
        high=df["high"], low=df["low"], lower_length=length, upper_length=length
    )

    return {
        "upper": result[f"DCU_{length}_{length}"].tolist(),
        "middle": result[f"DCM_{length}_{length}"].tolist(),
        "lower": result[f"DCL_{length}_{length}"].tolist(),
    }


# --- VOLUME INDICATORS ---


def calculate_obv() -> List[float]:
    """
    Calculate OBV (On-Balance Volume) momentum indicator.

    Cumulative volume indicator showing buying/selling pressure.
    Rising OBV suggests accumulation, falling OBV suggests distribution.

    Returns:
        List of OBV values
    """
    df = get_dataframe()
    result = ta.obv(close=df["close"], volume=df["volume"])
    return result.tolist()


def calculate_vwap() -> List[float]:
    """
    Calculate VWAP (Volume Weighted Average Price).

    Average price weighted by volume. Used to identify value areas and
    institutional trading levels. Price above VWAP is bullish, below is bearish.

    Returns:
        List of VWAP values
    """
    df = get_dataframe()
    result = ta.vwap(
        high=df["high"], low=df["low"], close=df["close"], volume=df["volume"]
    )
    return result.tolist()


def calculate_cmf(length: int = 20) -> List[float]:
    """
    Calculate Chaikin Money Flow volume indicator.

    Measures buying/selling pressure. Values above 0 indicate accumulation,
    below 0 indicate distribution. Strong signals above +0.25 or below -0.25.

    Args:
        length: Lookback period. Default 20

    Returns:
        List of CMF values (range: -1 to 1)
    """
    df = get_dataframe()
    result = ta.cmf(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        volume=df["volume"],
        length=length,
    )
    return result.tolist()
