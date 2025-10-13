import logfire
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.mcp import MCPServerStdio
from prompts import SYSTEM_PROMPT_TECHNICAL_ANALYST
from src.config import Config


logfire.configure(service_name="Tech agent")
logfire.instrument_pydantic_ai()

mcp_indicators = MCPServerStdio(
    command="node",
    args=["/Users/alex/Projects/crypto-indicators-mcp"],
    env={"EXCHANGE_NAME": "binance"},
)


agent = Agent(
    model=Config.MODEL_VERSION_TECHANAL_AGENT,
    instructions=SYSTEM_PROMPT_TECHNICAL_ANALYST,
    toolsets=[mcp_indicators],
)

if __name__ == "__main__":
    from pathlib import Path
    from src.agents.utils.exchange_utils import get_plot_and_save_ohlc
    from datetime import datetime, timedelta

    SYMBOL = "BTCUSDT"
    filepath = Path("logs/pics/btc_tmp.png")
    filepath_week = Path("logs/pics/btc_tmp_week.png")

    get_plot_and_save_ohlc(filepath=filepath)
    get_plot_and_save_ohlc(
        start_date=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
        filepath=filepath_week,
        sampling_freq="1hour",
    )

    user_prompt = (
        f"Make a technicall analysis for {SYMBOL}. The image is below",
        "Keep the analysis short and coinces. Your analysis will be used by trader later."
        f"Use tools if needed to calculate indicators, timeframe is {Config.SAMPLING_FREQ}",
        BinaryContent(data=filepath.read_bytes(), media_type="image/png"),
        "For better context, check last week of the price movements in a image below",
        BinaryContent(data=filepath_week.read_bytes(), media_type="image/png"),
    )
    res = agent.run_sync(user_prompt)
    print(res.output)
