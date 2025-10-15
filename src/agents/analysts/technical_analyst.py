import logfire
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.anthropic import AnthropicModelSettings
from src.agents.analysts.prompts import SYSTEM_PROMPT_TECHNICAL_ANALYST
from src.config import Config
from src.agents.utils.tech_indicators import (
    calculate_atr,
    calculate_bollinger_bands,
    calculate_ema,
    calculate_macd,
    calculate_obv,
    calculate_rsi,
    calculate_stochastic,
    calculate_supertrend,
    calculate_vwap,
    calculate_cdl_pattern,
)
from pathlib import Path
from src.agents.utils.exchange_utils import get_plot_and_save_ohlc
from datetime import datetime, timedelta, timezone
from src.agents.analysts.models import TechOutput, AgentsDeps

logfire.configure(service_name="Tech agent")
logfire.instrument_pydantic_ai()
settings = AnthropicModelSettings(
    anthropic_thinking={"type": "enabled", "budget_tokens": 1024},
)

agent = Agent(
    model=Config.MODEL_VERSION_TECHANAL_AGENT,
    instructions=SYSTEM_PROMPT_TECHNICAL_ANALYST,
    tools=[
        calculate_atr,
        calculate_bollinger_bands,
        calculate_ema,
        calculate_macd,
        calculate_obv,
        calculate_rsi,
        calculate_stochastic,
        calculate_supertrend,
        calculate_vwap,
        calculate_cdl_pattern,
    ],
    deps_type=AgentsDeps,
    output_type=TechOutput,
)


def run_tech_analysis(
    symbol: str,
    start_date: int,
    end_date: int,
    filepath: Path = Path("logs/pics/btc_tmp.png"),
    filepath_week: Path = Path("logs/pics/btc_tmp_week.png"),
    num_days_behind: int = 7,
) -> TechOutput:
    get_plot_and_save_ohlc(filepath=filepath, start_date=start_date, end_date=end_date)
    get_plot_and_save_ohlc(
        start_date=start_date - ((1000 * 60) * 60) * 24 * num_days_behind,
        end_date=end_date,
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
    res = agent.run_sync(
        user_prompt, deps=AgentsDeps(df_candle_path=filepath.with_suffix(".csv"))
    )
    return res.output


if __name__ == "__main__":
    SYMBOL = "BTCUSDT"
    start_date = int(
        (datetime.now(timezone.utc) - timedelta(days=1)).timestamp() * 1000
    )
    end_date = int(datetime.now(timezone.utc).timestamp() * 1000)
    res = run_tech_analysis(symbol=SYMBOL, start_date=start_date, end_date=end_date)
    print(res)
