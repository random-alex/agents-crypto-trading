import logfire
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.builtin_tools import WebSearchTool
from src.agents.analysts.prompts import SYSTEM_PROMPT_NEWS_ANALYST
from src.config import Config


logfire.configure(service_name="News agent")
logfire.instrument_pydantic_ai()

# mcp_alpha_vantage = MCPServerStreamableHTTP(
#     url=f"https://mcp.alphavantage.co/mcp?apikey={Config.ALPHA_VANTAGE_API_KEY}&categories=cryptocurrencies,alpha_intelligence"
# )


mcp_coingecko = MCPServerStdio(
    "npx",
    args=["-y", "@coingecko/coingecko-mcp"],
    env={
        "COINGECKO_PRO_API_KEY": "",
        "COINGECKO_DEMO_API_KEY": Config.COINGECKO_API_KEY,
        "COINGECKO_ENVIRONMENT": "demo",
    },
    timeout=600,
)

mcp_reddit = MCPServerStdio("npx", args=["-y", "reddit-mcp-buddy"])


agent = Agent(
    model=Config.MODEL_VERSION_NEWS_AGENT,
    instructions=SYSTEM_PROMPT_NEWS_ANALYST,
    builtin_tools=[WebSearchTool()],
    toolsets=[mcp_coingecko, mcp_reddit],
)


if __name__ == "__main__":
    SYMBOL = "Bitcoin"
    user_prompt = (
        f"Make a news sentiment search for {SYMBOL}",
        "Keep the analysis short and coinces. Your analysis will be used by trader later.",
    )
    res = agent.run_sync(user_prompt)
    print(res.output)
