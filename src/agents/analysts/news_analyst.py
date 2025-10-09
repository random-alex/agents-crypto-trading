import logfire
from pydantic_ai import Agent
from pydantic_ai.builtin_tools import WebSearchTool, MemoryTool, UrlContextTool
from src.prompts.analysts import SYSTEM_PROMPT_NEWS_ANALYST
from src.config import Config

logfire.configure()
logfire.instrument_pydantic_ai()
logfire.instrument_httpx(capture_all=True)


agent = Agent(
    model=Config.MODEL_VERSION_NEWS_AGENT,
    instructions=SYSTEM_PROMPT_NEWS_ANALYST,
    builtin_tools=[WebSearchTool()],
)

if __name__ == "__main__":
    res = agent.run_sync("Give me latest news about Bitcoin")
    print(res)
