import logfire
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModelSettings
from src.agents.analysts.prompts import SYSTEM_PROMPT_TECHNICAL_ANALYST
from src.config import Config
from pathlib import Path
from src.agents.analysts.context.tech import get_ta_context
from datetime import datetime, timedelta, timezone
from src.agents.analysts.models import TechOutput
from src.agents.utils.general import save_analysis

logfire.configure(service_name="Tech agent")
logfire.instrument_pydantic_ai()
settings = AnthropicModelSettings(
    anthropic_thinking={"type": "enabled", "budget_tokens": 1024},
)

agent = Agent(
    model=Config.MODEL_VERSION_TECHANAL_AGENT,
    instructions=SYSTEM_PROMPT_TECHNICAL_ANALYST,
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
    user_message = f"Make a technicall analysis for {symbol}. "
    context = get_ta_context(user_message)

    res = agent.run_sync(context)

    save_analysis(
        run_id="test",
        context=context,
        analysis=res.output.to_readable_string(),
        agent_type="tech",
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
