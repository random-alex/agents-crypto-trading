import logfire
from pydantic_ai import Agent
from src.prompts.analysts import SYSTEM_PROMPT_TECHNICAL_ANALYST
from config import Config


logfire.configure(service_name="News agent")
logfire.instrument_pydantic_ai()

agent = Agent(
    model=Config.MODEL_VERSION_TECHANAL_AGENT,
    instructions=SYSTEM_PROMPT_TECHNICAL_ANALYST,
)

if __name__ == "__main__":
    SYMBOL = "Bitcoin"
    user_prompt = (
        f"Make a news sentiment search for {SYMBOL}",
        "Keep the analysis short and coinces. Your analysis will be used by trader later.",
    )
    res = agent.run_sync(user_prompt)
    print(res.output)
