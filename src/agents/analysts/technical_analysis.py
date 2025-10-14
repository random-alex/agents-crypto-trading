import logfire
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.mcp import MCPServerStdio
from prompts import SYSTEM_PROMPT_TECHNICAL_ANALYST
from src.config import Config
from pydantic import BaseModel
from typing import Literal
from src.agents.utils.tech_indicators import (
    calculate_adx,
    calculate_atr,
    calculate_bollinger_bands,
    calculate_cci,
    calculate_cmf,
    calculate_donchian_channel,
    calculate_ema,
    calculate_ichimoku,
    calculate_keltner_channel,
    calculate_macd,
    calculate_mfi,
    calculate_obv,
    calculate_psar,
    calculate_roc,
    calculate_rsi,
    calculate_sma,
    calculate_stoch_rsi,
    calculate_stochastic,
    calculate_supertrend,
    calculate_vortex,
    calculate_vwap,
    calculate_williams_r,
)
from pathlib import Path
from src.agents.utils.exchange_utils import get_plot_and_save_ohlc
from datetime import datetime, timedelta, timezone


logfire.configure(service_name="Tech agent")
logfire.instrument_pydantic_ai()

mcp_indicators = MCPServerStdio(
    command="node",
    args=["/Users/alex/Projects/crypto-indicators-mcp"],
    env={"EXCHANGE_NAME": "binance"},
)


class TechOutput(BaseModel):
    decision: Literal["LONG", "SHORT", "NO_TRADE"]
    confidence: float
    entry: float
    stop_loss: float
    take_profit: list[float]
    risk_reward_ratio: str
    timeframe_alignment: bool
    key_signals: list[str]


agent = Agent(
    model=Config.MODEL_VERSION_TECHANAL_AGENT,
    instructions=SYSTEM_PROMPT_TECHNICAL_ANALYST,
    tools=[
        calculate_adx,
        calculate_atr,
        calculate_bollinger_bands,
        calculate_cci,
        calculate_cmf,
        calculate_donchian_channel,
        calculate_ema,
        calculate_ichimoku,
        calculate_keltner_channel,
        calculate_macd,
        calculate_mfi,
        calculate_obv,
        calculate_psar,
        calculate_roc,
        calculate_rsi,
        calculate_sma,
        calculate_stoch_rsi,
        calculate_stochastic,
        calculate_supertrend,
        calculate_vortex,
        calculate_vwap,
        calculate_williams_r,
    ],
    output_type=TechOutput,
)


def run_tech_analysis(symbol: str) -> TechOutput:
    filepath = Path("logs/pics/btc_tmp.png")
    filepath_week = Path("logs/pics/btc_tmp_week.png")

    get_plot_and_save_ohlc(filepath=filepath)
    get_plot_and_save_ohlc(
        start_date=int(
            (datetime.now(timezone.utc) - timedelta(days=7)).timestamp() * 1000
        ),
        filepath=filepath_week,
        sampling_freq="60",
    )

    user_prompt = (
        f"Make a technicall analysis for {symbol}.",
        "Keep the analysis short and coinces. Your analysis will be used by trader later."
        f"Use tools if needed to calculate indicators, timeframe is {Config.SAMPLING_FREQ}",
        BinaryContent(data=filepath.read_bytes(), media_type="image/png"),
        "For better context, check last 7 days of the price movements in a image below as well.",
        BinaryContent(data=filepath_week.read_bytes(), media_type="image/png"),
    )
    res = agent.run_sync(user_prompt)
    return res.output


if __name__ == "__main__":
    SYMBOL = "BTCUSDT"
    res = run_tech_analysis(symbol=SYMBOL)
    print(res)
